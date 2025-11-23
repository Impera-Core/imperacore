from pathlib import Path
from modules.paths import Paths
from manager.pactinst import Pacman
from utils.logger import create, install, added, copy, remove, patch, loading, build, flash, test, running, success, info, warning

class PackageInstaller:
    """
    Installiert Pakete in RootFS oder optional auf dem Host.
    Unterstützt Variante B: Cache → RootFS
    """

    def __init__(self, paths: Paths, use_cache_variant: bool = False):
        self.paths = paths
        self.rootfs_dir = self.paths.rootfs
        self.cache_dir = self.paths.pacman_cache
        self.use_cache_variant = use_cache_variant
        
    def install_pkgs(self):
        # Basis- und Dev-Pakete definieren
        base_packages = ["bash", "coreutils", "util-linux", "nano", "make", "git", "wget", "curl",
                         "pkgconf", "autoconf", "automake", "apk-tools"]
        dev_packages = ["gcc", "clang", "glibc", "git", "autoconf", "automake"]

        pkg_manager = Pacman(rootfs_dir=self.rootfs_dir, pacman_cache=self.cache_dir, update_cache=True)

        # 1. Pakete in Cache herunterladen
        info("Installing packages into RootFS using cache variant...")
        create(f"Installing base packages into RootFS: {base_packages}")
        pkg_manager.download_packages(base_packages + dev_packages)

        pkg_manager.install_local_packages(
        base_packages + dev_packages,
        rootfs=self.rootfs_dir
)
        # 2. Pakete aus Cache ins RootFS extrahieren
        pkg_manager.extract_packages_to_rootfs()
        success("All packages successfully extracted into RootFS!")

    def install_pkgsx(self):
        """
        Installiert Basis- und Entwicklerpakete.
        Variante B: Cache → RootFS
        """

        pkg_manager = Pacman(rootfs_dir=self.rootfs_dir, pacman_cache=self.cache_dir)

        # --- Basis-Pakete ins RootFS ---
        base_packages = [
            "bash", "coreutils", "util-linux", "nano", "make", "git", "wget",
            "curl", "pkgconf", "autoconf", "automake", "apk-tools"
        ]

        if self.use_cache_variant:
            info("Installing packages into RootFS using cache variant...")
            create(f"🛠 Installing base packages into RootFS: {base_packages}")
            pkg_manager.download_packages(base_packages)
            pkg_manager.extract_packages_to_rootfs()
        else:
            create(f"Installing base packages into RootFS: {base_packages}")
            pkg_manager.install_packages(base_packages)

        # --- Entwicklerpakete dynamisch auf Host ---
        dev_packages = [
            "gcc", "glib2", "device-mapper", "libarchive", "zstd", "libusb",
            "glibc", "curl", "wget", "git", "clang", "pkgconf", "autoconf",
            "automake", "autogen", "bison", "flex", "libtool", "binutils",
            "m4", "gawk", "grep", "help2man", "gettext"
        ]
        install(f"Installing developer packages on Host: {dev_packages}")
        pkg_manager.install_packages(dev_packages, dynamic=True)

        success("All packages successfully installed!")

    # Optional: einzelne Actions für Convenience
    def install_base(self):
        base_packages = [
            "bash", "coreutils", "util-linux", "nano", "make", "git", "wget"
        ]
        create(f"Installing base packages: {base_packages}")
        Pacman(self.rootfs_dir, self.cache_dir).install_packages(base_packages)

    def install_dev(self):
        dev_packages = [
            "gcc", "clang", "glibc", "git", "autoconf", "automake"
        ]
        install(f"Installing dev packages: {dev_packages}")
        Pacman(self.rootfs_dir, self.cache_dir).install_packages(dev_packages, dynamic=True)
