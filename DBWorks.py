# coding: utf-8

import MySQLdb


class MyDB():
    def __init__(self):
        self.db = MySQLdb.connect(host='localhost', user='root', passwd = '1111', db='mydb', charset = 'utf8')
        self.cursor = self.db.cursor()

    def closeDB(self, msg_text=""):
        self.db.close()

def insertInDB(sql_query):
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

# функция возвращает список id из таблица по переданному запросу
def get_ids_from_table(query):
    objMyDB = MyDB()
    try:
        objMyDB.cursor.execute(query)
        raw_query = objMyDB.cursor.fetchall()
        ids_in_db = [ idquery[0] for idquery in raw_query]
        return ids_in_db
    except:
        print(str(objMyDB.cursor.messages[0]))
    finally:
        objMyDB.closeDB()

# функция возвращает списко только тех id которых нет в переданном списке
def get_only_new_ids(given_id, query):
    list_ids = get_ids_from_table(query)
    #проверим что вернула функция,
    # если None тогда значит была ошибка в выборке
    if list_ids != None:
        new_ids = [given for given in given_id if not given in list_ids]
    return new_ids


"""******************************************************
MAKERS & MODELS
"""

# проверить и записать в базу нужные записи
def test_write_makers_models(list_of_dicts_maker_and_model):
    # для начала запишим марки, только новые
    pairs_idMaker_nameMaker = getNewMakerForWriteDB(list_of_dicts_maker_and_model) # кортеж пар idMaker и nameMaker
    insert_makers_list_query = getMakersInsertQuery(pairs_idMaker_nameMaker)
    if len(insert_makers_list_query)>0:
        insertInDB(insert_makers_list_query)

    # теперь проверим есть ли новые модели и запишим их
    list_new_models = getNewModelForWriteDB(list_of_dicts_maker_and_model)
    insert_model_list_query = getModelInsertQuery(list_new_models)
    if len(insert_model_list_query)>0:
        insertInDB(insert_model_list_query)

"""
    Записываем в базу MODEL
"""

#
def getNewModelForWriteDB(list_of_dicts_maker_and_model):
    new_Models = []

    dict_idModel_nameModel = {}
    idModel_list_temp = []
    # для начала вытащим из словаря список idModel для проверки на присудствие их в базе
    for elem_list in list_of_dicts_maker_and_model:
        current_idModel = int(elem_list['idModel'])
        current_nameModel = elem_list['nameModel']
        current_idGroupModel = int(elem_list['idGroupModel'])
        current_nameGroupModel = elem_list['nameGroupModel']
        current_idMaker   = int(elem_list['idMaker'])

        idModel_list_temp.append(current_idModel)
        # сразу сформируем словарь которым нам пригодиться для записи новых моделей(если такие найдутся)
        # ключ будет idModel, значение список [idModel, nameModel, idGroupModel, nameGroupModel, idMaker]
        dict_idModel_nameModel.update({current_idModel: (current_idModel, current_nameModel, current_idGroupModel, current_nameGroupModel, current_idMaker) })

    # прогоним через множества и тем самым удалим дубли
    idModel_list = list(set(idModel_list_temp))

    # проверим какие из них новые и их надо записать в базу
    query_for_get_ids = "SELECT idModel FROM `mydb`.`Model`;"
    new_idModel_list = get_only_new_ids(idModel_list, query_for_get_ids)
    for new_idModel in new_idModel_list:
        new_model_attrib = dict_idModel_nameModel[new_idModel]
        new_Models.append(new_model_attrib)

    return new_Models

def getModelInsertQuery(list_models):
    list_query = []
    for model_attr in list_models:
        list_query.append("INSERT Model(idModel, nameModel, idGroupModel, nameGroupModel, idMaker) VALUES (%d, \'%s\', %d, \'%s\', %d);" % model_attr)
    return list_query

"""
    Записываем в базу MAKERS
"""

# Функция формирует список заросов для записи idMaker и nameMaker
def getMakersInsertQuery(list_makers):
    list_query = []
    for pair in list_makers:
        list_query.append("INSERT Makers(idMaker, nameMaker) VALUES (%d, \'%s\');" % pair)
    return list_query

#Функция отбирет только те пары (idMaker и nameMaker) марок, которых ещё нет в базе
# возвращает список пар. Пара - это словарь
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
    query_for_get_ids = "SELECT idMaker FROM `mydb`.`Makers`;"
    new_idMaker_list = get_only_new_ids(idMakers_list, query_for_get_ids)
    for new_idMaker in new_idMaker_list:
        new_pair = dict_idMaker_nameMaker[new_idMaker] #новая пара id и имя марки
        new_idMaker_nameMaker.append(new_pair)

    return new_idMaker_nameMaker

