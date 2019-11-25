from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.app import App

########################################################################
from ui.utils import KVLoader


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):

    pass

class LabelBox(BoxLayout):
    text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_text(self, instance, value):
        self.ids.label.text = value

    def on_back(self):
        self.parent.on_back()


class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    data = StringProperty()
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def unSelect(self):
        self.selected = False
        self.text = self.data
        pass

    def select(self):
        self.selected = True
        self.text = "[u][color=#0077ffff]{}[/color][/u]".format(self.data)
        self.markup = True
        pass

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)



    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        if isinstance(rv.parent, DateWidget):
            rv.parent.checkItem(self, is_selected)
        if self.parent is not None and rv is not None and rv.parent is not None:
            for c in rv.ids.selectbox.children:
                if isinstance(c, SelectableLabel):
                    c.unSelect()
            rv.parent.onItemSelected(self.data, self, index)


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': ''}]




class DateWidget(BoxLayout, KVLoader):
    orientation = 'vertical'
    YEAR = 1
    MONTH = 2
    heading = ""
    mode = YEAR
    currentYear = 0
    currentMonth = 0

    years = []
    months = []

    _prev_mode = -1

    onYearFunc = ObjectProperty(None)
    onMonthFunc = ObjectProperty(None)
    onBackFunc = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.loadKV(self, 'datewidget.kv')
        super().__init__(**kwargs)
        self.id = 'to'

    def after(self, __):
        self.changeToYear()
        self.ids.heading.ids.back_button.ids.lbl_txt.font_size = 20.0
        self.postMessage(App.get_running_app().REQUEST_YEARS, self)

    def on_data(self, message, data):
        if message == App.get_running_app().REQUEST_YEARS:
            self.years = data
            self.changeToYear()
        elif message == App.get_running_app().REQUEST_MONTHS:
            self.months = data
            self.changeToMonth()

    def checkItem(self, label, selected):
        if self.mode != self.MONTH:
            return
        if selected and self._prev_mode == self.mode:
            label.select()
        else:
            label.unSelect()

    def onItemSelected(self, text: str, label, index):
        _mode_changed = self._prev_mode != self.mode
        self._prev_mode = self.mode
        if self.mode == self.YEAR:
            self.currentYear = -1 if not text.isdigit() else int(text)
            self.mode = self.MONTH if self.currentYear != -1 else self.YEAR
            self.postMessage(App.get_running_app().REQUEST_MONTHS, self, self.currentYear)
            if self.onYearFunc is not None:
                self.onYearFunc(self, self.currentYear)
        elif self.mode == self.MONTH:
            self.currentMonth = text
            if _mode_changed:
                return
            label.select()
            self.postMessage(App.get_running_app().SUBMIT_DATE, self, self.currentYear, self.currentMonth)
            if self.onMonthFunc is not None:
                self.onMonthFunc(self, self.currentYear, self.currentMonth)



    def changeToMonth(self):
        self.mode = self.MONTH
        self.ids.heading.ids.back_button.disabled = False
        self.ids.heading.text = str(self.currentYear)
        self.ids.date.data = [{'text': month, 'data': month} for month in self.months]
        self.ids.date.refresh_from_data()

    def on_back(self):
        for c in self.ids.date.ids.selectbox.children:
            if isinstance(c, SelectableLabel):
                c.unSelect()
        self.changeToYear()

    def changeToYear(self):
        self._prev_mode = -1
        self.mode = self.YEAR
        self.ids.heading.ids.back_button.disabled = True
        self.ids.heading.text = "Select A Year"
        self.ids.date.data = [{'text': str(x), 'data': str(x)} for x in self.years]
        self.ids.date.refresh_from_data()

    def setYears(self, years):
        self.years = years
        self.changeToYear()

    def setMonths(self, months):
        self.months = months
        self.changeToMonth()
