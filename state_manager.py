from threading import Event

recording_event = Event()

def enable_recording():
    recording_event.set()

def disable_recording():
    recording_event.clear()

def is_recording():
    return recording_event.is_set()

def get_event():
    return recording_event
