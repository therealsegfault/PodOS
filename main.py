import sys
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

# Scale up on macOS for dev visibility
if sys.platform == 'darwin':
    os.environ['GDK_SCALE'] = '2'

if sys.platform != 'linux':
    from src.system.mock import SystemBridge
else:
    from src.system.dbus import SystemBridge

from src.ui.starboard import Starboard
from src.ui.flipstack import FlipStack


class PodOSApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.podos.shell')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.bridge = SystemBridge()

        self.win = Gtk.ApplicationWindow(application=app)
        self.win.set_title('podOS')
        self.win.set_default_size(600, 800)
        self.win.set_resizable(False)

        # No window decorations on the actual device
        self.win.set_decorated(False)

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_path = os.path.join(os.path.dirname(__file__), 'src/ui/style.css')
        css_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Root container with true black background
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.add_css_class('root-bg')
        self.win.set_child(root)

        # FlipStack is the navigation container
        self.flipstack = FlipStack()
        root.append(self.flipstack)

        # Starboard is home
        self.starboard = Starboard(self.bridge, self.flipstack)
        self.flipstack.push(self.starboard, animate=False)

        # Global key handler — bypass GTK focus entirely by attaching to root window
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect('key-pressed', self.on_key_pressed)
        # set_propagation_phase CAPTURE means we see keys before any widget
        key_ctrl.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.win.add_controller(key_ctrl)

        self.win.present()

    def on_key_pressed(self, ctrl, keyval, keycode, state):
        """Route arrow keys and Enter to the topmost view in the FlipStack."""
        top = self.flipstack.top()
        if top is None:
            return False
        if hasattr(top, 'handle_key'):
            return top.handle_key(keyval, state)
        return False


def main():
    app = PodOSApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
