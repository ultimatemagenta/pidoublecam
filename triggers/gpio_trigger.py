import RPi.GPIO as GPIO
import time
from state_manager import enable_recording, disable_recording, is_recording

def start_gpio_trigger(pin, trigger_on=GPIO.HIGH, label="GPIO"):
    pull = GPIO.PUD_DOWN if trigger_on == GPIO.HIGH else GPIO.PUD_UP

    def on_gpio_change(channel):
        value = GPIO.input(pin)
        print(f"⚡️ [{label}] GPIO change: {value}")
        if value == trigger_on and not is_recording():
            print(f"🚀 [{label}] Enregistrement activé")
            enable_recording()
        elif value != trigger_on and is_recording():
            print(f"🛑 [{label}] Enregistrement désactivé")
            disable_recording()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=pull)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=on_gpio_change, bouncetime=200)

    print(f"🔌 [{label}] Prêt sur pin {pin} (niveau déclencheur : {trigger_on})")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
