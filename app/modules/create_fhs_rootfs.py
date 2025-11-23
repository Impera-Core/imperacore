# modules/create_fhs_rootfs.py
import os
from pathlib import Path
from utils.logger import create, success, debug, info

class FHSRootFSBuilder:
    def __init__(self, rootfs_dir: str | Path, fhs_layout):
        self.rootfs_dir = Path(rootfs_dir)
        self.layout = fhs_layout

    def create_directories(self):
        create("[*] Erstelle Verzeichnisse...")
        for d in self.layout.directories():
            path = self.rootfs_dir / d.lstrip("/")
            path.mkdir(parents=True, exist_ok=True)
            debug(f"Verzeichnis erstellt: {path}")

        # Speziell für Pacman DB
        pacman_sync = self.rootfs_dir / "var/lib/pacman/sync"
        pacman_sync.mkdir(parents=True, exist_ok=True)
        info(f"Pacman DB-Verzeichnis sichergestellt: {pacman_sync}")

    def create_files(self):
        create("[*] Erstelle Dateien...")
        for f in self.layout.files():
            target = self.rootfs_dir / f["path"].lstrip("/")

            target.parent.mkdir(parents=True, exist_ok=True)

            if "content" in f:
                target.write_text(f["content"])
                debug(f"Datei erstellt mit Inhalt: {target}")

            elif "source" in f:
                src = Path(f["source"])
                target.write_text(src.read_text())
                debug(f"Datei aus Quelle kopiert: {target} <- {src}")

            else:
                target.touch()
                debug(f"Leere Datei erstellt: {target}")

    def create_symlinks(self):
        create("[*] Erstelle Symlinks...")
        for s in self.layout.symlinks():
            link_path = self.rootfs_dir / s["link"].lstrip("/")
            target = s["target"]

            if link_path.exists():
                link_path.unlink()

            link_path.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(target, link_path)
            debug(f"Symlink erstellt: {link_path} -> {target}")

    def build(self):
        self.create_directories()
        self.create_files()
        self.create_symlinks()
        success("[✓] FHS RootFS erfolgreich aufgebaut!")
