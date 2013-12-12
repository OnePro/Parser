# coding: utf-8

import MySQLdb


class MyDB():
    def __init__(self):
        self.db = MySQLdb.connect(host='localhost', user='root', passwd = '1111', db='mydb', charset = 'utf8')
        self.cursor = self.db.cursor()

    def closeDB(self, msg_text=""):
        self.db.close()



#Получим все записи Maker
def getMakers():
    objMyDB = MyDB()
    try:
        objMyDB.cursor.execute("SELECT idMaker FROM `mydb`.`Makers`;")
        raw_query = objMyDB.cursor.fetchall()
        maker_in_db = [ idquery[0] for idquery in raw_query]
        return maker_in_db
    except:
        print(str(objMyDB.cursor.messages[0]))
    finally:
        objMyDB.closeDB()

#Записываем в базу все марки
def writeMaker(sql_query):
    if len(sql_query) > 0:
        objMyDB = MyDB()
    try:
        for query in sql_query:
            objMyDB.cursor.execute(query)
        objMyDB.db.commit()
    except:
        objMyDB.db.rollback()
        #print(str(objMyDB.cursor.messages[0]))
    finally:
        objMyDB.closeDB()


#Записавыем все модели
def writeModels(list_models):
    pass

# Функция формирует список заросов для записи idMaker и nameMaker
def getMakersInsertQuery(list_makers):
    list_query = []
    for pair in list_makers:
        list_query.append("INSERT Makers(idMaker, nameMaker) VALUES (%d, \'%s\');" % pair)
    return list_query

#Функция возвращает список марок которых ещё нет в базе
def getNewMakers(given_makers):
    list_makers = getMakers()
    #проверим что вернула функция,
    # если None тогда значит была ошибка в выборке
    if list_makers != None:
        new_makers = [given for given in given_makers if not given in list_makers]
    return new_makers

#Функция отбирет только те пары (idMaker и nameMaker) марок, которых ещё нет в базе
def getNewMakerForWriteDB(list_of_dicts_maker_and_model):
    new_idMaker_nameMaker = []

    dict_idMaker_nameMaker = {}
    idMaker_list_temp = []
    # для начала вытащим из словаря список idMaker для проверки на присудствие их в базе
    for elem_list in list_of_dicts_maker_and_model:
        current_idMaker = int(elem_list['idMaker'])
        current_nameMaker = elem_list['nameMaker']

        idMaker_list_temp.append(current_idMaker)
        # сразу сформируем словарь которым нам пригодиться для записи новых марок(если такие найдутся)
        # ключ будет idMaker, значение список [idMaker, nameMaker]
        dict_idMaker_nameMaker.update({current_idMaker: (current_idMaker, current_nameMaker) })

    # прогоним через множества и тем самым удалим дубли
    idMakers_list = list(set(idMaker_list_temp))

    # проверим какие из них новые и их надо записать в базу
    new_idMaker_list = getNewMakers(idMakers_list)
    for new_idMaker in new_idMaker_list:
        new_pair = dict_idMaker_nameMaker[new_idMaker] #новая пара id и имя марки
        new_idMaker_nameMaker.append(new_pair)

    return new_idMaker_nameMaker

# провеить и записать в базу нужные записи
def test_write_makers_models(list_of_dicts_maker_and_model):
    # для начала запишим марки, только новые
    pairs_idMaker_nameMaker = getNewMakerForWriteDB(list_of_dicts_maker_and_model) # кортеж пар idMaker и nameMaker
    insert_makers_list_query = getMakersInsertQuery(pairs_idMaker_nameMaker)
    if len(insert_makers_list_query)>0:
        writeMaker(insert_makers_list_query)
