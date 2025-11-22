import argparse
from pathlib import Path
from modules.paths import Paths
from modules.workspace import Workspace
from modules.fhs_layout import FHSLayout
from modules.create_fhs_rootfs import FHSRootFSBuilder
from modules.arch import ARCHES

def main():
    parser = argparse.ArgumentParser(description="MetaNexuz RootFS Builder")
    parser.add_argument(
        "--fhs", type=str, required=True,
        help="Pfad zum FHS YAML Layout (z.B. configs/rootfs/default_fhs.yaml)"
    )
    parser.add_argument(
        "--arch", type=str, default="x86_64",
        choices=ARCHES.keys(),
        help="Zielarchitektur (x86_64, x86_64-efi, arm64)"
    )
    args = parser.parse_args()
    
    fhs_layout = args.fhs
    fhs_configs = Path("configs") / "rootfs"
    fhs_yaml = Path(fhs_configs) / fhs_layout
    if not fhs_yaml.exists():
        print(f"[!] FHS Layout nicht gefunden: {fhs_yaml}")
        return
    

    arch_conf = ARCHES[args.arch]


    # 2️⃣ Paths & Workspace initialisieren
    paths = Paths(Path("."))
    ws = Workspace(paths.root)
    ws.ensure()


    # 3️⃣ FHS Layout laden
    layout = FHSLayout(fhs_yaml)
    layout.load()


    # 4️⃣ RootFS Pfad pro Architektur
    rootfs_path = paths.rootfs / arch_conf.rootfs_subdir



    # Optional sauber machen
    if rootfs_path.exists():
        import shutil
        shutil.rmtree(rootfs_path)
    rootfs_path.mkdir(parents=True, exist_ok=True)
    
    

    # 5️⃣ RootFS erstellen
    builder = FHSRootFSBuilder(rootfs_path, layout)
    builder.build()
    
    

    print(f"[✓] RootFS erfolgreich erstellt für Architektur {args.arch} in {rootfs_path}")




if __name__ == "__main__":
    main()
