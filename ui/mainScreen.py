from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import os

from kivymd.theming import ThemeManager

from ui.utils import KVLoader


class MainScreen(BoxLayout, KVLoader):
    theme_cls = ThemeManager()
    dateWidget = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.loadKV(self, 'mainscreen.kv')

    def after(self, __):
        self.dateWidget = self.ids.dateWidget

    def setDateYears(self, years):
        self.dateWidget.setYears(years)

    def onYear(self, widget, year):
        pass


    def _keyboard_closed(self):
        #self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        #self._keyboard = None
        pass

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'right':
            self.ids.imageWidget.on_right_press()
        elif keycode[1] == 'left':
            self.ids.imageWidget.on_left_press()
        if keycode[1] == 'pagedown':
            self.ids.imageWidget.on_right_press(step=10)
        elif keycode[1] == 'pageup':
            self.ids.imageWidget.on_left_press(step=10)
        if keycode[1] == 'end':
            self.ids.imageWidget.on_right_press(step=101)
        elif keycode[1] == 'home':
            self.ids.imageWidget.on_left_press(step=101)


        return True





