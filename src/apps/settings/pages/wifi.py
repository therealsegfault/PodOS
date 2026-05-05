from gi.repository import Gtk
from src.apps.settings.settings_app import SubPage, make_section, make_row, ToggleSwitch

MOCK_NETWORKS = ['PodNet', 'HomeNetwork_5G', 'iPhone Hotspot', 'CoffeeShop_Guest']


class WifiPage(SubPage):
    def __init__(self, bridge, flipstack):
        super().__init__('Connectivity', flipstack)
        self.bridge = bridge
        self._wifi_on = True
        self._build()

    def _build(self):
        # Wi-Fi toggle
        wifi_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        wifi_card.set_margin_start(16)
        wifi_card.set_margin_end(16)
        wifi_card.set_margin_top(16)
        wifi_card.add_css_class('settings-card')

        wifi_row = make_row('📶', '#34aadc', 'Wi-Fi', 'Toggle wireless',
                            has_toggle=True, toggle_state=self._wifi_on,
                            on_toggle=self._toggle_wifi)
        wifi_card.append(wifi_row)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_start(60)
        wifi_card.append(sep)

        bt_row = make_row('🔵', '#007aff', 'Bluetooth', 'Toggle bluetooth',
                          has_toggle=True,
                          toggle_state=self.bridge.bluetoothEnabled,
                          on_toggle=self.bridge.setBluetooth)
        wifi_card.append(bt_row)
        self.body.append(wifi_card)

        # Networks list
        hdr = Gtk.Label(label='AVAILABLE NETWORKS')
        hdr.set_halign(Gtk.Align.START)
        hdr.set_margin_start(32)
        hdr.set_margin_top(16)
        hdr.set_margin_bottom(4)
        hdr.add_css_class('settings-section-header')
        self.body.append(hdr)

        self.net_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.net_card.set_margin_start(16)
        self.net_card.set_margin_end(16)
        self.net_card.add_css_class('settings-card')
        self._populate_networks()
        self.body.append(self.net_card)

    def _toggle_wifi(self, state):
        self._wifi_on = state

    def _populate_networks(self):
        for child in list(self.net_card):
            self.net_card.remove(child)

        for i, ssid in enumerate(MOCK_NETWORKS):
            connected = ssid == self.bridge.wifi
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.set_margin_start(16)
            row.set_margin_end(16)
            row.set_margin_top(10)
            row.set_margin_bottom(10)

            lbl = Gtk.Label(label=ssid)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_hexpand(True)
            lbl.add_css_class('settings-label')
            row.append(lbl)

            if connected:
                check = Gtk.Label(label='✓')
                check.add_css_class('accent')
                row.append(check)
            else:
                chev = Gtk.Label(label='›')
                chev.add_css_class('settings-chevron')
                row.append(chev)

            click = Gtk.GestureClick()
            click.connect('released', lambda *_, s=ssid: self._connect(s))
            row.add_controller(click)
            self.net_card.append(row)

            if i < len(MOCK_NETWORKS) - 1:
                sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                sep.set_margin_start(16)
                self.net_card.append(sep)

    def _connect(self, ssid):
        self.bridge.connectWifi(ssid)
        self._populate_networks()
