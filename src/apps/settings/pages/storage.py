import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
import cairo
from src.apps.settings.settings_app import SubPage

CATEGORIES = [
    ('Music',    0.38, '#ff2d55'),
    ('Videos',   0.22, '#ff9500'),
    ('Photos',   0.15, '#4cd964'),
    ('Apps',     0.10, '#007aff'),
    ('Other',    0.08, '#8e8e93'),
    ('Free',     0.07, '#e5e5ea'),
]
TOTAL_GB = 16.0


class StorageBar(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_content_height(24)
        self.set_hexpand(True)
        self.set_draw_func(self._draw)

    def _draw(self, area, cr, w, h):
        r = h / 2
        x = 0
        for name, fraction, color in CATEGORIES:
            seg_w = w * fraction
            c = color.lstrip('#')
            rgb = tuple(int(c[i:i+2], 16) / 255 for i in (0, 2, 4))
            cr.set_source_rgb(*rgb)
            cr.rectangle(x, 0, seg_w, h)
            cr.fill()
            x += seg_w

        # Rounded ends via clip
        import math
        cr.set_operator(cairo.OPERATOR_DEST_IN)
        cr.set_source_rgba(1, 1, 1, 1)
        cr.arc(r, r, r, math.pi / 2, 3 * math.pi / 2)
        cr.arc(w - r, r, r, -math.pi / 2, math.pi / 2)
        cr.close_path()
        cr.fill()
        cr.set_operator(cairo.OPERATOR_OVER)


class StoragePage(SubPage):
    def __init__(self, bridge, flipstack):
        super().__init__('Storage', flipstack)
        self._build()

    def _build(self):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.set_margin_start(16)
        card.set_margin_end(16)
        card.set_margin_top(16)
        card.set_margin_bottom(16)
        card.add_css_class('settings-card')

        used_gb = TOTAL_GB * sum(f for _, f, _ in CATEGORIES[:-1])
        summary_lbl = Gtk.Label(label=f'{used_gb:.1f} GB used of {TOTAL_GB:.0f} GB')
        summary_lbl.set_halign(Gtk.Align.CENTER)
        summary_lbl.add_css_class('settings-secondary')
        summary_lbl.set_margin_top(12)
        card.append(summary_lbl)

        bar = StorageBar()
        bar.set_margin_start(16)
        bar.set_margin_end(16)
        bar.set_margin_top(4)
        bar.set_margin_bottom(8)
        card.append(bar)

        for name, fraction, color in CATEGORIES:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.set_margin_start(16)
            row.set_margin_end(16)
            row.set_margin_top(4)
            row.set_margin_bottom(4)

            dot = Gtk.DrawingArea()
            dot.set_content_width(12)
            dot.set_content_height(12)
            c = color.lstrip('#')
            rgb = tuple(int(c[i:i+2], 16) / 255 for i in (0, 2, 4))

            def make_dot_draw(r, g, b):
                def draw(area, cr, w, h):
                    import math
                    cr.set_source_rgb(r, g, b)
                    cr.arc(w/2, h/2, min(w, h)/2, 0, 2*math.pi)
                    cr.fill()
                return draw
            dot.set_draw_func(make_dot_draw(*rgb))

            lbl = Gtk.Label(label=name)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_hexpand(True)
            lbl.add_css_class('settings-label')

            gb_lbl = Gtk.Label(label=f'{fraction * TOTAL_GB:.1f} GB')
            gb_lbl.add_css_class('settings-secondary')

            row.append(dot)
            row.append(lbl)
            row.append(gb_lbl)
            card.append(row)

        self.body.append(card)
