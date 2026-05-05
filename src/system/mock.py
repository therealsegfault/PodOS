"""Mock system bridge for macOS/Windows development — no DBus required."""
from gi.repository import GObject


class SystemBridge(GObject.Object):
    # Signals
    batteryChanged = GObject.Signal()
    wifiChanged = GObject.Signal()
    bluetoothChanged = GObject.Signal()
    volumeChanged = GObject.Signal()
    brightnessChanged = GObject.Signal()
    eqPresetChanged = GObject.Signal()
    aodChanged = GObject.Signal()
    uptimeChanged = GObject.Signal()
    appLaunchRequested = GObject.Signal('appLaunchRequested', arg_types=(str,))

    def __init__(self):
        super().__init__()
        self._battery = 72
        self._wifi = "PodNet"
        self._bluetooth_enabled = False
        self._volume = 72
        self._brightness = 80
        self._eq_preset = "Flat"
        self._aod_enabled = False
        self._uptime = "2h 14m"

    # ── Properties ──────────────────────────────────────────────────────────

    @GObject.Property(type=int)
    def battery(self):
        return self._battery

    @GObject.Property(type=str)
    def wifi(self):
        return self._wifi

    @GObject.Property(type=bool, default=False)
    def bluetoothEnabled(self):
        return self._bluetooth_enabled

    @GObject.Property(type=int)
    def volume(self):
        return self._volume

    @GObject.Property(type=int)
    def brightness(self):
        return self._brightness

    @GObject.Property(type=str)
    def eqPreset(self):
        return self._eq_preset

    @GObject.Property(type=bool, default=False)
    def aodEnabled(self):
        return self._aod_enabled

    @GObject.Property(type=str)
    def uptime(self):
        return self._uptime

    # ── Slots (callable from UI) ────────────────────────────────────────────

    def setBluetooth(self, enabled: bool):
        self._bluetooth_enabled = enabled
        self.notify('bluetoothEnabled')
        self.emit('bluetoothChanged')

    def setVolume(self, value: int):
        self._volume = max(0, min(100, value))
        self.notify('volume')
        self.emit('volumeChanged')

    def setBrightness(self, value: int):
        self._brightness = max(0, min(100, value))
        self.notify('brightness')
        self.emit('brightnessChanged')

    def setAod(self, enabled: bool):
        self._aod_enabled = enabled
        self.notify('aodEnabled')
        self.emit('aodChanged')

    def setEqPreset(self, preset: str):
        self._eq_preset = preset
        self.notify('eqPreset')
        self.emit('eqPresetChanged')

    def connectWifi(self, ssid: str):
        self._wifi = ssid
        self.notify('wifi')
        self.emit('wifiChanged')

    def enterDiskMode(self):
        print("[mock] enterDiskMode")

    def enterRecovery(self):
        print("[mock] enterRecovery")

    def checkUpdate(self):
        print("[mock] checkUpdate → up to date")

    def launchApp(self, app_id: str):
        print(f"[mock] launchApp: {app_id}")
        self.emit('appLaunchRequested', app_id)
