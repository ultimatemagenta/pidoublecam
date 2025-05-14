import time
import json
import paho.mqtt.client as mqtt
from state_manager import enable_recording, disable_recording, is_recording

MQTT_BROKER = "192.168.86.31"
MQTT_PORT = 1883
MQTT_USER = "picamguestroom"
MQTT_PASSWORD = "cksflO3p"
TOPIC_COMMAND = "home/picam5/switch/set"
TOPIC_STATE = "home/picam5/switch/state"
CLIENT_ID = "picam5_switch"

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connecté au broker MQTT avec le code {rc}")
    client.subscribe(TOPIC_COMMAND)

    switch_payload = {
        "name": "PiCam5 Recording",
        "command_topic": TOPIC_COMMAND,
        "state_topic": TOPIC_STATE,
        "payload_on": "ON",
        "payload_off": "OFF",
        "device": {
            "identifiers": ["picam5"],
            "name": "PiCam5",
            "manufacturer": "Bixxy Inc.",
            "model": "Surveillance Unit"
        },
        "unique_id": "picam5_recording_switch"
    }
    client.publish("homeassistant/switch/picam5_recording/config", json.dumps(switch_payload), retain=True)
    print("📡 Switch MQTT annoncé à Home Assistant.")

def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip().upper()
    print(f"📥 Commande MQTT reçue : {payload}")
    if payload == "ON":
        if not is_recording():
            print("🚀 Enregistrement activé via HA")
            enable_recording()
    elif payload == "OFF":
        if is_recording():
            print("🛑 Enregistrement désactivé via HA")
            disable_recording()

def run():
    print("📡 Démarrage du déclencheur MQTT (mode switch)")
    client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311, transport="tcp")



    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    last_state = None
    try:
        while True:
            current_state = "ON" if is_recording() else "OFF"
            if current_state != last_state:
                client.publish(TOPIC_STATE, current_state, retain=True)
                print(f"📤 État MQTT mis à jour : {current_state}")
                last_state = current_state
            time.sleep(1)
    except KeyboardInterrupt:
        print("👋 Arrêt manuel")
    finally:
        client.loop_stop()
        client.disconnect()
