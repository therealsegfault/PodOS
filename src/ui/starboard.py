import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import math

APPS = [
    {'name': 'Music',    'sub': 'Now Playing',     'emoji': '🎵', 'accent': '#ff2d55', 'bg': '#1c1c1e', 'id': 'music'},
    {'name': 'YouTube',  'sub': 'Trending',         'emoji': '▶',  'accent': '#ff0000', 'bg': '#1c1c1e', 'id': 'youtube'},
    {'name': 'Fetch',    'sub': 'System Info',      'emoji': '🐶', 'accent': '#00bcd4', 'bg': '#1c1c1e', 'id': 'fetch'},
    {'name': 'Browser',  'sub': 'Safari-like',      'emoji': '🌐', 'accent': '#007aff', 'bg': '#1c1c1e', 'id': 'browser'},
    {'name': 'Videos',   'sub': 'Library',          'emoji': '🎬', 'accent': '#ff9500', 'bg': '#1c1c1e', 'id': 'videos'},
    {'name': 'Photos',   'sub': 'Camera Roll',      'emoji': '📷', 'accent': '#4cd964', 'bg': '#1c1c1e', 'id': 'photos'},
    {'name': 'Clock',    'sub': 'World Clock',      'emoji': '🕐', 'accent': '#ff9500', 'bg': '#1c1c1e', 'id': 'clock'},
    {'name': 'Settings', 'sub': 'Preferences',      'emoji': '⚙',  'accent': '#8e8e93', 'bg': '#1c1c1e', 'id': 'settings'},
]

CARD_W = 260
CARD_H = 260
SIDE_SCALE = 0.75
SIDE_ANGLE = math.radians(55)   # Y-axis rotation of side cards
REFLECT_H = 80                  # reflection strip height below card


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


