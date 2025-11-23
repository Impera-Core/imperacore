import subprocess
from pathlib import Path
from utils.logger import debug, info, warning, error, success
from utils.execute import run_command, run_command_live
class Pacman:
    """
    Pacman Wrapper für RootFS-Buildsystem.
    Unterstützt:
        - dynamische Installation auf Host
        - statische Installation in RootFS
        - Download in Cache (Variante B)
    """

    def __init__(self, rootfs_dir: Path | str = None, pacman_cache: Path | str = None, update_cache: bool = False):
        self.rootfs = Path(rootfs_dir) if rootfs_dir else None
        self.pacman_cache = Path(pacman_cache) if pacman_cache else None

        if self.pacman_cache:
            self.pacman_cache.mkdir(parents=True, exist_ok=True)

        if update_cache:
            self._update_db()

    def _run(self, cmd: list):
        debug(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            error(f"Command failed: {e}")
            raise

    def _update_db(self):
        """Pacman DB auf Host aktualisieren"""
        cmd = ["pacman", "-Sy", "--noconfirm"]
        if self.pacman_cache:
            cmd += [f"--cachedir={self.pacman_cache}"]
        info("Updating Pacman database on Host...")
        self._run(cmd)

    def install_packages(self, packages: list[str], dynamic: bool = False):
        """Installiert Pakete direkt ins RootFS oder dynamisch auf Host"""
        if not packages:
            return

        cmd = ["pacman", "-S", "--noconfirm"] + packages

        if self.pacman_cache:
            cmd += [f"--cachedir={self.pacman_cache}"]

        if not dynamic:
            if not self.rootfs:
                raise ValueError("RootFS-Verzeichnis muss angegeben werden!")
            cmd += [f"--root={self.rootfs}"]

        info(f"Installing packages: {packages} (dynamic={dynamic})")
        self._run(cmd)

    def download_packages(self, packages: list[str]):
        """Pakete nur in Cache herunterladen (vom Host aus, ohne --root)"""
        if not packages:
            return

        cmd = ["pacman", "-Sw", "--noconfirm"] + packages
        if self.pacman_cache:
            cmd += [f"--cachedir={self.pacman_cache}"]

        info(f"Downloading packages into cache: {packages}")
        self._run(cmd)

    def extract_packages_to_rootfs(self):
        """Extrahiert alle Pakete aus Cache ins RootFS"""
        if not self.rootfs or not self.pacman_cache:
            raise ValueError("RootFS und Pacman-Cache müssen angegeben sein!")

        pkg_files = list(self.pacman_cache.glob("*.pkg.tar.*.zst"))
        if not pkg_files:
            warning("Keine Pakete im Cache gefunden zum Extrahieren!")
            return

        for pkg_file in pkg_files:
            info(f"Extracting {pkg_file.name} into RootFS...")
            self._run(["bsdtar", "-xpf", str(pkg_file), "-C", str(self.rootfs)])
    
    def install_local_packages(self, packages: list[str], rootfs: Path) -> bool:
        """
        Installiert lokal heruntergeladene .zst Pakete in ein RootFS über pacman -U.
        Erwartet, dass die Pakete bereits im Cache liegen.

        :param packages: Paketnamen ohne .zst (z.B. "bash")
        :param rootfs: Pfad zum RootFS
        """
        info(f"📦 Installiere lokal gecachte Pakete ins RootFS via pacman -U...")

        # Pfad zum Cache
        cache_dir = self.pacman_cache
        if not cache_dir.exists():
            error(f"Cache-Verzeichnis existiert nicht: {cache_dir}")
            return False

        # Liste der tatsächlichen .zst-Dateien erstellen
        zst_files = []
        for pkg in packages:
            matches = list(f"{pkg}-*.zst")
            if not matches:
                error(f"❌ Paket {pkg} nicht im Cache gefunden (fehlendes .zst)")
                return False
            # Nimm das neueste Paket (falls mehrere Versionen existieren)
            matches.sort()
            zst_files.append(matches[-1])

        info(f"📦 Zu installierende Dateien: {zst_files}")

        # pacman -U Befehl
        cmd = [
            "pacman",
            "-U",
            "--noconfirm",
            "--root", str(self.rootfs),
            "--cachedir", str(cache_dir),
        ] + [str(f) for f in zst_files]

        return run_command(cmd, desc="Installiere lokal gecachte Pakete ins RootFS")

    def install(self):
        if not self.rootfs or not self.pacman_cache:
            raise ValueError("RootFS und Pacman-Cache müssen angegeben sein!")

        pkg_files = list(self.pacman_cache.glob("*.pkg.tar.*"))
        if not pkg_files:
            warning("Keine Pakete im Cache gefunden zum Extrahieren!")
            return

        for pkg_file in pkg_files:
            info(f"Extracting {pkg_file.name} into RootFS...")
            self._run(["sudo", "pacman", "-U", str(pkg_file), "--root", "/mnt/nexuzfs/work/rootfs"])