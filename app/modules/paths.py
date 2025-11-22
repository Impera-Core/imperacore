import shutil

from dataclasses import dataclass
from pathlib import Path

@dataclass
class Paths:
    root: Path

    def __post_init__(self):
        # Stelle sicher, dass die Basisstruktur existiert
        for p in [
            self.work,
            self.download,
            self.cache,
            self.rootfs,
            self.images,
            self.logs,
            self.tmp,
        ]:
            p.mkdir(parents=True, exist_ok=True)

    def clean_rootfs(self):
        shutil.rmtree(self.rootfs, ignore_errors=True)
        self.rootfs.mkdir(parents=True, exist_ok=True)

    @property
    def work(self) -> Path:
        return self.root / "work"

    @property
    def download(self) -> Path:
        return self.work / "download"

    @property
    def cache(self) -> Path:
        return self.work / "cache"

    @property
    def rootfs(self) -> Path:
        return self.work / "rootfs"

    @property
    def images(self) -> Path:
        return self.work / "images"

    @property
    def logs(self) -> Path:
        return self.work / "logs"

    @property
    def tmp(self) -> Path:
        return self.work / "tmp"
