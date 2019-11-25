import sqlite3
import os
from exif import Image
import exifread
from datetime import datetime
import re

folders = ['E:/Pictures', 'G:/RTS', 'G:/Scatter']
extensions = ['.jpg', '.png', '.jpeg']
today = datetime.now()


def regexSearch(name):
    match = re.search('1[0123456]\d{11}', name)
    if match is not None:
        timestamp = datetime.utcfromtimestamp(int(match.group())/1000)
        return timestamp.year, timestamp.month, timestamp.day
    match = re.search('(20\d\d)(\d\d)(\d\d)', name)
    if match is not None:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    match = re.search('(20\d{2})[_-](\d\d)[_-](\d\d)', name)
    if match is not None:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    match = re.search('(\d{1,2})[_-](\d{1,2})[_-](\d\d\d\d)', name)
    if match is not None:
        return int(match.group(3)), int(match.group(1)), int(match.group(2))
    match = re.search('(\d{1,2})[_-](\d{1,2})[_-](\d\d)', name)
    if match is not None:
        return 2000+int(match.group(3)), int(match.group(1)), int(match.group(2))
    return None


def getDateInfo(path, name):
    with open(path+'/'+name, 'rb') as image_file:
        tags = exifread.process_file(image_file, details=False, stop_tag='DateTimeOriginal')
        if len(tags) > 0 and 'EXIF DateTimeOriginal' in tags:
            dt = tags['EXIF DateTimeOriginal'].values
            tm = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')
            if tm <= today and tm.year > 1996:
                return tm.year, tm.month, tm.day

        # try:
        #     image = Image(image_file)
        #     if image.has_exif and "datetime_original" in dir(image):
        #         dt = image.datetime_original
        #         tm = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')
        #         return tm.year, tm.month, tm.day
        # except MemoryError as e:
        #     print("Failed to open file {}".format(path+'/'+name))

    #check filename
    res = regexSearch(name)
    if res is None: #check directory
        res = regexSearch(path)
    return res

def isDuplicate(name, year, month, day, path, dtMap, dup):
    fmt = "{}_{}_{}".format(year, month, day)
    fname = os.path.splitext(name)[0]
    if fmt not in dtMap:
        dtMap[fmt] = []
    for item in dtMap[fmt]:
        if fname == item[0] and os.path.dirname(item[1]) not in os.path.dirname(path):
            dup.append((path, item[1]))
            return True
    dtMap[fmt].append((fname, path))
    return False


def findPhotos():
    processedFiles = 0
    found = []
    notFound = []
    year_month_map = {}
    duplicate = []
    for folder in folders:
        for dirName, subDir, files in os.walk(folder):
            for f in files:
                fname, ext = os.path.splitext(f)
                if ext.lower() in extensions:
                    path = dirName+'/'+f
                    dateInfo = getDateInfo(dirName, f)
                    if dateInfo is None:
                        if isDuplicate(f, -1, -1, -1, path, year_month_map, duplicate):
                            continue
                        notFound.append((fname, path))
                        continue
                    else:
                        if isDuplicate(f, dateInfo[0], dateInfo[1], dateInfo[2], path, year_month_map, duplicate):
                            continue
                        found.append((fname, path, dateInfo))
                    processedFiles += 1
                    if processedFiles % 100 == 0:
                        print("Processed {} images".format(processedFiles))

    return found, notFound, duplicate




def createDB():
    conn = sqlite3.connect('db/photos.db')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE photos
                 (year INTEGER, month INTEGER, day INTEGER, path TEXT, filename TEXT)''')
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def populate():
    conn = sqlite3.connect('db/photos.db')
    cur = conn.cursor()
    found, notFound, dups = findPhotos()
    query = '''insert into photos values (?, ?, ?, ?, ?)'''
    for f in found:
        data_tuple = (f[2][0], f[2][1], f[2][2], f[1], f[0])
        cur.execute(query, data_tuple)
    for f in notFound:
        data_tuple = (-1, -1, -1, f[1], f[0])
        cur.execute(query, data_tuple)
    conn.commit()
    conn.close()

#createDB()
#populate()
