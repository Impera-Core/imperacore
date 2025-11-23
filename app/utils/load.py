import json
import yaml
from pathlib import Path
from typing import Union, Any
# Angenommen, utils.logger ist in Ihrem Environment verfügbar
# from utils.logger import * # Ersetzen Sie die logger-Importe durch Platzhalter, falls utils.logger nicht vorhanden ist:
def error(msg): print(f"ERROR: {msg}")
def loading(msg): print(f"LOADING: {msg}")
def success(msg): print(f"SUCCESS: {msg}")
def debug(msg): print(f"DEBUG: {msg}")


class ConfigLoader:
    """Lädt JSON- und YAML-Konfigurationsdateien mit Logging über module/logger.py"""

    SUPPORTED_EXTENSIONS = ('.json', '.yaml', '.yml')

    @staticmethod
    def load(file_path: Union[str, Path]) -> dict:
        """ Loading some configs """
        
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
        loading(f"Lade JSON-Konfiguration: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        success(f"JSON-Konfiguration erfolgreich geladen: {path}")
        return data

    @staticmethod
    def _load_yaml(path: Path) -> dict:
        loading(f"Lade YAML-Konfiguration: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            # Verwenden Sie safe_load, wie in der Klasse definiert
            data = yaml.safe_load(f) 
        success(f"YAML-Konfiguration erfolgreich geladen: {path}")
        return data


# if __name__ == "__main__":
#     # Laden der Konfiguration (Annahme: default.yaml liegt im selben Verzeichnis)
#     config_file_path = "default.yaml"
    
#     try:
#         config = ConfigLoader.load(config_file_path)
#         debug(f"Gesamte geladene Konfiguration: {config}")

#         # Extrahieren des Pfades
#         # 1. Auf den Schlüssel 'workenvironment' zugreifen
#         work_envs = config.get("workenvironment")
        
#         if work_envs and isinstance(work_envs, list) and len(work_envs) > 0:
#             # 2. Das erste Element der Liste nehmen (index 0)
#             first_env = work_envs[0]
            
#             # 3. Auf den Schlüssel 'paths' zugreifen
#             paths = first_env.get("paths")
            
#             if paths and isinstance(paths, dict):
#                 # 4. Auf den Pfad-Schlüssel 'development_enviroment' zugreifen
#                 dev_path = paths.get("development_enviroment")
                
#                 if dev_path:
#                     success(f"Gefundener Entwicklungspfad: {dev_path}")
#                     # Beispiel für die weitere Verwendung
#                     path_obj = Path(dev_path)
#                     debug(f"Pfad-Objekt erstellt: {path_obj}")
#                 else:
#                     error("Schlüssel 'development_enviroment' nicht gefunden.")
#             else:
#                 error("Schlüssel 'paths' nicht gefunden oder ungültig.")
#         else:
#             error("Schlüssel 'workenvironment' nicht gefunden oder leer.")

#     except Exception as e:
#         error(f"Hauptprogrammfehler: {e}")