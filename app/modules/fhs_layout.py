# modules/fhs_layout.py
import yaml
from pathlib import Path

class FHSLayout:
    def __init__(self, yaml_file):
        self.yaml_file = Path(yaml_file)
        self.layout = {}

    def load(self):
        if not self.yaml_file.exists():
            raise FileNotFoundError(f"FHS YAML nicht gefunden: {self.yaml_file}")

        data = yaml.safe_load(self.yaml_file.read_text())

        if "fhs" not in data:
            raise ValueError("FHS-Layout fehlt in YAML unter 'fhs'")

        self.layout = data["fhs"]
        return self.layout

    def directories(self):
        return self.layout.get("directories", [])

    def files(self):
        return self.layout.get("files", [])

    def symlinks(self):
        return self.layout.get("symlinks", [])
