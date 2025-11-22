from pathlib import Path
from modules.paths import Paths
from utils.logger import info, debug, warning, error, success

class Workspace:

    def __init__(self, base_path: str | Path):
        self.paths = Paths(Path(base_path).resolve())

    def ensure(self) -> Paths:
        dirs = [
            self.paths.work,
            self.paths.download,
            self.paths.cache,
            self.paths.rootfs,
            self.paths.images,
            self.paths.logs,
            self.paths.tmp,
        ]

        for d in dirs:
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                info(f"[workspace] created: {d}")

        return self.paths
