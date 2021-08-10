from PyQt5.QtSql import *
from PyQt5.QtWidgets import QMainWindow

def CreateConn():
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('models/db/register.db')
    return db

def PrepareDatabase():
    db = CreateConn()
    if db.open():
        q = QSqlQuery()
        if (q.prepare("create table if not exists log(id integer primary key autoincrement not null, nomask integer, total integer, date text)")):
            if (q.exec()):
                db.close()
                return True



def SaveLog(nomask,total,date):
    conn = CreateConn()
    if conn.open():
        q = QSqlQuery()
        if (q.prepare("insert into log (nomask,total,date) values (" + str(nomask) + "," + str(total) + ",datetime('" + date + "'))")):
            if (q.exec()):
                conn.close()
                return True
        else:
            print(q.lastError().text())

def GetInfToday(now):
    conn = CreateConn()
    if conn.open():
        q = QSqlQuery()
        if q.prepare("SELECT count(date), sum(nomask), sum(total) FROM log WHERE date(date) = '" + now +"';"):
            if q.exec():
                while q.next():
                   return q.value(0),q.value(1),q.value(2)
                else:
                    return None,None,None
        else:
            return None,None,None
    conn.close()

def GetInfYesterday(yesterday):
    conn = CreateConn()
    if conn.open():
        q = QSqlQuery()
        if q.prepare("SELECT count(date), sum(nomask), sum(total) FROM log WHERE date(date) = '" + yesterday +"';"):
            if q.exec():
                while q.next():
                    return q.value(0),q.value(1),q.value(2)
                else:
                    return None,None,None
        else:
            return None,None,None
    conn.close()

def GetTotals():
    conn = CreateConn()
    if conn.open():
        q = QSqlQuery()
        if q.prepare("SELECT sum(total), sum(nomask) FROM log;"):
            if q.exec():
                while q.next():
                    return q.value(0),q.value(1)
            else:
                return 0
    conn.close()

def GetLastData(day):
    data = []
    conn = CreateConn()
    if conn.open():
        q = QSqlQuery()
        if q.prepare("SELECT sum(nomask),sum(total),date(date) FROM log WHERE date(date) >= '"+day+"' GROUP BY date(date);"):
            if q.exec():
                while q.next():
                    data.append([q.value(0),q.value(1),q.value(2)])
                return data
            else:
                return 0
    conn.close()

def GetInfOneDay(day):
    conn = CreateConn()
    data = []
    if conn.open():
        q = QSqlQuery()
        if q.prepare("SELECT sum(nomask), sum(total), strftime('%H',date) as hour FROM log WHERE date(date) = '" + day + "' GROUP BY strftime('%H',date);"):
            if q.exec():
                while q.next():
                    data.append([q.value(0),q.value(1),q.value(2)]) 
                return data
            else:
                return None,None,None
        else:
            return None,None,None
    conn.close()

def GetDayDataDownload(day):
    conn = CreateConn()
    data = []
    if conn.open():
        q = QSqlQuery()
        if q.prepare("SELECT * FROM log WHERE date(date) = '" + day + "';"):
            if q.exec():
                while q.next():
                    data.append([q.value(0),q.value(1),q.value(2),q.value(3)]) 
                return data
            else:
                return None,None,None
        else:
            return None,None,None
    conn.close()