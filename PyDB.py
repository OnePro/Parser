# coding: utf-8
__author__ = 'freeman'

import MySQLdb

def print_all_table(table):
    for x in table:
        print(x[1])

def insert_data_in_table_name(data_to_table):
    try:
     cursor.execute(u"INSERT INTO names VALUES (%s, \'%s\');" % (data_to_table))
     db.commit()
    except NameError, e:
    # print e
     db.rollback()




db = MySQLdb.connect(host='localhost', user='root', passwd = '1111', db='testpy', charset = 'utf8')

cursor = db.cursor()
result = cursor.execute("SELECT * FROM names")

try:
    name = str(raw_input('Введите ваше имя\n'))
    idname = result+1

    insert_data_in_table_name((idname, name))

    rowdata = cursor.fetchall()
    if len(rowdata) > 0:
        print_all_table(rowdata)

finally:

 cursor.close()
 db.close()