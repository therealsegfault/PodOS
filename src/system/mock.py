from PySide6.QtCore import QObject, Slot, Property, Signal

class SystemBridge(QObject):
    def __init__(self):
        super().__init__()
        self._battery = 72
        self._wifi = "PodNet"
        self._playing = False

    @Property(int, constant=False)
    def battery(self):
        return self._battery

    @Property(str, constant=False)
    def wifi(self):
        return self._wifi

    @Property(bool, constant=False)
    def playing(self):
        return self._playing

    @Slot(str)
    def launchApp(self, app_id):
        print(f"launching {app_id}")