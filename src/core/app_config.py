import os
from typing import Any

import yaml


class BaseConfig:
    """Handles loading, parsing, and hierarchical merging of configuration files.

    Dynamically maps configuration files residing outside the src folder.
    """

    def __init__(self, job_name: str, environment: str, config_dir: str = None) -> None:
        self.job_name = job_name
        self.environment = environment

        if config_dir is None:
            # os.path.abspath(__file__) -> /project_root/src/core/config.py
            # 1st dirname -> /project_root/src/core
            # 2nd dirname -> /project_root/src
            # 3rd dirname -> /project_root
            core_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(core_dir)
            project_root = os.path.dirname(src_dir)

            self.config_dir = os.path.join(project_root, "config")
        else:
            self.config_dir = config_dir

        self._config = {}
        self._load_config_pipeline()

    def _load_config_pipeline(self) -> None:
        """Executes the sequential read and deep merge process."""
        # 1. Read global base configuration baseline
        global_path = os.path.join(self.config_dir, "base_config.yaml")
        global_config = self._read_yaml_file(global_path)

        # 2. Read specific environment sub-directory and job configuration file
        job_env_path = os.path.join(self.config_dir, self.environment, f"{self.job_name}.yaml")
        job_config = self._read_yaml_file(job_env_path)

        # 3. Deep merge configurations
        self._config = self._deep_merge_dictionaries(global_config, job_config)

    def get(self, key: str, default: Any = None) -> Any:
        """Safe top-level dictionary access."""
        return self._config.get(key, default)

    def _read_yaml_file(self, file_path: str) -> dict[str, Any]:
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            parsed_content = yaml.safe_load(f)
        return parsed_content if isinstance(parsed_content, dict) else {}

    def _deep_merge_dictionaries(self, base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
        merged = base.copy()
        for key, value in overrides.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge_dictionaries(merged[key], value)
            else:
                merged[key] = value
        return merged