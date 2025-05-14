import os
import time
import shutil
from datetime import datetime
from config.recorder_config import TEMP_DIR, BASE_OUTPUT_DIR

CHECK_INTERVAL = 60  # secondes
FILE_AGE_THRESHOLD = 5  # secondes depuis dernière modification

# Extensions prises en charge : vidéos, audio et images
EXTENSIONS = [".mjpeg", ".wav", ".png", ".jpg", ".dng", ".raw"]



def is_file_ready(path):
    try:
        return time.time() - os.path.getmtime(path) > FILE_AGE_THRESHOLD
    except FileNotFoundError:
        return False

def run():
    print(f"🚚 Démarrage du segment mover (src: {TEMP_DIR})")
    while True:
        # Liste les fichiers valides avec une extension ciblée
        files = [f for f in os.listdir(TEMP_DIR) if os.path.splitext(f)[1].lower() in EXTENSIONS]
        ready_files = [f for f in files if is_file_ready(os.path.join(TEMP_DIR, f))]

        if ready_files:
            try:
                with open(os.path.join(TEMP_DIR, ".current_session"), "r") as f:
                    session_name = f.read().strip()
            except FileNotFoundError:
                session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S")

            dest_dir = os.path.join(BASE_OUTPUT_DIR, session_name)
            
            os.makedirs(dest_dir, exist_ok=True)
            os.chmod(dest_dir, 0o775)  # rwxrwxr-x


            print(f"📦 Déplacement de {len(ready_files)} fichiers vers {dest_dir}")
            for f in ready_files:
                src = os.path.join(TEMP_DIR, f)
                dst = os.path.join(dest_dir, f)
                try:
                    shutil.move(src, dst)
                    os.chmod(dst, 0o664)  # ✅ important pour que SMB puisse supprimer depuis le PC
                    print(f"✅ Déplacé : {f}")
                except Exception as e:
                    print(f"❌ Erreur sur {f} :", e)


        else:
            print("🕵️ Aucun fichier à déplacer pour le moment.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
