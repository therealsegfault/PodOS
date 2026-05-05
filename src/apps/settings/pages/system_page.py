from gi.repository import Gtk
from src.apps.settings.settings_app import SubPage, make_section, make_row

ABOUT_INFO = [
    ('Device',        '*pod gen 1'),
    ('podOS Version', '1.0.0-alpha'),
    ('Build',         '20260505'),
    ('Kernel',        'Linux 6.18.5'),
    ('Chip',          'Allwinner A64'),
    ('Serial',        'PODOS-0001'),
]


class SystemPage(SubPage):
    def __init__(self, bridge, flipstack):
        super().__init__('System', flipstack)
        self.bridge = bridge
        self._build()

    def _build(self):
        # About card
        about_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        about_card.set_margin_start(16)
        about_card.set_margin_end(16)
        about_card.set_margin_top(16)
        about_card.add_css_class('settings-card')

        for i, (key, val) in enumerate(ABOUT_INFO):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.set_margin_start(16)
            row.set_margin_end(16)
            row.set_margin_top(10)
            row.set_margin_bottom(10)

            k_lbl = Gtk.Label(label=key)
            k_lbl.set_halign(Gtk.Align.START)
            k_lbl.set_hexpand(True)
            k_lbl.add_css_class('settings-label')

            v_lbl = Gtk.Label(label=val)
            v_lbl.add_css_class('settings-secondary')

            row.append(k_lbl)
            row.append(v_lbl)
            about_card.append(row)

            if i < len(ABOUT_INFO) - 1:
                sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                sep.set_margin_start(16)
                about_card.append(sep)

        self.body.append(about_card)

        # Actions section
        def build_action(spec):
            emoji, color, label, summary, cb = spec
            return make_row(emoji, color, label, summary, on_tap=cb)

        actions = [
            ('🔄', '#34aadc', 'Software Update', f'Uptime: {self.bridge.uptime}',  self.bridge.checkUpdate),
            ('💽', '#8e8e93', 'Disk Mode',        'Mount as USB storage',           self.bridge.enterDiskMode),
            ('🔧', '#ff3b30', 'Recovery Mode',    'Reboot into recovery',           self.bridge.enterRecovery),
        ]
        self.body.append(make_section('Actions', actions, build_action))
