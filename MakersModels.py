# coding: utf-8

from grab.spider import Spider, Task
from grab import Grab
import logging
import re
import codecs
import ResultOfSearch


# список словарей с ключами
# 'idMaker' - код производителя
# 'nameMaker' - имя производителя
# 'idGroupModel' - код группы модели из URL
# 'nameGroupModel' - название группы моделей
# 'idModel' - код модели из URL
# 'nameModel' - имя модели
list_of_models = []

# Общее задание
class MakersParse(Spider):
    initial_urls = ['http://en.bildelsbasen.se/?link=search&ggl=s11&searchmode=1']
    base_url = 'http://en.bildelsbasen.se/'

    def task_initial(self, grab, task):

        try:
         # находим ссылки на марку, и переходим на страницу её моделей
         list_makers_url = []
         for x in grab.doc.select('//a[@class="invert"]').selector_list:
            if x.node.sourceline != 1:
             url_models = x.node.attrib['href']
             self.curent_maker = x.node.text
             yield Task('models', url=self.base_url+url_models+"&sortmodel=1")
        except:
         print ("Vsio")

    def task_models(self, grab, task):
        # Определим название модели
        name_maker = grab.doc.select('//ul[@class="padSml"]/li/strong').text()
        # Выбираем все строки из таблицы "Группа модели" -> "Модель"
        # интерируемся по ним
        list_of_table_models = grab.doc.select('//div[@class="box"]/table/tr')
        i=0
        while i< len(list_of_table_models):
         amount_td = list_of_table_models[i].select(".//td")

      # Проверим если нужная таблица (если 2 колонки, значит она :) )

      # из первой колонки имя "Группа моделей" = name_model_group
      # из второй колонки выбираем список содеражащий ссылки (это и есть ссылки на нужные нам модели).

      # передадим их имя производителя на обработку в функцию.
      # И в ней заполним список словарей list_models:
         if len(amount_td) == 2:
          name_gr_model = list_of_table_models[i].select(".//td")[0].select(".//b").text()
          urls_list = list_of_table_models[i].select(".//td")[1].select(".//a")
          # передаем в функцию
          add_to_list_of_models(self.base_url, urls_list, name_maker, name_gr_model)

         i+=1


#///////////////////
# для каждого url модели создаем словарь с ключами (см. в начале описание list_of_models)
# и записываем все словари в глобальный список list_of_models
def add_to_list_of_models(base_url, urls_list, name_maker, name_gr_model):

    for elem in urls_list:
        url = base_url + elem.node.attrib['href']
        dict_model = ResultOfSearch.parse_full_URL(url);
        dict_model.update({'nameMaker':  name_maker})
        dict_model.update({'nameGroupModel': name_gr_model})
        dict_model.update({'nameModel': elem.text()})
        if len(dict_model) == 6:
            list_of_models.append(dict_model)


def start_parse_makers():
    bot = MakersParse()
    bot.setup_cache(
        backend='mysql',
        database='cache_parser',
        user='root', passwd='1111',
    )
    bot.run()

    file = codecs.open('/home/freeman/result.txt', 'w', 'utf-8')
    for item in list_of_models:
       file.write("{%s}\n" % ";".join(["%s=%s" % (k, v) for k, v in item.items()]))
    file.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    start_parse_makers()

