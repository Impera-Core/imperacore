import json
import yaml
from pathlib import Path
from typing import Union, Any
from utils.logger import log, success, info, warning, error, debug

class ConfigLoader:
    """Lädt JSON- und YAML-Konfigurationsdateien mit Logging über module/logger.py"""

    SUPPORTED_EXTENSIONS = ('.json', '.yaml', '.yml')

    @staticmethod
    def load(file_path: Union[str, Path]) -> dict:
        """
        Lädt eine Konfigurationsdatei basierend auf ihrer Endung.

        Args:
            file_path (str | Path): Pfad zur Konfigurationsdatei

        Returns:
            dict: Geladene Konfiguration

        Raises:
            FileNotFoundError: Datei existiert nicht
            ValueError: Dateityp wird nicht unterstützt
            Exception: Parsing Fehler
        """
        path = Path(file_path)
        if not path.exists():
            error(f"Konfigurationsdatei nicht gefunden: {file_path}")
            raise FileNotFoundError(f"Datei existiert nicht: {file_path}")

        if path.suffix.lower() not in ConfigLoader.SUPPORTED_EXTENSIONS:
            error(f"Nicht unterstützter Dateityp: {path.suffix}")
            raise ValueError(f"Nicht unterstützter Dateityp: {path.suffix}")

        try:
            if path.suffix.lower() == '.json':
                return ConfigLoader._load_json(path)
            else:  # .yaml oder .yml
                return ConfigLoader._load_yaml(path)
        except Exception as e:
            error(f"Fehler beim Laden der Konfiguration: {file_path} - {e}")
            raise e

    @staticmethod
    def _load_json(path: Path) -> dict:
        info(f"Lade JSON-Konfiguration: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        success(f"JSON-Konfiguration erfolgreich geladen: {path}")
        return data

    @staticmethod
    def _load_yaml(path: Path) -> dict:
        info(f"Lade YAML-Konfiguration: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        success(f"YAML-Konfiguration erfolgreich geladen: {path}")
        return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        error("Bitte eine Config-Datei als Argument angeben")
        sys.exit(1)

    config_file = sys.argv[1]
    config = ConfigLoader.load(config_file)
    debug(f"Geladene Konfiguration: {config}")
