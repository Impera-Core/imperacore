# modules/create_fhs_rootfs.py
import os
from pathlib import Path

class FHSRootFSBuilder:
    def __init__(self, rootfs_dir, fhs_layout):
        self.rootfs_dir = Path(rootfs_dir)
        self.layout = fhs_layout

    def create_directories(self):
        for d in self.layout.directories():
            p = self.rootfs_dir / d.lstrip("/")
            p.mkdir(parents=True, exist_ok=True)

    def create_files(self):
        for f in self.layout.files():
            target = self.rootfs_dir / f["path"].lstrip("/")

            if "content" in f:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f["content"])

            elif "source" in f:
                src = Path(f["source"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(src.read_text())

            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()

    def create_symlinks(self):
        for s in self.layout.symlinks():
            link_path = self.rootfs_dir / s["link"].lstrip("/")
            target = s["target"]

            if link_path.exists():
                link_path.unlink()

            link_path.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(target, link_path)

    def build(self):
        print("[*] Erstelle FHS-Verzeichnisstruktur...")
        self.create_directories()

        print("[*] Erstelle Dateien...")
        self.create_files()

        print("[*] Erstelle Symlinks...")
        self.create_symlinks()

        print("[✓] FHS RootFS erfolgreich aufgebaut!")
