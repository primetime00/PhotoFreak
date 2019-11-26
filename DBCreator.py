import sqlite3
import os
from exif import Image
import exifread
from datetime import datetime
from time import time
import re

#folders = ['E:/Pictures', 'G:/RTS', 'G:/Scatter']
folders = ['G:/Scatter']
extensions = ['.jpg', '.png', '.jpeg']
dbName = 'db/photos.db'
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

     #check filename
    res = regexSearch(name)
    if res is None: #check directory
        res = regexSearch(path)
    return res

def shouldTimeProcess(checkData, path):
    if checkData is None:
        return True
    dirName = os.path.dirname(path)
    if dirName in checkData:
        mTime = int(os.path.getmtime(path))
        checkTime = checkData[dirName]
        if mTime > checkTime:
            return True
        return False
    return True

def firstPass(timeCheck=None):
    processedFiles = 0
    szMap = {}
    nonDupes = []
    duplicate = []
    photoDirectories = set()
    for folder in folders:
        for dirName, subDir, files in os.walk(folder):
            for f in files:
                fname, ext = os.path.splitext(f)
                if ext.lower() in extensions:
                    path = dirName+'/'+f
                    if not shouldTimeProcess(timeCheck, path):
                        photoDirectories.add(os.path.dirname(path))
                        continue
                    fSize = os.path.getsize(path)
                    fmt = "{}".format(fSize)
                    if fmt not in szMap:
                        szMap[fmt] = []
                    sList = szMap[fmt]
                    dupeCheck = False
                    for item in sList:
                        sample1 = None
                        sample2 = None
                        with open(path, 'rb') as file_handle:
                            file_handle.seek(int(fSize / 2))
                            sample1 = file_handle.read(10)
                        with open(item[1], 'rb') as file_handle:
                            file_handle.seek(int(fSize / 2))
                            sample2 = file_handle.read(10)
                        if sample1 == sample2:  # we have a duplicate
                            duplicate.append((path, item[1]))
                            dupeCheck = True
                            break
                    if not dupeCheck:
                        sList.append((fname, path))
                        nonDupes.append((fname, path))
                        photoDirectories.add(os.path.dirname(path))
                    processedFiles += 1
                    if processedFiles % 100 == 0:
                        print("Processed {} images and found {} dupes".format(processedFiles, len(duplicate)))
    return duplicate, nonDupes, photoDirectories

def secondPass(fList):
    dateMap = {}
    duplicate = []
    notFound = []
    found = []
    index = 0
    tSize = len(fList)
    for item in fList:
        if index % 100 == 0:
            print("processing {} of {} files with {} dupes".format(index+1, tSize, len(duplicate)))
        index+=1
        path = item[1]
        name, directory = os.path.basename(path), os.path.dirname(path)
        info = getDateInfo(directory, name)
        if info is None:
            if isDuplicate(name, -1, -1, -1, path, dateMap, duplicate):
                continue
            notFound.append(((-1, -1, -1), name, path))
        else:
            if isDuplicate(name, info[0], info[1], info[2], path, dateMap, duplicate):
                continue
            found.append((info, name, path))
    return found, notFound

def isDuplicate(name, year, month, day, path, dtMap, dup):
    dtFmt = "{}_{}_{}".format(year, month, day)
    fname = os.path.splitext(name)[0]
    if dtFmt not in dtMap:
        dtMap[dtFmt] = []
    for item in dtMap[dtFmt]:
        if fname == item[0] and os.path.dirname(item[1]) not in os.path.dirname(path):
            dup.append((path, item[1]))
            return True
    dtMap[dtFmt].append((fname, path))
    return False


