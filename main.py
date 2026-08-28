from __future__ import annotations

from dataclasses import dataclass
import os
import sys
from typing import Optional

PHONE_PREVIEW = "--phone" in sys.argv
if PHONE_PREVIEW:
    os.environ["KIVY_NO_ARGS"] = "1"

from kivy.app import App  # pyright: ignore[reportMissingImports]
from kivy.clock import Clock  # pyright: ignore[reportMissingImports]
from kivy.core.window import Window  # pyright: ignore[reportMissingImports]
from kivy.graphics import Color, Line, RoundedRectangle  # pyright: ignore[reportMissingImports]
from kivy.metrics import dp  # pyright: ignore[reportMissingImports]
from kivy.properties import NumericProperty, StringProperty  # pyright: ignore[reportMissingImports]
from kivy.animation import Animation  # pyright: ignore[reportMissingImports]
from kivy.uix.boxlayout import BoxLayout  # pyright: ignore[reportMissingImports]
from kivy.uix.button import Button  # pyright: ignore[reportMissingImports]
from kivy.uix.floatlayout import FloatLayout  # pyright: ignore[reportMissingImports]
from kivy.uix.label import Label  # pyright: ignore[reportMissingImports]
from kivy.uix.textinput import TextInput  # pyright: ignore[reportMissingImports]
from kivy.uix.widget import Widget  # pyright: ignore[reportMissingImports]


@dataclass
class CaptureSettings:
    delay: float = 3.0
    exposure: float = 1.0
    interval: float = 10.0
    number: int = 24


class PanelBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.055, 0.075, 0.105, 0.72)
            self.background = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            Color(0.17, 0.22, 0.28, 1)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=1)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.background.pos = self.pos
        self.background.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))


class DraggablePanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._drag_offset = (0, 0)
        with self.canvas.before:
            Color(0.055, 0.075, 0.105, 0.72)
            self.background = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            Color(0.17, 0.22, 0.28, 1)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=1)
        self.bind(pos=self._sync_background, size=self._sync_background)

    def _sync_background(self, *_):
        self.background.pos = self.pos
        self.background.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))

    def on_touch_down(self, touch):
        drag_strip = self.top - dp(24)
        if self.collide_point(*touch.pos):
            handled = super().on_touch_down(touch)
            if handled and touch.y < drag_strip:
                return True
            if not handled or touch.y >= drag_strip:
                self._drag_offset = (touch.x - self.x, touch.y - self.y)
                touch.grab(self)
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            parent = self.parent
            if parent:
                self.x = min(max(0, touch.x - self._drag_offset[0]), parent.width - self.width)
                self.y = min(max(0, touch.y - self._drag_offset[1]), parent.height - self.height)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class Crosshair(Widget):
    accent = (0.95, 0.14, 0.18, 1)
    tap_alpha = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*self.accent)
            self.ring = Line(circle=(self.center_x, self.center_y, dp(26)), width=dp(2))
            self.horizontal = Line(points=(self.x, self.center_y, self.right, self.center_y), width=dp(2))
            self.vertical = Line(points=(self.center_x, self.y, self.center_x, self.top), width=dp(2))
            Color(1, 0.28, 0.28, 1)
            self.dot = RoundedRectangle(pos=(self.center_x - dp(4), self.center_y - dp(4)), size=(dp(8), dp(8)), radius=[dp(4)])
            self.tap_color = Color(1, 0.3, 0.3, 0.0)
            self.tap_ring = Line(circle=(self.center_x, self.center_y, dp(34)), width=dp(3))
        self.bind(pos=self._sync, size=self._sync)
        self.bind(tap_alpha=self._sync_tap)

    def _sync(self, *_):
        self.ring.circle = (self.center_x, self.center_y, dp(26))
        self.horizontal.points = (self.x, self.center_y, self.right, self.center_y)
        self.vertical.points = (self.center_x, self.y, self.center_x, self.top)
        self.dot.pos = (self.center_x - dp(4), self.center_y - dp(4))
        self.tap_ring.circle = (self.center_x, self.center_y, dp(34))

    def _sync_tap(self, *_):
        self.tap_color.a = self.tap_alpha

    def begin_hold(self):
        Animation.cancel_all(self, "tap_alpha")
        self.tap_alpha = 0.85
        hold_animation = Animation(tap_alpha=0.45, duration=0.7, t="in_out_sine") + Animation(tap_alpha=0.85, duration=0.7, t="in_out_sine")
        hold_animation.repeat = True
        hold_animation.start(self)

    def end_hold(self):
        Animation.cancel_all(self, "tap_alpha")
        Animation(tap_alpha=0, duration=0.18, t="out_quad").start(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class IntervalometerRoot(FloatLayout):
    status = StringProperty("READY / TAP TARGET TO TEST")
    count_text = StringProperty("00 / 5")
    elapsed_text = StringProperty("00:00")
    total_text = StringProperty("TOTAL 00:12")
    running = False
    shot_count = 0
    elapsed = 0.0
    _shot_event: Optional[object] = None
    _clock_event: Optional[object] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = CaptureSettings()
        self._build_ui()
        self.bind(size=self._adapt_layout)
        Clock.schedule_once(self._adapt_layout, 0)

    def _label(self, text, size=14, color=(0.68, 0.74, 0.8, 1), **kwargs):
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        return Label(text=text, font_size=dp(size), color=color, **kwargs)

    def _build_ui(self):
        self.add_widget(Widget())
        self.crosshair = Crosshair(size_hint=(None, None), size=(dp(88), dp(88)), pos=(dp(260), dp(250)))
        self.add_widget(self.crosshair)

        self.panel = DraggablePanel(orientation="vertical", size_hint=(None, None), size=(dp(240), dp(286)), pos=(dp(24), dp(96)), padding=(dp(8), dp(8)), spacing=dp(3))
        content = BoxLayout(orientation="vertical", padding=(dp(3), dp(2)), spacing=dp(3))
        content.add_widget(self._label("PLACE CROSS ON SHUTTER", size=9, color=(0.72, 0.77, 0.83, 1), size_hint_y=None, height=dp(18)))

        self.inputs = {}
        self.field_base_colors = {}
        for key, label, value, suffix in (("delay", "DELAY", "3", "sec"), ("exposure", "LONG", "1", "sec"), ("interval", "INTERVAL", "2", "sec"), ("number", "NUMBER", "5", "shots")):
            row = BoxLayout(size_hint_y=None, height=dp(29), spacing=dp(5))
            row.add_widget(self._label(label, size=9, color=(0.61, 0.68, 0.76, 1), size_hint_x=None, width=dp(70)))
            field = TextInput(text=value, multiline=False, input_filter="float" if key != "number" else "int", font_size=dp(13), size_hint_x=None, width=dp(70), foreground_color=(0.92, 0.95, 0.98, 1), background_color=(0.1, 0.13, 0.18, 0.82), padding=(dp(6), dp(4)))
            self.inputs[key] = field
            self.field_base_colors[key] = field.background_color
            field.bind(text=self._update_total_from_inputs)
            row.add_widget(field)
            row.add_widget(self._label(suffix, size=10, color=(0.4, 0.48, 0.57, 1), size_hint_x=None, width=dp(38)))
            content.add_widget(row)

        actions = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(54), spacing=dp(3), padding=(0, dp(2), 0, 0))
        start = Button(text="START", size_hint_x=None, width=dp(104), font_size=dp(11), background_normal="", background_color=(0.89, 0.18, 0.18, 1), color=(1, 1, 1, 1), pos_hint={"center_x": 0.5})
        stop = Button(text="STOP", size_hint_x=None, width=dp(104), font_size=dp(11), background_normal="", background_color=(0.19, 0.24, 0.3, 1), color=(0.86, 0.89, 0.93, 1), pos_hint={"center_x": 0.5})
        start.bind(on_release=lambda *_: self.start_sequence())
        stop.bind(on_release=lambda *_: self.stop_sequence())
        actions.add_widget(start)
        actions.add_widget(stop)
        content.add_widget(actions)
        self.status_label = self._label(self.status, size=10, color=(0.94, 0.42, 0.32, 1), size_hint_y=None, height=dp(18))
        content.add_widget(self.status_label)
        info_row = BoxLayout(size_hint_y=None, height=dp(20))
        self.count_label = self._label(self.count_text, size=11, color=(0.9, 0.93, 0.96, 1))
        self.elapsed_label = self._label(self.elapsed_text, size=11, color=(0.55, 0.63, 0.71, 1), halign="right")
        info_row.add_widget(self.count_label)
        info_row.add_widget(self.elapsed_label)
        content.add_widget(info_row)
        self.total_label = self._label(self.total_text, size=10, color=(0.6, 0.68, 0.76, 1), size_hint_y=None, height=dp(18))
        content.add_widget(self.total_label)
        self.panel.add_widget(content)
        self.add_widget(self.panel)
        self.bind(status=self._refresh_footer, count_text=self._refresh_footer, elapsed_text=self._refresh_footer, total_text=self._refresh_footer)

    def _adapt_layout(self, *_):
        phone = self.width < dp(600)
        if phone:
            self.panel.width = min(dp(240), self.width - dp(24))
            self.panel.x = (self.width - self.panel.width) / 2
            self.panel.y = dp(92)
        else:
            self.panel.width = dp(240)
            self.panel.x = dp(24)
            self.panel.y = dp(96)

    def _refresh_footer(self, *_):
        if hasattr(self, "status_label"):
            self.status_label.text = self.status
            self.count_label.text = self.count_text
            self.elapsed_label.text = self.elapsed_text
            self.total_label.text = self.total_text

    def _format_duration(self, seconds):
        total_seconds = max(0, int(round(seconds)))
        return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"

    def _update_total(self):
        spacing = max(self.settings.interval, self.settings.exposure)
        total = self.settings.delay + self.settings.exposure + max(0, self.settings.number - 1) * spacing
        self.total_text = f"TOTAL {self._format_duration(total)}"

    def _read_settings(self):
        def number(key, fallback, minimum):
            try:
                value = float(self.inputs[key].text.strip())
                return max(minimum, value)
            except (ValueError, TypeError):
                return fallback
        self.settings = CaptureSettings(number("delay", 3, 0), number("exposure", 1, 0.1), number("interval", 2, 0.5), int(number("number", 5, 1)))

    def _update_total_from_inputs(self, *_):
        self._read_settings()
        self._update_total()

    def _highlight_field(self, key):
        self._clear_highlights()
        field = self.inputs.get(key)
        if field is None:
            return
        base = self.field_base_colors[key]
        pulse = Animation(background_color=(0.34, 0.10, 0.12, 0.95), duration=0.8) + Animation(background_color=base, duration=0.8)
        pulse.repeat = True
        pulse.start(field)
        self.active_field = key

    def _clear_highlights(self):
        for key, field in self.inputs.items():
            Animation.cancel_all(field, "background_color")
            field.background_color = self.field_base_colors[key]
        self.active_field = None

    def start_sequence(self):
        if self.running:
            return
        self._read_settings()
        self._update_total()
        self._highlight_field("delay")
        self.running = True
        self.shot_count = 0
        self.elapsed = 0
        self.status = "ARMED / WAITING FOR DELAY"
        self.count_text = f"00 / {self.settings.number:02d}"
        self._clock_event = Clock.schedule_interval(self._tick, 0.1)
        self._shot_event = Clock.schedule_once(self._trigger_shot, self.settings.delay)

    def stop_sequence(self):
        self.running = False
        if self._shot_event:
            self._shot_event.cancel()
        if getattr(self, "_release_event", None):
            self._release_event.cancel()
        if self._clock_event:
            self._clock_event.cancel()
        self.crosshair.end_hold()
        self._clear_highlights()
        self.status = "STOPPED / READY"

    def _tick(self, dt):
        if self.running:
            self.elapsed += dt
            total_seconds = int(self.elapsed)
            self.elapsed_text = f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"

    def _trigger_shot(self, *_):
        if not self.running:
            return
        self.shot_count += 1
        self.status = f"PRESSING {self.shot_count:02d} / TARGET HELD"
        self.count_text = f"{self.shot_count:02d} / {self.settings.number:02d}"
        self._highlight_field("exposure")
        self.crosshair.begin_hold()
        self._release_event = Clock.schedule_once(self._release_shot, self.settings.exposure)
        if self.shot_count >= self.settings.number:
            return
        self._shot_event = Clock.schedule_once(self._trigger_shot, max(self.settings.interval, self.settings.exposure))

    def _release_shot(self, *_):
        if self.running and self.shot_count < self.settings.number:
            self.crosshair.end_hold()
            self._highlight_field("interval")
            self.status = f"WAITING / NEXT TAP IN {self.settings.interval:g} SEC"
        elif self.running:
            self.running = False
            self.crosshair.end_hold()
            self._clear_highlights()
            self.status = "COMPLETE / SEQUENCE FINISHED"
            if self._clock_event:
                self._clock_event.cancel()

if PHONE_PREVIEW:
    Window.size = (412, 915)


class IntervalometerApp(App):
    title = "Night Intervalometer"

    def build(self):
        return IntervalometerRoot()


if __name__ == "__main__":
    IntervalometerApp().run()
