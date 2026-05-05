import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import math


class FlipStack(Gtk.Stack):
    """Navigation stack with a Y-axis page-flip animation.

    GTK4's Gtk.Stack supports named transitions; we use SLIDE_LEFT/RIGHT for
    push/pop but override with a custom DrawingArea-based flip for the 350ms
    cubic animation when needed. For simplicity we use GTK_STACK_TRANSITION_TYPE_ROTATE_LEFT/RIGHT
    which approximates the flip effect without requiring a separate Cairo overlay.
    """

    def __init__(self):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        # 350ms cubic-easing flip transition
        self.set_transition_duration(350)
        self.set_transition_type(Gtk.StackTransitionType.ROTATE_LEFT)
        self._pages = []

    def push(self, widget, animate=True):
        name = str(id(widget))
        self.add_named(widget, name)
        if not animate:
            self.set_transition_type(Gtk.StackTransitionType.NONE)
        else:
            self.set_transition_type(Gtk.StackTransitionType.ROTATE_LEFT)
        self.set_visible_child_name(name)
        self._pages.append(widget)

    def pop(self):
        if len(self._pages) <= 1:
            return
        self._pages.pop()
        prev = self._pages[-1]
        self.set_transition_type(Gtk.StackTransitionType.ROTATE_RIGHT)
        self.set_visible_child(prev)
        # Remove the old page after transition completes
        GLib.timeout_add(380, self._cleanup_detached)

    def _cleanup_detached(self):
        visible = self.get_visible_child()
        for page in self.get_pages():
            child = page.get_child()
            if child is not visible and child not in self._pages:
                self.remove(child)
        return False  # don't repeat

    def top(self):
        return self._pages[-1] if self._pages else None
