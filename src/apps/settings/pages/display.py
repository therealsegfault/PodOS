from gi.repository import Gtk, Gdk
from src.apps.settings.settings_app import SubPage, make_section, make_row, ToggleSwitch


class DisplayPage(SubPage):
    def __init__(self, bridge, flipstack):
        super().__init__('Display', flipstack)
        self.bridge = bridge
        self._build()

    def _build(self):
        # Brightness slider row
        bright_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bright_box.set_margin_start(16)
        bright_box.set_margin_end(16)
        bright_box.set_margin_top(16)
        bright_box.set_margin_bottom(0)
        bright_box.add_css_class('settings-card')

        lbl = Gtk.Label(label='Brightness')
        lbl.set_halign(Gtk.Align.START)
        lbl.add_css_class('settings-label')
        lbl.set_margin_start(16)
        lbl.set_margin_top(10)
        bright_box.append(lbl)

        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_value(self.bridge.brightness)
        slider.set_margin_start(16)
        slider.set_margin_end(16)
        slider.set_margin_bottom(10)
        slider.connect('value-changed', lambda s: self.bridge.setBrightness(int(s.get_value())))
        bright_box.append(slider)
        self.body.append(bright_box)

        # Sleep timer
        sleep_spec = [
            ('⏰', '#ff9500', 'Sleep Timer', '2 minutes', '2 min', None),
        ]
        def build_sleep(spec):
            return make_row(spec[0], spec[1], spec[2], spec[3], spec[4])
        self.body.append(make_section('', sleep_spec, build_sleep))

        # AOD toggle
        def aod_spec_builder(spec):
            return make_row('🌙', '#5856d6', 'Always-On Display',
                            'Show time when sleeping', '',
                            has_toggle=True,
                            toggle_state=self.bridge.aodEnabled,
                            on_toggle=self.bridge.setAod)
        self.body.append(make_section('', [None], aod_spec_builder))
