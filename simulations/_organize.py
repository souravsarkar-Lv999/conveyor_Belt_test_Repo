"""Move image and 3D model files into assets/ folder."""
import shutil
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

moved = []
for src in ROOT.iterdir():
    if src.is_file() and src.suffix.lower() in {".webp", ".jpg", ".jpeg", ".png", ".glb", ".gif"}:
        dst = ASSETS / src.name
        shutil.move(str(src), str(dst))
        moved.append(src.name)

print("Moved:", moved)
print("Now in root:", sorted(p.name for p in ROOT.iterdir()))
print("Now in assets:", sorted(p.name for p in ASSETS.iterdir()))