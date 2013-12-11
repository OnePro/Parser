# coding: utf-8

import MySQLdb


class MyDB():
    def __init__(self):
        self.db = MySQLdb.connect(host='localhost', user='root', passwd = '1111', db='mydb', charset = 'utf8')
        self.cursor = self.db.cursor()

    def closeDB(self, msg_text=""):
        if len(msg_text)>0:
            print msg_text
        self.db.close()



#Получим все записи Maker
def getMakers():
    objMyDB = MyDB()
    try:
        objMyDB.cursor.execute("SELECT idMakerj FROM `mydb`.`Makers`;")
        raw_query = objMyDB.cursor.fetchall()
        maker_in_db = [ idquery[0] for idquery in raw_query]
        return maker_in_db
    except NameError, error_name:
        objMyDB.closeDB(msg_text=error_name)
    finally:
        objMyDB.closeDB()

#Записываем в базу все марки
def writeMaker(list_makers):
    pass

#Записавыем все модели
def writeModels(list_models):
    pass

if __name__ == '__main__':
    list_makers = getMakers()
    for idMakers in list_makers:
        print( "%s" % idMakers)