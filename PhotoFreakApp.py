from kivy.app import App
from kivy.clock import Clock

from PhotoDB import PhotoDB


class PhotoFreakApp(App):
    db = PhotoDB()
    mainScreen = None

    READY = "on_ready"
    REQUEST_YEARS = "on_requestYears"
    REQUEST_MONTHS = "on_requestMonths"
    SUBMIT_DATE = "on_submitDate"

    events = [READY, REQUEST_YEARS, REQUEST_MONTHS, SUBMIT_DATE]

    def __init__(self, **kwargs):
        self.kv_file = "photofreak.kv"
        for evt in self.events:
            self.register_event_type(evt)
        super().__init__(**kwargs)

    def on_ready(self, *args):
        self.mainScreen = self.root

    def on_requestYears(self, *args):
        handler = args[1]
        yearList = self.db.getYearList()
        handler.on_data(args[0], yearList)

    def on_requestMonths(self, *args):
        handler = args[1]
        year = args[2][0]
        months = self.db.getMonths(year)
        handler.on_data(args[0], months)

    def on_submitDate(self, *args):
        year = args[2][0]
        month = args[2][1]
        photoList = self.db.getPhotos(year=year, month=month)

        imageWidget = self.root.ids.imageWidget
        imageWidget.setImageList(photoList)

PhotoFreakApp().run()