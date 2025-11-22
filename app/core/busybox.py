from pathlib import Path
import os
from utils.load import ConfigLoader
from utils.execute import run_command
from module.logger import info, success, error

class BusyBoxBuilder2:
    def __init__(self, config_path: str):
        self.config = ConfigLoader.load(config_path)
        self.version = self.config['busybox']['version']
        self.url = self.config['busybox']['download_url'].replace("{version}", self.version)
        self.targets = self.config['busybox'].get('targets', ['x86_64'])
        self.build_dir = Path(self.config['busybox'].get('build_dir', 'build/busybox'))
        self.install_dir = Path(self.config['busybox'].get('install_dir', 'build/rootfs-upper/bin'))
        self.config_file = self.config['busybox'].get('config')
        self.make_jobs = self.config['busybox'].get('make_jobs', 4)

        self.src_dir = self.build_dir / f"busybox-{self.version}"

    def prepare_dirs(self):
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.install_dir.mkdir(parents=True, exist_ok=True)
        info(f"Build- und Install-Verzeichnisse vorbereitet: {self.build_dir}, {self.install_dir}")

    def download_source(self):
        tarball = self.build_dir / f"busybox-{self.version}.tar.bz2"
        if not tarball.exists():
            info(f"Lade BusyBox {self.version} von {self.url}")
            if not run_command(["wget", "-O", str(tarball), self.url], desc="BusyBox herunterladen"):
                raise RuntimeError("Fehler beim Herunterladen von BusyBox")
        else:
            info(f"BusyBox-Tarball bereits vorhanden: {tarball}")

        # Entpacken
        if not self.src_dir.exists():
            info(f"Entpacke BusyBox Quellcode nach {self.src_dir}")
            if not run_command(["tar", "xjf", str(tarball), "-C", str(self.build_dir)], desc="BusyBox entpacken"):
                raise RuntimeError("Fehler beim Entpacken von BusyBox")
        else:
            info(f"Quellcode bereits vorhanden: {self.src_dir}")

    def build_target(self, arch: str):
        info(f"Starte BusyBox Build für {arch}")
        env = os.environ.copy()
        if arch == "aarch64":
            env["CROSS_COMPILE"] = "aarch64-linux-gnu-"
        elif arch == "x86_64":
            env["CROSS_COMPILE"] = ""
        else:
            error(f"Unbekannte Architektur: {arch}")
            return

        # Konfiguration kopieren falls vorhanden
        if self.config_file and Path(self.config_file).exists():
            run_command(["cp", self.config_file, str(self.src_dir / ".config")], desc="BusyBox .config kopieren")
        else:
            info("Keine custom .config angegeben, Default-Konfiguration wird verwendet")

        # Build
        if not run_command(["make", "oldconfig"], cwd=self.src_dir, env=env, desc=f"BusyBox oldconfig für {arch}"):
            raise RuntimeError(f"Fehler bei oldconfig für {arch}")
        if not run_command(["make", f"-j{self.make_jobs}"], cwd=self.src_dir, env=env, desc=f"BusyBox bauen für {arch}"):
            raise RuntimeError(f"Fehler beim Kompilieren von BusyBox für {arch}")
        if not run_command(["make", f"CONFIG_PREFIX={self.install_dir}", "install"], cwd=self.src_dir, env=env,
                           desc=f"BusyBox installieren für {arch}"):
            raise RuntimeError(f"Fehler beim Installieren von BusyBox für {arch}")

        success(f"BusyBox Build für {arch} abgeschlossen")

    def build_all(self):
        self.prepare_dirs()
        self.download_source()
        for arch in self.targets:
            self.build_target(arch)
