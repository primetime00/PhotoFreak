import io
import os
from functools import partial

from PIL import Image as PillowImage
from kivy.clock import Clock
from kivy.core.image import ImageData as CoreImageData
from kivy.core.image import Texture
from kivy.graphics.transformation import Matrix
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from .utils import ImageLoader


class ImageWidget(BoxLayout):
    orientation = 'vertical'
    imageList = None
    coreImage = None
    currentPos = 0
    imageAngle = NumericProperty(0)
    imageNumber = StringProperty("")
    imageName = StringProperty("")
    imageLoader = ImageLoader(threads=4)

    reflect = Matrix().scale(0.1,1,1)
    buttonSchedule = None




    def __init__(self, onClick=None, **kwargs):
        tmp = os.getcwd()
        os.chdir('ui')
        Builder.load_file('imagewidget.kv')
        super().__init__(**kwargs)
        self.id = 'image'
        self.onClick = onClick
        os.chdir(tmp)

    def setImageList(self, imageList):
        self.imageList = imageList
        self.currentPos = 0
        self.imageLoader.loadImageList(imageList)
        self.openImage(self.imageList[self.currentPos][3], self.currentPos)
        self.imageName = self.imageList[self.currentPos][4]
        self.imageNumber = "{}/{}".format(self.currentPos + 1, len(self.imageList))

    def on_left_press(self, step=0):
        if self.imageList is not None:
            amount = 1
            if step > 0:
                amount = int(len(self.imageList) * step/100.0)
            self.currentPos -= max(amount, 1)
            if self.currentPos < 0:
                self.currentPos = 0
            if self.buttonSchedule is not None:
                Clock.unschedule(self.buttonSchedule)
                self.buttonSchedule = None
            self.buttonSchedule = Clock.schedule_once(partial(self.openPicture, self.currentPos), 0.1)
            self.imageNumber = "{}/{}".format(self.currentPos + 1, len(self.imageList))
            self.imageName = self.imageList[self.currentPos][4]

    def on_right_press(self, step=0):
        if self.imageList is not None:
            amount = 1
            if step > 0:
                amount = int(len(self.imageList) * step/100.0)
            self.currentPos += max(amount, 1)
            if self.currentPos >= len(self.imageList):
                self.currentPos = len(self.imageList)-1
            if self.buttonSchedule is not None:
                Clock.unschedule(self.buttonSchedule)
                self.buttonSchedule = None
            self.buttonSchedule = Clock.schedule_once(partial(self.openPicture, self.currentPos), 0.1)
            self.imageNumber = "{}/{}".format(self.currentPos + 1, len(self.imageList))
            self.imageName = self.imageList[self.currentPos][4]


    def openPicture(self, *args):
        pos = args[0]
        if pos != self.currentPos:
            return
        self.openImage(self.imageList[self.currentPos][3], self.currentPos)

    def reTryOpen(self, *largs):
        pos = largs[0]
        name = largs[1]
        self.openImage(name, pos)

    def openImage(self, name, pos):
        print(name)
        image = self.imageLoader.getImage(pos)
        if image['status'] != 'loaded':
            print("waiting")
            Clock.schedule_once(partial(self.reTryOpen, pos, name), 0.5)

        else:
            imData = image
            tex = self.get_texture(imData)
            self.ids.image.texture = tex
            if imData['vflip']:
                self.ids.image.texture.flip_vertical()
            if imData['hflip']:
                self.ids.image.texture.flip_horizontal()
            self.imageAngle = imData['angle']

    def get_texture(self, data):
        bt = data['image']
        full = PillowImage.open(io.BytesIO(bt))
        exif_data = full._getexif()
        angle = 0
        vFlip = True
        hFlip = False
        # is there a rotation?
        rotation = 1
        if exif_data is not None and 274 in exif_data:
            rotation = exif_data[274]
        coreImage = CoreImageData(full.size[0], full.size[1], full.mode.lower(), full.tobytes())
        texture = Texture.create_from_data(coreImage)
        if rotation == 2:
            hFlip = True
        elif rotation == 3:
            angle = 180
        elif rotation == 4:
            vFlip = False
        elif rotation == 5:
            hFlip = True
            angle = -270
        elif rotation == 6:
            angle = 90
        elif rotation == 7:
            hFlip = True
            angle = -90
        elif rotation == 8:
            angle = -270
        data['angle'] = angle
        data['vflip'] = vFlip
        data['hflip'] = not hFlip
        return texture










