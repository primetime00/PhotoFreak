import sqlite3
from datetime import datetime


class PhotoDB:
    databaseName = "db/photos.db"
    tableName = "photos"
    isOpened = False
    conn = None

    def openDB(self):
        if not self.isOpened:
            self.conn = sqlite3.connect(self.databaseName)
            self.isOpened = True

    def closeDB(self):
        if self.conn is not None:
            self.conn.close()
        self.isOpened = False


    def getYearList(self):
        self.openDB()
        try:
            cursor = self.conn.cursor()
            query = 'SELECT DISTINCT year from ' + self.tableName
            data = cursor.execute(query).fetchall()
            years = []
            for d in data:
                if int(d[0]) == -1:
                    years.append("Unknown")
                else:
                    years.append(str(d[0]))
            return sorted(years)
        except Exception as e:
            print("Error", e)
        finally:
            self.closeDB()

    def getMonths(self, year):
        self.openDB()
        try:
            cursor = self.conn.cursor()
            query = 'SELECT DISTINCT month from ' + self.tableName + ' WHERE year = (?)'
            if not str(year).isdigit():
                year = "-1"
            params = [year]
            data = cursor.execute(query, params).fetchall()
            nList = [datetime.strptime(str(name), "%m").strftime("%B") for name in sorted([x[0] for x in data])]
            return nList
        except Exception as e:
            print("Error", e)
            return []
        finally:
            self.closeDB()

    def getPhotos(self, year, month, limit=-1):
        self.openDB()
        month = "-1" if month is None else str(datetime.strptime(str(month), "%B").strftime("%m"))
        try:
            cursor = self.conn.cursor()
            query = 'SELECT * from ' + self.tableName + ' WHERE year = (?) AND month = (?) ORDER BY day ASC'
            if not str(year).isdigit():
                year = "-1"
                month = "-1"
            params = [year, month]
            data = cursor.execute(query, params).fetchall()
            return data
        except Exception as e:
            print("Error", e)
            return []
        finally:
            self.closeDB()

#db = PhotoDB()
#db.getPhotos("Unknown", None)
