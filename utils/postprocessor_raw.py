import os
import numpy as np
from pathlib import Path
from config.recorder_config import BASE_OUTPUT_DIR

RAW_WIDTH = 1920
RAW_HEIGHT = 1080

def decode_raw_bayer(file_path, width, height):
    with open(file_path, 'rb') as f:
        raw_data = np.frombuffer(f.read(), dtype=np.uint8)
    if raw_data.size != width * height:
        print(f"❌ Taille inattendue pour {file_path}")
        return None
    raw_image = raw_data.reshape((height, width))
    return raw_image

def convert_all_raw_to_png():
    print("🖼️ Début conversion des .raw en .png")
    for root, _, files in os.walk(BASE_OUTPUT_DIR):
        for file in files:
            if file.endswith(".raw"):
                raw_path = Path(root) / file
                png_path = raw_path.with_suffix(".png")
                if png_path.exists():
                    continue
                img = decode_raw_bayer(raw_path, RAW_WIDTH, RAW_HEIGHT)
                if img is not None:
                    from imageio import imwrite
                    imwrite(str(png_path), img)
                    os.remove(raw_path)
                    print(f"✅ Converti : {raw_path.name} ➜ {png_path.name}")

if __name__ == "__main__":
    convert_all_raw_to_png()
