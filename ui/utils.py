import os

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.app import App

from kivy.core.image import ImageData as CoreImageData
from kivy.core.image import Texture
from functools import partial


from concurrent.futures import ThreadPoolExecutor
from PIL import Image as PillowImage

class KVLoader:
    def loadKV(self, widget: Widget, file):
        tmp = os.getcwd()
        self.widget = widget
        os.chdir('ui')
        Builder.load_file(file)
        os.chdir(tmp)
        Clock.schedule_once(self.after)
        Clock.schedule_once(self.trigger)

    def trigger(self, __):
        App.get_running_app().dispatch('on_ready', [self])

    def postMessage(self, message, handler, *args):
        Clock.schedule_once(partial(self.pm, message, handler, args))

    def pm(self, *args):
        App.get_running_app().dispatch(args[0], args[0], args[1], args[2])


    def on_data(self, message, data):
        pass

    def after(self, __):
        pass


import time, random

st = 0

class ImageLoader:
    imageList = None
    maxThreads = 4
    allocated = 0
    images = {}
    minLoad = 0
    maxLoad = 0
    loadSize = 256*1000000

    def __init__(self, threads=4):
        self.maxThreads = threads
        self.executer = ThreadPoolExecutor(max_workers=threads)

    def loadImageList(self, imageList):
        self.imageList = imageList
        self.allocated = 0
        self.minLoad = 0
        for i in range(0, len(self.imageList)):
            self.images[str(i)] = {'status': 'not loaded', 'size': os.path.getsize(self.imageList[i][3])}
        self.processImages(0)

    def processImages(self, pos):
        info = self.calcualteImages(pos)
        for i in range(0, info['min']):
            del self.images[str(i)]
            self.images[str(i)] = {'status': 'not loaded', 'size': os.path.getsize(self.imageList[i][3])}
        for i in range(info['max'], len(self.imageList)):
            del self.images[str(i)]
            self.images[str(i)] = {'status': 'not loaded', 'size': os.path.getsize(self.imageList[i][3])}
        self.minLoad = info['min']
        self.maxLoad = info['max']-1
        for i in range(info['min'], info['max']):
            f = self.executer.submit(self.loadImage, i, self.images[str(i)])


    def calcualteImages(self, position):
        allocBefore = 0
        allocAfter = 0
        minPos = 0
        maxPos = len(self.imageList)-1

        numImages = len(self.imageList)
        if numImages % 2 != 0:
            numImages += 1

        for i in range(0, int(numImages/2)):
            bp = position - (i+1)
            if bp >= 0:
                allocBefore += self.images[str(bp)]['size']
                minPos = bp
            ap = position + (i+1)
            if ap < len(self.imageList):
                allocAfter += self.images[str(ap)]['size']
                maxPos = ap
            if allocBefore + allocAfter > self.loadSize:
                break
        return {'min': minPos, 'max': maxPos+1}



    def loadImage(self, pos, imData):
        name = self.imageList[pos][3]
        imData['status'] = 'loading'
        try:
            self.openImage(name, imData)
        except Exception as e:
            imData['status'] = 'error'
            print("ERROR", e)

    def openImage(self, name, imData):
        if imData['status'] == 'loaded':
            print("file {} is already open".format(name))
            return
        with open(name, 'rb') as image_file:
            dt = image_file.read()
            imData['angle'] = 0
            imData['image'] = dt
            imData['vflip'] = False
            imData['hflip'] = False
            imData['status'] = 'loaded'


    def getImage(self, pos):
        if self.minLoad > 0 and pos - self.minLoad <= 10:
            self.processImages(pos)
        elif self.maxLoad+1 < len(self.imageList) and self.maxLoad+1 - pos <= 10:
            self.processImages(pos)
        return self.images[str(pos)]

#v = ImageLoader()
#iList = ["E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-026.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-025.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-024.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-023.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-022.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-021.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-020.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-019.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-018.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-017.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-016.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-015.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-014.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-013.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-012.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-011.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-010.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-009.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-008.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-007.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-006.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-005.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-004.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-003.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-002.JPG", "E:\\Pictures\\2019\\[08-10-19]Gender Reveal\\[08-10-19]Gender Reveal-001.JPG"]
#v.loadImageList(iList, 0)
#im = v.getImage(12)
#print(im)

