#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# core/busybox.py

import os
import json
import multiprocessing
from pathlib import Path
from utils.download import download_file, extract_archive
from utils.execute import run_command_live
from utils.logger import *

DEFAULT_PATCH = {"CONFIG_TC": "n", "CONFIG_STATIC": "y"}

class BusyBoxBuilder:
    def __init__(self, json_path: Path, paths: dict, arch: str | None = None):
        self.json_path = Path(json_path)
        if not self.json_path.exists():
            raise FileNotFoundError(f"BusyBox JSON nicht gefunden: {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.version = self.config["version"]
        self.urls = self.config.get("urls", [])
        self.extra_cfg = self.config.get("extra_config", {})
        self.config_patches = self._parse_patch_list(self.config.get("config_patch", []))
        self.cross_compile = self.config.get("cross_compile", {})
        self.arch = arch or self.cross_compile.get("arch", "x86_64")
        
        self.work_path = paths.work
        self.downloads_path = paths.download
        self.rootfs_path = paths.rootfs
        # Pfade
        self.work_dir = Path(self.work_path)
        self.downloads_dir = Path(self.downloads_path)
        self.rootfs_dir = Path(self.rootfs_path)
        self.src_dir_template = self.work_path / f"busybox-{self.version}"

        if self.arch != "x86_64":
            self.cross_compile.setdefault("compiler_prefix", "aarch64-linux-gnu-")
        else:
            self.cross_compile["compiler_prefix"] = ""

    @staticmethod
    def _parse_patch_list(patch_list):
        patch_dict = {}
        for line in patch_list:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                patch_dict[key.strip()] = val.strip()
        return patch_dict

    @staticmethod
    def _set_config_option(cfg_file: Path, key: str, value: str):
        lines = cfg_file.read_text().splitlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                break
        else:
            lines.append(f"{key}={value}")
        cfg_file.write_text("\n".join(lines) + "\n")

    def _patch_config(self, busybox_src_dir: Path):
        cfg_file = busybox_src_dir / ".config"
        if not cfg_file.exists():
            raise FileNotFoundError(f".config nicht gefunden in {busybox_src_dir}")
        for key, val in {**DEFAULT_PATCH, **self.config_patches, **self.extra_cfg}.items():
            self._set_config_option(cfg_file, key, val)
        success(f"BusyBox .config gepatcht: {list({**DEFAULT_PATCH, **self.config_patches, **self.extra_cfg}.keys())}")

    def create_symlinks(self):
        busybox_path = self.rootfs_dir / "bin/busybox"
        if not busybox_path.exists():
            warning(f"BusyBox Binary nicht gefunden in {busybox_path}, Symlinks übersprungen")
            return
        sbin_init = self.rootfs_dir / "sbin/init"
        sh_link = self.rootfs_dir / "bin/sh"
        sbin_init.parent.mkdir(parents=True, exist_ok=True)
        if not sbin_init.exists():
            sbin_init.symlink_to("../bin/busybox")
        if not sh_link.exists():
            sh_link.symlink_to("busybox")
        success("[SUCCESS] BusyBox Symlinks erstellt")

    def build(self):
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.rootfs_dir.mkdir(parents=True, exist_ok=True)

        tarball = download_file(self.urls, self.downloads_path)
        extracted_dir = extract_archive(tarball, self.work_path)
        busybox_src_dir = Path(self.src_dir_template).with_name(f"busybox-{self.version}")

        scripts_dir = busybox_src_dir / "scripts"
        if scripts_dir.exists():
            for root, dirs, files in os.walk(scripts_dir):
                for f in files:
                    file_path = Path(root) / f
                    file_path.chmod(file_path.stat().st_mode | 0o111)

        env = os.environ.copy()
        env["ARCH"] = self.arch
        env["CROSS_COMPILE"] = self.cross_compile.get("compiler_prefix", "")
        env["CFLAGS"] = self.cross_compile.get("cflags", "")
        env["LDFLAGS"] = self.cross_compile.get("ldflags", "")

        run_command_live(["make", "defconfig"], cwd=busybox_src_dir, env=env, desc="BusyBox defconfig")
        self._patch_config(busybox_src_dir)
        run_command_live(["make", "oldconfig", "KCONFIG_ALLCONFIG=/dev/null"], cwd=busybox_src_dir, env=env, desc="BusyBox oldconfig")
        run_command_live(["make", f"-j{multiprocessing.cpu_count()}"], cwd=busybox_src_dir, env=env, desc="BusyBox kompilieren")
        run_command_live(["make", f"CONFIG_PREFIX={self.rootfs_path}", "install"], cwd=busybox_src_dir, env=env, desc="BusyBox installieren")
        self.create_symlinks()
        success(f"✅ BusyBox {self.version} erfolgreich installiert in {self.rootfs_path}")
