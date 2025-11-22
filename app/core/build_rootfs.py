from modules.fhs_layout import FHSLayout
from modules.create_fhs_rootfs import FHSRootFSBuilder
from modules.workspace import Workspace

def main():
    # Workspace initialisieren
    ws = Workspace(".")
    ws.create()

    # FHS Layout laden
    fhs = FHSLayout("configs/rootfs/default_fhs.yaml")
    fhs.load()

    # RootFS erstellen
    builder = FHSRootFSBuilder("build/rootfs/readonly", fhs)
    builder.build()

if __name__ == "__main__":
    main()
