# fake_pykms.py

class PixelFormat:
    RGBA8888 = None
    RGB888 = None
    RGB565 = None
    NV12 = None
    YUYV = None

class Plane:
    def __init__(self, *args, **kwargs): pass

class DRM:
    def __init__(self, *args, **kwargs): pass
    def close(self): pass

class Connector:
    def __init__(self, *args, **kwargs): pass
    def get_default_resolution(self): return (640, 480)

# pour d'autres composants possibles
class Mode: pass
class Framebuffer: pass
