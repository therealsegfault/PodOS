from gi.repository import Gtk
from src.apps.settings.settings_app import SubPage, make_section, make_row

EQ_PRESETS = ['Flat', 'Bass Booster', 'Bass Reducer', 'Classical', 'Dance',
              'Deep', 'Electronic', 'Hip-Hop', 'Jazz', 'Latin',
              'Loudness', 'Lounge', 'Piano', 'Pop', 'R&B',
              'Rock', 'Small Speakers', 'Spoken Word', 'Treble Booster',
              'Treble Reducer', 'Vocal Booster']


class SoundPage(SubPage):
    def __init__(self, bridge, flipstack):
        super().__init__('Sound', flipstack)
        self.bridge = bridge
        self._build()

    def _build(self):
        # Volume slider card
        vol_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vol_card.set_margin_start(16)
        vol_card.set_margin_end(16)
        vol_card.set_margin_top(16)
        vol_card.add_css_class('settings-card')

        lbl = Gtk.Label(label='Volume')
        lbl.set_halign(Gtk.Align.START)
        lbl.add_css_class('settings-label')
        lbl.set_margin_start(16)
        lbl.set_margin_top(10)
        vol_card.append(lbl)

        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_value(self.bridge.volume)
        slider.set_margin_start(16)
        slider.set_margin_end(16)
        slider.set_margin_bottom(10)
        slider.connect('value-changed', lambda s: self.bridge.setVolume(int(s.get_value())))
        vol_card.append(slider)
        self.body.append(vol_card)

        # EQ section header
        from gi.repository import Gtk as _Gtk
        hdr = _Gtk.Label(label='EQ PRESET')
        hdr.set_halign(_Gtk.Align.START)
        hdr.set_margin_start(32)
        hdr.set_margin_top(16)
        hdr.set_margin_bottom(4)
        hdr.add_css_class('settings-section-header')
        self.body.append(hdr)

        # EQ list card
        eq_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        eq_card.set_margin_start(16)
        eq_card.set_margin_end(16)
        eq_card.add_css_class('settings-card')

        for i, preset in enumerate(EQ_PRESETS):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.set_margin_start(16)
            row.set_margin_end(16)
            row.set_margin_top(10)
            row.set_margin_bottom(10)

            lbl = Gtk.Label(label=preset)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_hexpand(True)
            lbl.add_css_class('settings-label')
            row.append(lbl)

            check = Gtk.Label(label='✓' if preset == self.bridge.eqPreset else '')
            check.add_css_class('accent')
            row.append(check)

            def on_tap(p=preset, c=check):
                self.bridge.setEqPreset(p)
                # Refresh checkmarks — simplest: queue redraw of parent
                for child in eq_card:
                    for w in child:
                        if hasattr(w, 'get_css_classes') and 'accent' in w.get_css_classes():
                            inner_row_lbl = None
                            for ww in child:
                                if hasattr(ww, 'get_label') and 'accent' not in ww.get_css_classes():
                                    inner_row_lbl = ww
                            w.set_label('✓' if (inner_row_lbl and inner_row_lbl.get_label() == p) else '')

            click = Gtk.GestureClick()
            click.connect('released', lambda *_, t=on_tap: t())
            row.add_controller(click)
            eq_card.append(row)

            if i < len(EQ_PRESETS) - 1:
                sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                sep.set_margin_start(16)
                eq_card.append(sep)

        self.body.append(eq_card)
