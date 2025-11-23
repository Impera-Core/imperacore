from dataclasses import dataclass

@dataclass(frozen=True)
class ArchConfig:
    arch: str
    qemu_user_binary: str
    rootfs_subdir: str

ARCHES = {
    "x86_64": ArchConfig(
        arch="x86_64",
        qemu_user_binary="",
        rootfs_subdir="x86_64"
    ),
    "x86_64-efi": ArchConfig(
        arch="x86_64-efi",
        qemu_user_binary="",
        rootfs_subdir="x86_64-efi"
    ),
    "arm64": ArchConfig(
        arch="arm64",
        qemu_user_binary="qemu-aarch64-static",
        rootfs_subdir="arm64"
    )
}
