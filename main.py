from threading import Thread
from recorder import mjpeg_recorder, audio_recorder,picture_recorder,raw_recorder
from triggers import mqtt_trigger, gpio_trigger
from utils import segment_mover,postprocessor
from config.triggers_config import TRIGGERS
from config.recorder_config import RECORD_MODE


def main():

    print("🧠 Lancement complet de PiCam5 Surveillance Suite")

    threads = [
        Thread(target=mqtt_trigger.run, daemon=True),
        Thread(target=audio_recorder.run, daemon=True),
        Thread(target=segment_mover.run, daemon=True),
        Thread(target=postprocessor.run, daemon=True)
    ]
    if RECORD_MODE == "video":
        threads.append(Thread(target=mjpeg_recorder.run, daemon=True))
    elif RECORD_MODE == "pictures":
        threads.append(Thread(target=picture_recorder.run, daemon=True))
    elif RECORD_MODE == "raw":
        threads.append(Thread(target=raw_recorder.run, daemon=True))
    for trig in TRIGGERS:
        threads.append(Thread(
            target=gpio_trigger.start_gpio_trigger,
            args=(trig["pin"], trig["trigger_on"], trig["label"]),
            daemon=True
        ))

    for t in threads:
        t.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("👋 Interruption reçue, fermeture propre...")

if __name__ == "__main__":
    main()
