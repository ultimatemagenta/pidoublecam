import RPi.GPIO as GPIO

TRIGGERS = [
    {
        "label": "GPIO_Pi_Toggle",
        "pin": 17,
        "trigger_on": GPIO.HIGH,
    },
    {
        "label": "GPIO_PIR_Sensor",
        "pin": 27,
        "trigger_on": GPIO.LOW,
    }
]
