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
        if q.prepare("SELECT count(date) FROM log WHERE SUBSTR(date, 9, 2) = '" + now +"';"):
            if q.exec():
                while q.next():
                   return q.value(0)
            else:
                return 0
    conn.close()

def GetInfYesterday(yesterday):
    conn = CreateConn()
    if conn.open():
        q = QSqlQuery()
        if q.prepare("SELECT count(date) FROM log WHERE SUBSTR(date, 9, 2) = '" + yesterday +"';"):
            if q.exec():
                while q.next():
                    return q.value(0)
            else:
                return 0
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