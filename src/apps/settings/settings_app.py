"""
Main Settings screen — iOS 6 grouped table view style.

Layout:
  • Fixed header: search bar + title
  • Scrollable body: sections, each a white rounded card
  • Each row: icon square | label + summary | value + chevron OR toggle
"""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

from src.apps.settings.pages.display import DisplayPage
from src.apps.settings.pages.sound import SoundPage
from src.apps.settings.pages.wifi import WifiPage
from src.apps.settings.pages.storage import StoragePage
from src.apps.settings.pages.podos_page import PodOSPage
from src.apps.settings.pages.system_page import SystemPage


# ── Helper widgets ──────────────────────────────────────────────────────────

class ToggleSwitch(Gtk.DrawingArea):
    """iOS 6 style green toggle implemented with Cairo."""

    def __init__(self, active=False, on_change=None):
        super().__init__()
        self.active = active
        self.on_change = on_change
        self.set_content_width(51)
        self.set_content_height(31)
        self.set_draw_func(self._draw)

        click = Gtk.GestureClick()
        click.connect('released', self._on_click)
        self.add_controller(click)

    def _on_click(self, *_):
        self.active = not self.active
        self.queue_draw()
        if self.on_change:
            self.on_change(self.active)

    def _draw(self, area, cr, w, h):
        import cairo, math
        r = h / 2

        # Track
        if self.active:
            cr.set_source_rgb(0.298, 0.851, 0.392)   # #4cd964
        else:
            cr.set_source_rgb(0.898, 0.898, 0.918)   # #e5e5ea

        # Pill shape
        cr.arc(r, r, r, math.pi / 2, 3 * math.pi / 2)
        cr.arc(w - r, r, r, -math.pi / 2, math.pi / 2)
        cr.close_path()
        cr.fill()

        # Border when off
        if not self.active:
            cr.set_source_rgba(0.784, 0.784, 0.8, 1)
            cr.arc(r, r, r - 0.5, math.pi / 2, 3 * math.pi / 2)
            cr.arc(w - r, r, r - 0.5, -math.pi / 2, math.pi / 2)
            cr.close_path()
            cr.set_line_width(1)
            cr.stroke()

        # Thumb
        thumb_x = w - r - 2 if self.active else r + 2
        cr.set_source_rgb(1, 1, 1)
        cr.arc(thumb_x, h / 2, r - 3, 0, 2 * math.pi)
        cr.fill()

        # Thumb shadow
        cr.set_source_rgba(0, 0, 0, 0.2)
        cr.arc(thumb_x, h / 2 + 1, r - 3, 0, 2 * math.pi)
        cr.set_line_width(1)
        cr.stroke()


