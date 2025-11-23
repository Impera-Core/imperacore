import shutil
import subprocess
import os
import stat
from pathlib import Path


class PacmanRootFSInstaller:
    def __init__(self, rootfs: Path, cache_dir: Path):
        self.rootfs = Path(rootfs)
        self.cache_dir = Path(cache_dir)

    # -------------------------------------------------------------
    # STATIC: UNIX Sonderdateien erkennen
    # -------------------------------------------------------------
    @staticmethod
    def is_special_file(path: Path) -> bool:
        """Ignore UNIX sockets, device files, pipes etc."""
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            return True

        return (
            stat.S_ISSOCK(mode) or
            stat.S_ISCHR(mode) or
            stat.S_ISBLK(mode) or
            stat.S_ISFIFO(mode)
        )

    # -------------------------------------------------------------
    # STATIC: Sicheres rekursives Kopieren
    # -------------------------------------------------------------
    @staticmethod
    def safe_copytree(src: Path, dst: Path):
        """Copy directory recursively but skip unsupported file types."""
        for root, dirs, files in os.walk(src):
            rel = Path(root).relative_to(src)
            target_dir = dst / rel
            target_dir.mkdir(parents=True, exist_ok=True)

            for file in files:
                src_file = Path(root) / file

                if PacmanRootFSInstaller.is_special_file(src_file):
                    print(f"[SKIP] {src_file} (socket/device/fifo)")
                    continue

                dst_file = target_dir / file
                shutil.copy2(src_file, dst_file)

    # -------------------------------------------------------------
    # PACMAN CONFIGS INS ROOTFS
    # -------------------------------------------------------------
    def copy_pacman_configs(self):
        print("[INFO] Copying pacman config...")

        (self.rootfs / "etc/pacman.d").mkdir(parents=True, exist_ok=True)
        (self.rootfs / "usr/share/pacman").mkdir(parents=True, exist_ok=True)

        # pacman.conf kopieren
        shutil.copy2("/etc/pacman.conf", self.rootfs / "etc/pacman.conf")

        # pacman.d (mit Skip für sockets)
        self.safe_copytree(
            Path("/etc/pacman.d"),
            self.rootfs / "etc/pacman.d"
        )

        # /usr/share/pacman
        self.safe_copytree(
            Path("/usr/share/pacman"),
            self.rootfs / "usr/share/pacman"
        )

        print("✓ pacman config copied safely.")

    # -------------------------------------------------------------
    # PACMAN PAKETE HERUNTERLADEN
    # -------------------------------------------------------------
    def download_packages(self, pkgs: list[str]):
        cmd = [
            "pacman",
            "-Sw",
            "--noconfirm",
            "--cachedir", str(self.cache_dir),
        ] + pkgs

        print(f"[INFO] Downloading via pacman: {pkgs}")
        subprocess.run(cmd, check=True)
        print("✓ Pakete in Cache heruntergeladen.")

    # -------------------------------------------------------------
    # PAKETE INS ROOTFS EXTRAHIEREN
    # -------------------------------------------------------------
    def extract_all_packages(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        pkg_files = list(self.cache_dir.glob("*.pkg.tar.zst"))

        if not pkg_files:
            print("⚠ Keine .pkg.tar.zst Dateien im Cache gefunden.")
            return

        for pkg in pkg_files:
            print(f"[EXTRACT] {pkg.name}")
            subprocess.run(
                ["bsdtar", "-xpf", str(pkg), "-C", str(self.rootfs)],
                check=True
            )

        print("✓ Alle Pakete erfolgreich extrahiert.")

    # -------------------------------------------------------------
    # KOMBINIERTE INSTALLATION
    # -------------------------------------------------------------
    def install_to_rootfs(self, packages: list[str]):
        self.copy_pacman_configs()
        self.download_packages(packages)
        self.extract_all_packages()
        print("🎉 RootFS erfolgreich mit pacman Paketen befüllt!")