"""**********************************************************
   GROUPPARTS & PARTS
"""

def test_write_grupparts_parts(list_of_dicts_groupparts_and_parts):
    #для начала проверим и запишим группы запчастей, которых ещё нет в базе
    new_groups_parts_list = get_new_group_parts_for_DB(list_of_dicts_groupparts_and_parts)
    queries_gr_list = get_gr_parts_insert_query(new_groups_parts_list)
    if len(queries_gr_list):
       insertInDB(queries_gr_list)

    # теперь проверим есть ли новые запчасти и запишим их
    list_new_parts = get_new_part_from_DB(list_of_dicts_groupparts_and_parts)
    insert_parts_list_query = get_parts_insert_query(list_new_parts)
    if len(insert_parts_list_query)>0:
        insertInDB(insert_parts_list_query)


"""
    Записываем в базу GroupParts
"""

"""
Group parts
"""
def get_new_group_parts_for_DB(list_of_dicts_groupparts_and_parts):
    new_idGrParts_nameGrParts = []

    dict_idGrParts_nameGrParts = {}
    idGrParts_list_temp = []
    # для начала вытащим из словаря список idGrParts для проверки на присудствие их в базе
    for elem_list in list_of_dicts_groupparts_and_parts:
        current_idPartGroup = int(elem_list['idPartGroup'])
        current_namePartGroup = elem_list['namePartGroup']

        idGrParts_list_temp.append(current_idPartGroup)
        # сразу сформируем словарь которым нам пригодиться для записи новых марок(если такие найдутся)
        # ключ будет idGroupPart, значение список [idPartGroup, namePartGroup]
        dict_idGrParts_nameGrParts.update({current_idPartGroup: (current_idPartGroup, current_namePartGroup) })

    # прогоним через множества и тем самым удалим дубли
    idGrParts_list = list(set(idGrParts_list_temp))

    # проверим какие из них новые и их надо записать в базу
    query_for_get_ids = "SELECT idPartGroup FROM mydb.PartGroup;"
    new_idGrParts_list = get_only_new_ids(idGrParts_list, query_for_get_ids)
    for new_idGrPart in new_idGrParts_list:
        new_GrPart_id_name = dict_idGrParts_nameGrParts[new_idGrPart] #новая пара id и имя группы запчастей
        new_idGrParts_nameGrParts.append(new_GrPart_id_name)

    return new_idGrParts_nameGrParts

def get_gr_parts_insert_query(list_gr_parts):
    list_query = []
    for pair in list_gr_parts:
        list_query.append("INSERT PartGroup(idPartGroup, namePartGroup) VALUES (%d, \'%s\');" % pair)
    return list_query

"""
Parts
"""
#отбираем только новые id
def get_new_part_from_DB(list_of_dicts_groupparts_and_parts):
    new_Parts = []

    dict_idPart_name_Part = {}
    idPart_list_temp = []
    # для начала вытащим из словаря список idModel для проверки на присудствие их в базе
    for elem_list in list_of_dicts_groupparts_and_parts:
        current_idPart = int(elem_list['idPart'])
        current_namePart = elem_list['namePart']
        current_idPartGroup = int(elem_list['idPartGroup'])
        current_namePartsBlock = elem_list['namePartsBlock']

        idPart_list_temp.append(current_idPart)
        # сразу сформируем словарь которым нам пригодиться для записи новых моделей(если такие найдутся)
        # ключ будет idPart, значение список [idPart, namePart, idPartGroup, namePartsBlock]
        dict_idPart_name_Part.update({current_idPart: (current_idPart, current_namePart, current_idPartGroup, current_namePartsBlock) })

    # прогоним через множества и тем самым удалим дубли
    idPart_list = list(set(idPart_list_temp))

    # проверим какие из них новые и их надо записать в базу
    query_for_get_ids = "SELECT idPart FROM `mydb`.`Part`;"
    new_idParts_list = get_only_new_ids(idPart_list, query_for_get_ids)
    for new_idPart in new_idParts_list:
        new_part_attrib = dict_idPart_name_Part[new_idPart]
        new_Parts.append(new_part_attrib)

    return new_Parts

#формируем список запросов для MySQL
#
def get_parts_insert_query(list_parts):
    list_query = []
    for part_attr in list_parts:
        list_query.append("INSERT Part(idPart, namePart, idPartGroup, namePartsBlock) VALUES (%d, \'%s\', %d, \'%s\');" % part_attr)
    return list_query
