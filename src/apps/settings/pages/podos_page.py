from gi.repository import Gtk
from src.apps.settings.settings_app import SubPage, make_section, make_row


class PodOSPage(SubPage):
    def __init__(self, bridge, flipstack):
        super().__init__('podOS', flipstack)
        self.bridge = bridge
        self._wheel_sensitivity = 5
        self._haptics = True
        self._show_labels = True
        self._build()

    def _build(self):
        # Click wheel sensitivity
        wheel_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        wheel_card.set_margin_start(16)
        wheel_card.set_margin_end(16)
        wheel_card.set_margin_top(16)
        wheel_card.add_css_class('settings-card')

        wheel_lbl = Gtk.Label(label='Click Wheel Sensitivity')
        wheel_lbl.set_halign(Gtk.Align.START)
        wheel_lbl.add_css_class('settings-label')
        wheel_lbl.set_margin_start(16)
        wheel_lbl.set_margin_top(10)
        wheel_card.append(wheel_lbl)

        labels_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        labels_row.set_margin_start(16)
        labels_row.set_margin_end(16)
        slow = Gtk.Label(label='Slow')
        slow.add_css_class('settings-secondary')
        slow.set_hexpand(True)
        slow.set_halign(Gtk.Align.START)
        fast = Gtk.Label(label='Fast')
        fast.add_css_class('settings-secondary')
        labels_row.append(slow)
        labels_row.append(fast)
        wheel_card.append(labels_row)

        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        slider.set_value(self._wheel_sensitivity)
        slider.set_margin_start(16)
        slider.set_margin_end(16)
        slider.set_margin_bottom(10)
        slider.set_draw_value(False)
        slider.connect('value-changed', lambda s: setattr(self, '_wheel_sensitivity', int(s.get_value())))
        wheel_card.append(slider)
        self.body.append(wheel_card)

        # Haptics + Starboard labels section
        def build_row(spec):
            key, emoji, color, label, summary = spec
            initial = getattr(self, key)
            return make_row(emoji, color, label, summary,
                            has_toggle=True, toggle_state=initial,
                            on_toggle=lambda v, k=key: setattr(self, k, v))

        rows = [
            ('_haptics',     '📳', '#5856d6', 'Haptic Feedback',    'Vibrate on interaction'),
            ('_show_labels', '🏷',  '#ff9500', 'Starboard Labels',   'Show app names below icons'),
        ]
        self.body.append(make_section('Interface', rows, build_row))
