import sys
import os
import argparse
from pathlib import Path
from typing import Union, Dict
import shutil

from core.busybox import BusyBoxBuilder

from modules.paths import Paths
from modules.workspace import Workspace
from modules.fhs_layout import FHSLayout
from modules.create_fhs_rootfs import FHSRootFSBuilder
from modules.arch import ARCHES
from modules.install_to_rootfs import PackageInstaller
from manager.paccy import PacmanRootFSInstaller

from utils.load import ConfigLoader
from utils.logger import info, debug, warning, error, success, running


def setup_development_enviroment(config_file_path: Union[str, Path]) -> Union[Dict[str, Path], None]:
    exported_paths: Dict[str, Path] = {}

    try:
        # TODO: ConfigLoader nutzen, hier Mock
        config = {
            "workenvironment": [
                {
                    "paths": {
                        "development_enviroment": "/mnt/nexuzfs/",
                        "work_dir": "/mnt/nexuzfs/work",
                        "build_dir": "/mnt/nexuzfs/build",
                        "rootfs_dir": "/mnt/nexuzfs/work/rootfs",
                        "cache_dir": "/mnt/nexuzfs/work/cache",
                        "download_dir": "/mnt/nexuzfs/work/downloads",
                        "pacman_cache": "/mnt/nexuzfs/work/rootfs/var/cache/pacman",
                        "image_dir": "/mnt/nexuzfs/work/images",
                        "logs_dir": "/mnt/nexuzfs/work/logs",
                        "tmp_dir": "/mnt/nexuzfs/work/tmp"
                    }
                }
            ]
        }

        debug(f"Gesamte geladene Konfiguration: {config}")

        work_envs = config.get("workenvironment")
        if not work_envs or not isinstance(work_envs, list) or len(work_envs) == 0:
            error("Schlüssel 'workenvironment' nicht gefunden oder leer.")
            return None

        paths_dict = work_envs[0].get("paths")
        if not paths_dict or not isinstance(paths_dict, dict):
            error("Schlüssel 'paths' nicht gefunden oder ungültig.")
            return None

        for key, path_str in paths_dict.items():
            if path_str:
                exported_paths[key] = Path(path_str)
                exported_paths[key].mkdir(parents=True, exist_ok=True)  # Verzeichnisse sicherstellen
                success(f"Pfad '{key}' geladen: {path_str}")
            else:
                debug(f"Optionaler Pfad '{key}' fehlt in der Config.")

        return exported_paths

    except Exception as e:
        error(f"Fehler beim Einrichten der Entwicklungsumgebung: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="MetaNexuz RootFS Builder")
    parser.add_argument("--config", type=str, required=False, default="default.yaml")
    parser.add_argument("--fhs", type=str, required=False, default="default_fhs.yaml")
    parser.add_argument("--arch", type=str, default="x86_64", choices=ARCHES.keys())
    args = parser.parse_args()

    config_yaml = Path("configs") / "system" / args.config
    geladene_pfade = setup_development_enviroment(config_yaml)

    if not geladene_pfade:
        error("Keine Pfade geladen – Abbruch!")
        return

    # Pfade extrahieren
    DEV_ENV_DIR = geladene_pfade["development_enviroment"]
    WORK_DIR = geladene_pfade["work_dir"]
    BUILD_DIR = geladene_pfade["build_dir"]
    ROOTFS_DIR = geladene_pfade["rootfs_dir"]
    CACHE_DIR = geladene_pfade["cache_dir"]
    PACMAN_CACHE_DIR = geladene_pfade["pacman_cache"]
    TMP_DIR = geladene_pfade["tmp_dir"]
    IMAGE_DIR = geladene_pfade["image_dir"]
    LOGS_DIR = geladene_pfade["logs_dir"]

    arch_conf = ARCHES[args.arch]

    # Paths & Workspace
    paths = Paths(DEV_ENV_DIR)
    ws = Workspace(paths.root)
    ws.ensure()

    # FHS Layout
    fhs_yaml = Path("configs") / "rootfs" / args.fhs
    if not fhs_yaml.exists():
        error(f"[!] FHS Layout nicht gefunden: {fhs_yaml}")
        return

    layout = FHSLayout(fhs_yaml)
    layout.load()

    # RootFS Pfad vorbereiten
    rootfs_path = paths.rootfs
    if rootfs_path.exists():
        shutil.rmtree(rootfs_path)
    rootfs_path.mkdir(parents=True, exist_ok=True)

    # Pacman Cache sicherstellen
    pacman_cache_path = paths.pacman_cache
    pacman_cache_path.mkdir(parents=True, exist_ok=True)

    # RootFS erstellen
    builder = FHSRootFSBuilder(rootfs_path, layout)
    builder.build()
    success(f"[✓] RootFS erstellt für Architektur {args.arch} in {rootfs_path}")

    busybox_json = Path("configs/busybox/busybox.json")
    bb_builder = BusyBoxBuilder(busybox_json, paths=paths, arch="x86_64")
    bb_builder.build()
    bb_builder.create_symlinks()
    success("BusyBox gebaut und direkt ins OverlayFS installiert")
    # Pakete installieren – Variante B (Cache → RootFS)
    # info("Installing packages into RootFS using cache variant...")
    # installer = PackageInstaller(paths, use_cache_variant=True)
    # installer.install_pkgs()
    
    installer = PacmanRootFSInstaller(rootfs_path, pacman_cache_path)

    packages = [
        "bash", "coreutils", "util-linux", "nano",
        "make", "git", "wget", "curl", "pkgconf",
        "autoconf", "automake"
    ]

    installer.install_to_rootfs(packages)
    
    
    
    # info("Installing packages into RootFS using cache variant...")
    # installer = PackageInstaller(paths)
    # installer.install_pkgs()
    

if __name__ == "__main__":
    main()
