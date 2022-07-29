import threading

from PySide6 import QtCore

lock = threading.Lock()


# Thread-safety singleton metaclass
class Singleton(type(QtCore.QObject), type):
    _instances = {}

    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