class Starboard(Gtk.Box):
    def __init__(self, bridge, flipstack):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.bridge = bridge
        self.flipstack = flipstack
        self.add_css_class('starboard-bg')
        self.set_hexpand(True)
        self.set_vexpand(True)

        self._index = 0
        self._anim_offset = 0.0   # fractional position for smooth scrolling
        self._anim_target = 0.0
        self._anim_ticker = None

        # DrawingArea for the coverflow
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self._draw)
        self.append(self.canvas)

        # Label strip at bottom
        label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        label_box.set_margin_bottom(24)
        label_box.set_halign(Gtk.Align.CENTER)

        self.name_label = Gtk.Label(label=APPS[0]['name'])
        self.name_label.add_css_class('app-label')
        label_box.append(self.name_label)

        self.sub_label = Gtk.Label(label=APPS[0]['sub'])
        self.sub_label.add_css_class('app-sublabel')
        label_box.append(self.sub_label)

        self.append(label_box)

        # Touch/swipe gesture
        swipe = Gtk.GestureSwipe()
        swipe.connect('swipe', self._on_swipe)
        self.canvas.add_controller(swipe)

    # ── Key handling (called by main.py global key handler) ────────────────

    def handle_key(self, keyval, state):
        if keyval == Gdk.KEY_Left:
            self._navigate(-1)
            return True
        if keyval == Gdk.KEY_Right:
            self._navigate(1)
            return True
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._launch_current()
            return True
        return False

    # ── Navigation ─────────────────────────────────────────────────────────

    def _navigate(self, delta):
        new = self._index + delta
        if 0 <= new < len(APPS):
            self._index = new
            self._anim_target = float(new)
            self._start_animation()
            self._update_labels()

    def _on_swipe(self, gesture, vx, vy):
        # vx negative = swipe left = move right in list
        if abs(vx) > abs(vy):
            self._navigate(1 if vx < 0 else -1)

    def _launch_current(self):
        app = APPS[self._index]
        if app['id'] == 'settings':
            from src.apps.settings.settings_app import SettingsApp
            page = SettingsApp(self.bridge, self.flipstack)
            self.flipstack.push(page)
        else:
            print(f"[podOS] launch {app['id']}")
            self.bridge.launchApp(app['id'])

    def _update_labels(self):
        app = APPS[self._index]
        self.name_label.set_label(app['name'])
        self.sub_label.set_label(app['sub'])

    # ── Animation ──────────────────────────────────────────────────────────

    def _start_animation(self):
        if self._anim_ticker is not None:
            return
        self._anim_ticker = GLib.timeout_add(16, self._anim_step)

    def _anim_step(self):
        diff = self._anim_target - self._anim_offset
        # Ease-out: move 22% of remaining distance each frame
        if abs(diff) < 0.005:
            self._anim_offset = self._anim_target
            self._anim_ticker = None
            self.canvas.queue_draw()
            return False  # stop
        self._anim_offset += diff * 0.22
        self.canvas.queue_draw()
        return True  # keep going

    # ── Cairo drawing ──────────────────────────────────────────────────────

    def _draw(self, area, cr, width, height):
        # True black background
        cr.set_source_rgb(0, 0, 0)
        cr.paint()

        cx = width / 2
        # Vertical center for card tops — leave ~80px at bottom for labels
        card_top_y = (height - 80 - CARD_H - REFLECT_H) / 2

        # Draw from back to front: left cards, then right cards, then center
        indices = list(range(len(APPS)))
        # Sort so center draws last (on top)
        def draw_order(i):
            return abs(i - self._anim_offset)
        indices.sort(key=draw_order, reverse=True)

        for i in indices:
            self._draw_card(cr, i, cx, card_top_y)

    def _draw_card(self, cr, i, cx, card_top_y):
        app = APPS[i]
        offset = i - self._anim_offset   # negative = left of center

        # How far in "card widths" is this card from center?
        card_gap = CARD_W * 0.55
        x_center = cx + offset * card_gap

        is_center = abs(offset) < 0.3
        scale = 1.0 if is_center else SIDE_SCALE

        # Fade out cards beyond ±2 positions
        alpha = max(0.0, 1.0 - max(0.0, abs(offset) - 1.5) * 0.7)
        if alpha <= 0:
            return

        # Y-axis perspective skew via Cairo transform
        # We simulate 3D by shearing + scaling the x dimension
        skew_factor = math.cos(SIDE_ANGLE) if not is_center else 1.0
        if offset < 0:
            skew_factor = math.cos(SIDE_ANGLE) if not is_center else 1.0
        effective_w = CARD_W * scale * (skew_factor if not is_center else 1.0)
        effective_h = CARD_H * scale

        x_left = x_center - effective_w / 2
        y_top = card_top_y + (CARD_H - effective_h) / 2  # center vertically

        cr.save()
        cr.translate(x_center, y_top + effective_h / 2)
        cr.scale(scale, scale)

        # Simulate Y-rotation by scaling X
        if not is_center:
            x_compress = math.cos(SIDE_ANGLE)
            cr.scale(x_compress, 1.0)

        cr.translate(-CARD_W / 2, -CARD_H / 2)

        self._paint_card(cr, app, CARD_W, CARD_H, alpha)

        cr.restore()

        # Reflection
        cr.save()
        cr.translate(x_center, y_top + effective_h / 2)
        cr.scale(scale, scale)
        if not is_center:
            cr.scale(math.cos(SIDE_ANGLE), 1.0)
        cr.translate(-CARD_W / 2, CARD_H / 2)
        self._paint_reflection(cr, app, CARD_W, REFLECT_H, alpha)
        cr.restore()

    def _paint_card(self, cr, app, w, h, alpha):
        """Draw a single app card with radial gradient bg + gloss overlay."""
        r = 20  # corner radius

        # Rounded rect clip
        self._rounded_rect(cr, 0, 0, w, h, r)
        cr.clip()

        # Background radial gradient
        br, bg, bb = hex_to_rgb(app['bg'])
        ar, ag, ab = hex_to_rgb(app['accent'])

        grad = cairo.RadialGradient(w * 0.4, h * 0.3, 10, w / 2, h / 2, w * 0.7)
        grad.add_color_stop_rgba(0, ar * 0.6 + br * 0.4, ag * 0.6 + bg * 0.4, ab * 0.6 + bb * 0.4, alpha)
        grad.add_color_stop_rgba(1, br * 0.6, bg * 0.6, bb * 0.6, alpha)
        cr.set_source(grad)
        cr.paint()

        # Emoji icon — centered
        cr.set_source_rgba(1, 1, 1, alpha)
        cr.select_font_face('sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(80)
        ext = cr.text_extents(app['emoji'])
        cr.move_to(w / 2 - ext.width / 2 - ext.x_bearing,
                   h / 2 - ext.height / 2 - ext.y_bearing + 10)
        cr.show_text(app['emoji'])

        # Gloss overlay — top half lighter linear gradient
        gloss = cairo.LinearGradient(0, 0, 0, h * 0.55)
        gloss.add_color_stop_rgba(0,   1, 1, 1, 0.25 * alpha)
        gloss.add_color_stop_rgba(0.5, 1, 1, 1, 0.05 * alpha)
        gloss.add_color_stop_rgba(0.5, 0, 0, 0, 0.0)
        gloss.add_color_stop_rgba(1,   0, 0, 0, 0.0)
        cr.set_source(gloss)
        cr.paint()

        cr.reset_clip()

        # Thin border
        self._rounded_rect(cr, 0.5, 0.5, w - 1, h - 1, r)
        cr.set_source_rgba(1, 1, 1, 0.15 * alpha)
        cr.set_line_width(1)
        cr.stroke()

    def _paint_reflection(self, cr, app, w, h, alpha):
        """Mirror of card fading to black."""
        br, bg, bb = hex_to_rgb(app['bg'])
        ar, ag, ab = hex_to_rgb(app['accent'])

        r = 20
        self._rounded_rect(cr, 0, 0, w, h, r)
        cr.clip()

        # Flip vertically
        cr.save()
        cr.scale(1, -1)
        cr.translate(0, -CARD_H)

        # Same gradient as card but we'll fade it out
        grad = cairo.RadialGradient(w * 0.4, CARD_H * 0.3, 10, w / 2, CARD_H / 2, w * 0.7)
        grad.add_color_stop_rgba(0, ar * 0.6 + br * 0.4, ag * 0.6 + bg * 0.4, ab * 0.6 + bb * 0.4, alpha * 0.5)
        grad.add_color_stop_rgba(1, br * 0.6, bg * 0.6, bb * 0.6, alpha * 0.5)
        cr.set_source(grad)
        cr.paint()
        cr.restore()

        # Fade mask: linear from semi-transparent at top to opaque black
        mask = cairo.LinearGradient(0, 0, 0, h)
        mask.add_color_stop_rgba(0,   0, 0, 0, 0.3)
        mask.add_color_stop_rgba(1,   0, 0, 0, 1.0)
        cr.set_source(mask)
        cr.paint()

        cr.reset_clip()

    @staticmethod
    def _rounded_rect(cr, x, y, w, h, r):
        cr.new_sub_path()
        cr.arc(x + r,     y + r,     r, math.pi,       3 * math.pi / 2)
        cr.arc(x + w - r, y + r,     r, 3 * math.pi/2, 0)
        cr.arc(x + w - r, y + h - r, r, 0,              math.pi / 2)
        cr.arc(x + r,     y + h - r, r, math.pi / 2,   math.pi)
        cr.close_path()
