# coding: utf-8
import ResultOfSearch

__author__ = 'freeman'

from grab.spider import Spider, Task
from grab import Grab
import logging
import re
import codecs

# список словарей с ключами

# 'namePartGroup' - группы запчастей
# 'idPartGroup' - код группы запчастей из URL
# 'namePart' - название запчасти
# 'idPart' - код запчасти из URL
# 'namePartsBlock' - имя запчастей Окна(боковые, внутреннее)
parts_list=[]

# Общее задание
class GroupPartsParse(Spider):
    initial_urls = ['http://en.bildelsbasen.se/?link=search&ggl=s13&searchmode=1&vc1=111&vc[0]=111106100&vcx=1538']
    base_url = 'http://en.bildelsbasen.se/'

    def task_initial(self, grab, task):
        try:
         # находим группу запчастей (или узел) и потом бежим по названиюм запчастей,
         # которые относятся к этой группе
         for x in grab.doc.select('//div[@class="padLrg bdrSldAll3 bgColor3 bgGrdBlue"]/ul/li/a').selector_list:
            if x.node.sourceline != 1:
             url_models = x.node.attrib['href']
             yield Task('part', url=self.base_url+url_models)
        except:
         print ("Vsio")

    def task_part(self, grab, task):
        # выбираем названия блоков запчастей из дивов которые находятся на таблицами запчастей
        name_parts_tables = grab.doc.select('//div[@class="pagecontent_full_margin"]')[1].select('./div')[0].select('./div')
        # выбираем группы таблиц в которых содержатся запчасти с название группы (мы их вытащили строчкой выше)
        parts_tables = grab.doc.select('//div[@class="pagecontent_full_margin"]')[1].select('./div')[0].select('./table')
        #Теперь мы можем вытащить запчасти и название блока, в котором находиться запчасти.
        # будем это делать склеивая по индексу выбранные заголовок(блок) и таблицу запчастей под этим блоком
        for id in range(1, len(name_parts_tables),1):
            # получаем табличку блока
            curent_parts_table = parts_tables[id].select('./tr/td/a')

            # бежим по этой табличке и вытаскиваем все ссылки на запчасти
            for elem in curent_parts_table:
                 part_obj = Part()
                 part_obj.block_part_name = name_parts_tables[id].text() # название блока над запчастями
                 part_obj.namePart = elem.node.text
                 part_obj.idPart = get_idPart(elem.node.attrib['href'])
                 # запищем в parts_list. предварительно обработав url и вытащив из него idPartGroup и namePartGroup
                 part_obj.other_url_params = ResultOfSearch.parse_full_URL(task.url)

                 try:
                  part_dict = part_obj.make_part_dict()
                  update_parts_list(part_dict)
                 except:
                  print 'Ошибка при записи объекта'


def get_idPart(url):
    idPart = ''
    # проверим, если вдруг у текущей модели нет какой-то группы запчастей, то url будет другим
    url_params = url.split('&')
    for x in url_params:
      if x.find('pc') == 0:
          idPart = x[3:20]
      if x.find('pc[0]') == 0:
           idPart = x[6:20]
    return idPart

def update_parts_list(part):
    parts_list.append(part)

class Part():
    def make_part_dict(self):
        part_param_dict = {}
        part_param_dict.update({'namePartGroup':self.namePart})
        part_param_dict.update({'idPartGroup':self.other_url_params['idPartGroup']})
        part_param_dict.update({'namePart':self.namePart})
        part_param_dict.update({'idPart':self.idPart })
        part_param_dict.update({'namePartsBlock': self.block_part_name})
        return part_param_dict


def main():
    bot = GroupPartsParse()
    bot.setup_cache(
        backend='mysql',
        database='cache_parser',
        user='root', passwd='1111',
    )
    bot.run()

    # file = codecs.open('/home/freeman/parts.txt', 'w', 'utf-8')
    # for item in parts_list:
    #    file.write("{%s}\n" % ";".join(["%s=%s" % (k, v) for k, v in item.items()]))
    # file.close()
    import DBWorks
    DBWorks.test_write_grupparts_parts(parts_list)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