def isDuplicate2(name, year, month, day, path, dtMap, szMap, dup):
    dtFmt = "{}_{}_{}".format(year, month, day)
    fSize = os.path.getsize(path)
    szFmt = "{}".format(fSize)
    fname = os.path.splitext(name)[0]
    if szFmt not in szMap:
        szMap[szFmt] = []
    if dtFmt not in dtMap:
        dtMap[dtFmt] = []
    for item in szMap[szFmt]:
        sample1 = None
        sample2 = None
        with open(path, 'rb') as file_handle:
            file_handle.seek(int(fSize/2))
            sample1 = file_handle.read(10)
        with open(item[1], 'rb') as file_handle:
            file_handle.seek(int(fSize/2))
            sample2 = file_handle.read(10)
        if sample1 == sample2: #we have a duplicate
            dup.append((path, item[1]))
            return True
    szMap[szFmt].append((fname, path))
    for item in dtMap[dtFmt]:
        if fname == item[0] and os.path.dirname(item[1]) not in os.path.dirname(path):
            dup.append((path, item[1]))
            return True
    dtMap[dtFmt].append((fname, path))
    return False


def findPhotos():
    processedFiles = 0
    found = []
    notFound = []
    year_month_map = {}
    size_map = {}
    duplicate = []
    for folder in folders:
        for dirName, subDir, files in os.walk(folder):
            for f in files:
                fname, ext = os.path.splitext(f)
                if ext.lower() in extensions:
                    path = dirName+'/'+f
                    dateInfo = getDateInfo(dirName, f)
                    if dateInfo is None:
                        if isDuplicate(f, -1, -1, -1, path, year_month_map, size_map, duplicate):
                            continue
                        notFound.append((fname, path))
                        continue
                    else:
                        if isDuplicate(f, dateInfo[0], dateInfo[1], dateInfo[2], path, year_month_map, size_map, duplicate):
                            continue
                        found.append((fname, path, dateInfo))
                    processedFiles += 1
                    if processedFiles % 100 == 0:
                        print("Processed {} images".format(processedFiles))

    return found, notFound, duplicate




def createDB():
    if os.path.exists(dbName):
        os.remove(dbName)
    conn = sqlite3.connect('db/photos.db')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE photos
                 (year INTEGER, month INTEGER, day INTEGER, path TEXT UNIQUE, filename TEXT)''')
    c.execute('''CREATE TABLE last_check
                 (path TEXT UNIQUE, timestamp INTEGER)''')

    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def populate(found, notFound, removed, dirs):
    conn = sqlite3.connect(dbName)
    cur = conn.cursor()

    if removed is not None and len(removed) > 0:
        entries = [(x,) for x in removed]
        query = '''delete from photos where path = ?'''
        cur.executemany("DELETE FROM photos WHERE path=?", entries)

    query = '''replace into photos values (?, ?, ?, ?, ?)'''
    for f in found:
        path = f[2]
        data_tuple = (f[0][0], f[0][1], f[0][2], path, f[1])
        cur.execute(query, data_tuple)
    for f in notFound:
        path = f[2]
        data_tuple = (-1, -1, -1, path, f[1])
        cur.execute(query, data_tuple)

    for d in dirs:
        query = '''replace into last_check values (?, ?)'''
        data_tuple = (d, int(time()))
        cur.execute(query, data_tuple)
    conn.commit()
    conn.close()
    print("added {} entries to the database".format(len(found)+len(notFound)))

def checkUpdate():
    if not os.path.exists(dbName):
        return None
    conn = sqlite3.connect(dbName)
    cur = conn.cursor()
    query = '''select * from last_check'''
    cur.execute(query)
    res = cur.fetchall()
    conn.close()
    return dict(res)

def findRemoved():
    conn = sqlite3.connect(dbName)
    cur = conn.cursor()
    query = '''select path from photos'''
    cur.execute(query)
    res = cur.fetchall()
    conn.close()
    removed = []
    for f in res:
        path = f[0]
        if not os.path.exists(path):
            removed.append(path)
    return removed



check = checkUpdate()
if check is None:
    createDB()
removed = findRemoved()
dupe, nondupe, dirs = firstPass(timeCheck=check)
found, notFound = secondPass(nondupe)
populate(found, notFound, removed, dirs)