class IconSquare(Gtk.DrawingArea):
    """Rounded square icon with colored background and emoji."""

    def __init__(self, emoji, color):
        super().__init__()
        self.emoji = emoji
        self.color = color
        self.set_content_width(32)
        self.set_content_height(32)
        self.set_draw_func(self._draw)

    def _draw(self, area, cr, w, h):
        import cairo, math
        r = 7
        # Background
        c = self.color.lstrip('#')
        rgb = tuple(int(c[i:i+2], 16) / 255 for i in (0, 2, 4))
        cr.set_source_rgb(*rgb)
        cr.arc(r, r, r, math.pi, 3 * math.pi / 2)
        cr.arc(w - r, r, r, 3 * math.pi / 2, 0)
        cr.arc(w - r, h - r, r, 0, math.pi / 2)
        cr.arc(r, h - r, r, math.pi / 2, math.pi)
        cr.close_path()
        cr.fill()

        # Emoji
        cr.set_source_rgb(1, 1, 1)
        cr.select_font_face('sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(18)
        ext = cr.text_extents(self.emoji)
        cr.move_to(w / 2 - ext.width / 2 - ext.x_bearing,
                   h / 2 - ext.height / 2 - ext.y_bearing)
        cr.show_text(self.emoji)


def make_row(emoji, color, label, summary, value='', has_toggle=False,
             toggle_state=False, on_toggle=None, on_tap=None):
    """Build one settings row."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    row.set_margin_start(16)
    row.set_margin_end(16)
    row.set_margin_top(10)
    row.set_margin_bottom(10)

    row.append(IconSquare(emoji, color))

    text_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    text_col.set_hexpand(True)

    lbl = Gtk.Label(label=label)
    lbl.set_halign(Gtk.Align.START)
    lbl.add_css_class('settings-label')
    text_col.append(lbl)

    if summary:
        sub = Gtk.Label(label=summary)
        sub.set_halign(Gtk.Align.START)
        sub.add_css_class('settings-secondary')
        text_col.append(sub)

    row.append(text_col)

    if has_toggle:
        toggle = ToggleSwitch(active=toggle_state, on_change=on_toggle)
        row.append(toggle)
    else:
        right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        if value:
            val_lbl = Gtk.Label(label=value)
            val_lbl.add_css_class('settings-value')
            right.append(val_lbl)
        chev = Gtk.Label(label='›')
        chev.add_css_class('settings-chevron')
        right.append(chev)
        row.append(right)

    if on_tap and not has_toggle:
        click = Gtk.GestureClick()
        click.connect('released', lambda *_: on_tap())
        row.add_controller(click)

    return row


def make_section(title, rows_data, builder_fn):
    """Wrap a list of rows in a rounded white card with separators."""
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_margin_start(16)
    box.set_margin_end(16)
    box.set_margin_bottom(8)

    if title:
        hdr = Gtk.Label(label=title.upper())
        hdr.set_halign(Gtk.Align.START)
        hdr.set_margin_start(16)
        hdr.set_margin_bottom(4)
        hdr.set_margin_top(16)
        hdr.add_css_class('settings-section-header')
        box.append(hdr)

    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    card.add_css_class('settings-card')

    for idx, row_spec in enumerate(rows_data):
        row_widget = builder_fn(row_spec)
        card.append(row_widget)
        if idx < len(rows_data) - 1:
            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            sep.set_margin_start(60)
            card.append(sep)

    box.append(card)
    return box


# ── Sub-page base ────────────────────────────────────────────────────────────

class SubPage(Gtk.Box):
    """Base for every settings sub-page: header with back button + scrollable content."""

    def __init__(self, title, flipstack):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.flipstack = flipstack
        self.add_css_class('settings-bg')
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.add_css_class('settings-header')
        header.set_margin_bottom(0)

        back_btn = Gtk.Button(label='‹ Back')
        back_btn.add_css_class('back-button')
        back_btn.connect('clicked', lambda _: self.flipstack.pop())
        header.append(back_btn)

        title_lbl = Gtk.Label(label=title)
        title_lbl.set_hexpand(True)
        title_lbl.add_css_class('settings-title')
        header.append(title_lbl)

        # Spacer to balance back button
        spacer = Gtk.Box()
        spacer.set_size_request(80, -1)
        header.append(spacer)

        self.append(header)

        # Scrollable body
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.body.set_vexpand(True)
        scroll.set_child(self.body)
        self.append(scroll)

    def handle_key(self, keyval, state):
        from gi.repository import Gdk
        if keyval == Gdk.KEY_Escape:
            self.flipstack.pop()
            return True
        return False


# ── Main Settings page ───────────────────────────────────────────────────────

class SettingsApp(Gtk.Box):
    def __init__(self, bridge, flipstack):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.bridge = bridge
        self.flipstack = flipstack
        self.add_css_class('settings-bg')
        self.set_hexpand(True)
        self.set_vexpand(True)

        self._build_ui()

    def _build_ui(self):
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header.add_css_class('settings-header')

        title_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        back_btn = Gtk.Button(label='‹ Home')
        back_btn.add_css_class('back-button')
        back_btn.connect('clicked', lambda _: self.flipstack.pop())
        title_row.append(back_btn)

        title = Gtk.Label(label='Settings')
        title.set_hexpand(True)
        title.add_css_class('settings-title')
        title_row.append(title)

        spacer = Gtk.Box()
        spacer.set_size_request(80, -1)
        title_row.append(spacer)
        header.append(title_row)

        search = Gtk.Entry()
        search.set_placeholder_text('Search')
        search.add_css_class('settings-search')
        search.set_margin_start(16)
        search.set_margin_end(16)
        search.set_margin_top(8)
        search.set_margin_bottom(8)
        header.append(search)

        self.append(header)

        # Scrollable sections
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        sections = [
            ('', [
                ('🖥', '#007aff', 'Display',      'Brightness, Sleep, AOD',  '',   DisplayPage),
                ('🔊', '#ff9500', 'Sound',        'Volume, EQ',              '',   SoundPage),
                ('📶', '#34aadc', 'Connectivity', 'Wi-Fi, Bluetooth',        '',   WifiPage),
                ('💾', '#8e8e93', 'Storage',      'Usage by category',       '',   StoragePage),
            ]),
            ('', [
                ('🎛', '#5856d6', 'podOS',   'Click wheel, Haptics',  '', PodOSPage),
                ('⚙',  '#6d6d72', 'System',  'About, Update',         '', SystemPage),
            ]),
        ]

        for sec_title, rows in sections:
            def make_row_widget(spec, _bridge=self.bridge, _fs=self.flipstack):
                emoji, color, label, summary, value, PageClass = spec
                return make_row(
                    emoji, color, label, summary, value,
                    on_tap=lambda pc=PageClass: self._open_page(pc)
                )
            body.append(make_section(sec_title, rows, make_row_widget))

        scroll.set_child(body)
        self.append(scroll)

    def _open_page(self, PageClass):
        page = PageClass(self.bridge, self.flipstack)
        self.flipstack.push(page)

    def handle_key(self, keyval, state):
        from gi.repository import Gdk
        if keyval == Gdk.KEY_Escape:
            self.flipstack.pop()
            return True
        return False
