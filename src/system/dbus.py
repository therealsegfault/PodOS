"""DBus system bridge for Void Linux / production device."""
try:
    import dbus
    import dbus.mainloop.glib
    HAS_DBUS = True
except ImportError:
    HAS_DBUS = False

from gi.repository import GObject


class SystemBridge(GObject.Object):
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
        # Fall back to mock values if dbus isn't available yet
        self._battery = 72
        self._wifi = ""
        self._bluetooth_enabled = False
        self._volume = 72
        self._brightness = 80
        self._eq_preset = "Flat"
        self._aod_enabled = False
        self._uptime = ""

        if HAS_DBUS:
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            try:
                self._bus = dbus.SystemBus()
                self._connect_signals()
            except Exception as e:
                print(f"[dbus] init failed: {e}")

    def _connect_signals(self):
        # UPower for battery
        try:
            upower = self._bus.get_object('org.freedesktop.UPower',
                                          '/org/freedesktop/UPower/devices/battery_BAT0')
            props = dbus.Interface(upower, 'org.freedesktop.DBus.Properties')
            pct = props.Get('org.freedesktop.UPower.Device', 'Percentage')
            self._battery = int(pct)
        except Exception:
            pass

        # NetworkManager for wifi
        try:
            nm = self._bus.get_object('org.freedesktop.NetworkManager',
                                      '/org/freedesktop/NetworkManager')
            props = dbus.Interface(nm, 'org.freedesktop.DBus.Properties')
            self._wifi = str(props.Get('org.freedesktop.NetworkManager', 'ActiveConnectionsSsid'))
        except Exception:
            pass

    # ── Properties (mirrors mock.py interface) ───────────────────────────────

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

    # ── Slots ────────────────────────────────────────────────────────────────

    def setBluetooth(self, enabled: bool):
        self._bluetooth_enabled = enabled
        self.notify('bluetoothEnabled')

    def setVolume(self, value: int):
        self._volume = max(0, min(100, value))
        self.notify('volume')

    def setBrightness(self, value: int):
        self._brightness = max(0, min(100, value))
        self.notify('brightness')

    def setAod(self, enabled: bool):
        self._aod_enabled = enabled
        self.notify('aodEnabled')

    def setEqPreset(self, preset: str):
        self._eq_preset = preset
        self.notify('eqPreset')

    def connectWifi(self, ssid: str):
        self._wifi = ssid
        self.notify('wifi')

    def enterDiskMode(self):
        import subprocess
        subprocess.Popen(['modprobe', 'g_mass_storage'])

    def enterRecovery(self):
        import subprocess
        subprocess.Popen(['reboot', '--recovery'])

    def checkUpdate(self):
        import subprocess
        subprocess.Popen(['xbps-install', '-Su'])

    def launchApp(self, app_id: str):
        self.emit('appLaunchRequested', app_id)
