#!/usr/bin/env python3
import argparse
import importlib
import os
import sys

# ── 1. Setup Project Pathing ──────────────────────────────────────────────────
# Resolve the absolute path to the 'src' directory relative to this script
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Add 'src' to the Python system path so modules like 'core' and 'jobs' resolve cleanly
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Propagate 'src' to PYTHONPATH so Spark executor worker processes can unpickle UDFs
# that reference modules under src/ (e.g. transformers.base, transformers.cleanup)
existing_pythonpath = os.environ.get("PYTHONPATH", default="")
if SRC_DIR not in existing_pythonpath.split(os.pathsep):
    os.environ["PYTHONPATH"] = SRC_DIR + (os.pathsep + existing_pythonpath if existing_pythonpath else "")



# ── 2. Helper Utilities ───────────────────────────────────────────────────────
def get_job_class(job_module_name: str):
    """Dynamically loads the job module and extracts the target Job Class.

    Translates a snake_case job name (e.g., 'example_etl_job') into its corresponding
    PascalCase class name (e.g., 'ExampleETLJob') and imports it dynamically.
    """
    try:
        # Construct the full import path (e.g., 'jobs.example_etl_job')
        module_path = f"jobs.{job_module_name}"
        module = importlib.import_module(module_path)

        # Convert snake_case name to PascalCase class name string
        # e.g., 'example_etl_job' -> ['Example', 'Etl', 'Job'] -> 'ExampleEtlJob'
        # We handle case variations safely by looking up matching attributes
        class_name = "".join(word.capitalize() for word in job_module_name.split("_"))

        # Case insensitive matching to find the exact class name variant in the module
        for attr in dir(module):
            if attr.lower() == class_name.lower():
                return getattr(module, attr)

        raise AttributeError(f"Could not find matching class structure for '{class_name}' inside module.")

    except ModuleNotFoundError as e:
        print(f"Error: The job module '{job_module_name}' could not be found under src/jobs/.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading job class: {e}", file=sys.stderr)
        sys.exit(1)


# ── 3. Main Bootstrapper Execution ───────────────────────────────────────────
def main() -> None:
    # Build robust command line argument rules
    parser = argparse.ArgumentParser(
        description="Spark Framework Distributed ETL Pipeline Orchestration Execution Engine",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--job",
        required=True,
        help="The name of your python file under src/jobs/ without the '.py' extension (e.g. example_etl_job)"
    )
    parser.add_argument(
        "--env",
        required=True,
        choices=["dev", "staging", "prod"],
        help="Target environment runtime context execution platform profile"
    )

    args = parser.parse_args()

    print(f"Executing Bootstrapper Sequence for Task: [{args.job}] targeting Env: [{args.env}]")

    # Fetch the class archetype dynamically from the jobs directory layout
    JobClass = get_job_class(args.job)

    try:
        # Initialize the chosen job instance.
        # This will internally run core.config and construct your custom Spark Session
        job_instance = JobClass(job_name=args.job, environment=args.env)

        # Kick off processing engine
        job_instance.run()
        print(f"Pipeline executed successfully for job: {args.job}")

    except Exception as e:
        # Fallback console catch if logging bootstrap fails early
        print(f"CRITICAL: Application run failure inside engine sequence: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()