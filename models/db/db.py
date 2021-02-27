from PyQt5.QtSql import *
from PyQt5.QtWidgets import QMainWindow

def PrepareDatabase():
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('models/db/register.db')
    if db.open():
        q = QSqlQuery()
        if (q.prepare("create table if not exists log(id integer primary key autoincrement not null, nomask integer, total integer, date text)")):
            if (q.exec()):
                return True


def SaveLog(nomask,total,date):
    q = QSqlQuery()
    if (q.prepare("insert into log (nomask,total,date) values (" + str(nomask) + "," + str(total) + ",datetime('" + date + "'))")):
        if (q.exec()):
            return True
    else:
        print(q.lastError().text())

