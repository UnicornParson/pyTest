import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class OllamaConfig:
    use_ollama: bool = False
    host: str = "127.0.0.1"
    port: int = 11435
    main_model: str = "llama3.2"
    embed_model: str = "nomic-embed-text"

@dataclass
class ProjectStorageConfig:
    path: str

@dataclass
class AppConfig:
    ollama: OllamaConfig
    project_storage: ProjectStorageConfig

class ConfigManager:

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[AppConfig] = None
        self._required_sections = ['ollama', 'project_storage']
    
    def load(self) -> None:

        try:
            with self.config_path.open('r') as f:
                raw_data = yaml.safe_load(f) or {}
                self._validate(raw_data)
                self.config = AppConfig(
                    ollama=OllamaConfig(**raw_data['ollama']),
                    project_storage=ProjectStorageConfig(**raw_data['project_storage'])
                )
        except FileNotFoundError:
            raise ConfigError(f"Config file {self.config_path} not found")
        except yaml.YAMLError as e:
            raise ConfigError(f"YAML parsing error: {str(e)}")
        except TypeError as e:
            raise ConfigError(f"Invalid config structure: {str(e)}")
    
    def save(self, output_path: Optional[str] = None) -> None:
        if not self.config:
            raise ConfigError("No configuration loaded")

        save_path = Path(output_path) if output_path else self.config_path
        with save_path.open('w') as f:
            yaml.dump(
                self._to_dict(),
                f,
                default_flow_style=False,
                sort_keys=False,
                indent=2
            )
    
    def update_ollama(self, **kwargs) -> None:
        if not self.config:
            raise ConfigError("Config not loaded")
        for key, value in kwargs.items():
            if hasattr(self.config.ollama, key):
                setattr(self.config.ollama, key, value)
            else:
                raise AttributeError(f"OllamaConfig has no attribute '{key}'")
    
    def update_project_storage(self, path: str) -> None:
        if not self.config:
            raise ConfigError("Config not loaded")
        self.config.project_storage.path = path
    
    def _validate(self, raw_data: Dict) -> None:
        missing = [section for section in self._required_sections if section not in raw_data]
        if missing:
            raise ConfigError(f"Missing required sections: {', '.join(missing)}")
        
        ollama_required = ['host', 'port', 'main_model', 'embed_model']
        missing_ollama = [field for field in ollama_required if field not in raw_data['ollama']]
        if missing_ollama:
            raise ConfigError(f"Missing required Ollama fields: {', '.join(missing_ollama)}")
    
    def _to_dict(self) -> Dict:
        return {
            'ollama': asdict(self.config.ollama),
            'project_storage': asdict(self.config.project_storage)
        }
    
    @property
    def ollama_settings(self) -> OllamaConfig:
        if not self.config:
            raise ConfigError("Config not loaded")
        return self.config.ollama
    
    @property
    def storage_settings(self) -> ProjectStorageConfig:
        if not self.config:
            raise ConfigError("Config not loaded")
        return self.config.project_storage

class ConfigError(Exception):
    pass
