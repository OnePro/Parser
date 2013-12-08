# coding: utf-8
__author__ = 'freeman'

from grab.spider import Spider, Task
from grab import Grab
import logging
import re
from urllib import urlretrieve
import codecs


list_of_items = []
image_catalog = '/home/freeman/ParserImage/'
list_of_images = []

# Общее задание
class ItemsListResult(Spider):
    initial_urls = ['http://en.bildelsbasen.se/?link=list&ggl=s16&searchmode=1&pc[0]=119100100&page=35']
    base_url = 'http://en.bildelsbasen.se/'

    def task_initial(self, grab, task):

        try:
         # находим ссылки на объявления в тек. странице
         # и передаем их в класс Item
         list_readmore_button = grab.doc.select('//a[@class="Button18Blue"]').selector_list

         for x in list_readmore_button:
             link_to_item = x.node.attrib['href']
             ItemPage = self.base_url+link_to_item
             yield Task('item', url=ItemPage)

         #переходим к след странице
         nextPage = grab.doc.select('//a[@class="invert" and text() = ">>"]')[0].node.attrib['href']
         yield Task('initial', url=nextPage)
        except:
         print ("Vsio")

    # задание на парсинк объявы
    def task_item(self, grab, task):
         #создаем экземпляр класса и парсим его
         item = Item(grab)
         if item.yes_image:
         # создадим словарь из переменных
          item.make_dict()
          url = [x for x in item.url_param]
          itemprop = [x for x in item.item_dict]
          list_of_items.append([item.url_param, item.item_dict, item.image_names])


# класс парсит переданные селекторы и создлает словарь с ключами как имена полей в базе
class Item():
    def __init__(self, grab):
       #вводим переменную которая покажет есть ли картинки на странице
       #если их нет, то тогда парсить страницу не будем
       self.yes_image = False

       #посчитаем сколько у нас картинок. И вернем True есть они есть
       img_list = grab.doc.select('//div[@class="mgnBtmMed"]/a/img/@src').selector_list
       self.yes_image = len(img_list) > 0 # если есть хоть одна, говорим да

        #Если есть картинки будем парсить объяву
       if self.yes_image > 0:

        list_td = grab.doc.select('//div[@class="bgColor4 bdrSldTop2"]//table//tr//td').selector_list
        if len(list_td) > 47: # если на этой странице есть то, что нам надо

            #парсим текст
            temp_list = grab.config['url'].split('=')
            self.url_id = temp_list[len(temp_list)-1]
            self.stock_no = list_td[4].text()
            self.position = list_td[5].text()
            self.quality = list_td[6].text()
            self.model_y = list_td[7].text()
            self.new_code = list_td[12].text()
            self.manufact = list_td[13].text()
            self.manufact_no = list_td[14].text()
            self.orig_no = list_td[15].text()
            self.gearbox =  list_td[38].text()
            self.gearbox_no = list_td[39].text()
            self.engine = list_td[46].text()
            self.engine_no = list_td[47].text()
            self.company_name = grab.doc.select('//div[@class="mgnBtmMed"]//b//a[@class="invert"]').text()
            self.direct_link = grab.doc.select('//p[@class="fntSml mgnBtmMed"]//i').selector_list[0].node.text

            # получаем URL на страницу
            numb_of_tag = grab.doc.select('//div[@class="fntMin fntCap color1Lht"]//a').selector_list
            if len(numb_of_tag) > 0:
                self.full_item_href = numb_of_tag[len(numb_of_tag)-1].node.attrib['href']
                self.url_param = parse_full_URL(self.full_item_href)

            # сохраним картинки
            self.image_search(img_list)


    # процедура заполняет словарь из переменных класса
    def make_dict(self):
        self.item_dict = {'idItem':self.url_id, 'Stockno':self.stock_no, 'Position':self.position, 'Quality':self.quality,
                          'ModelYears':self.model_y, 'NewCode':self.new_code, 'Manufacturer':self.manufact,
                          'ManufacturerNo':self.manufact_no, 'OriginalNo':self.orig_no, 'Gearbox':self.gearbox,
                          'GearboxNo':self.gearbox_no, 'Engine':self.engine, 'EngineCode':self.engine_no,
                          'CompanyInformation':self.company_name, 'DirectLink':self.direct_link}


    def image_search(self, image_list):
        self.result_counter = 1
        self.image_names = []
        for img in image_list:
            img_url = clean_img_url(img.text())
            if img_url != "":
                self.take_image(img_url)

        # В этой функции мы получили результат обработки поиска картинок, но
        # это ещё не сама картинка! Это только список найденных картинок,
        #image_url = grab.xpath_text('//div[@class="b-image"]/a/img/@src')

    def take_image(self, url):
        try:
            #собираем путь к будущей картинке
            path = ''.join([self.url_id, '_', str(self.result_counter), '_', url.rsplit('/',1)[1]])

            # Картинка получена, можно сохранить результат.
            #urlretrieve(url, image_catalog + path)

            #добавляем в список сохраненных картинок
            self.image_names.append(path)
            # Не забудем увеличить счётчик ответов, чтобы
            # следующая картинка записалась в другой файл
            self.result_counter += 1
            list_of_images.append(path)
            #print('download images ' + str(len(list_of_images)))
        except:
            print('Error image saving -' + ' id:'+self.url_id +' url:' +url)




###########################################################################
def clean_img_url(img_url):
    base_url = 'http://en.bildelsbasen.se/'
    pos_width = img_url.find('&width')
    pos_height = img_url.find('&height')
    first_symbol = min(pos_width, pos_height)
    if first_symbol > 0:
        return base_url+img_url[:first_symbol]
    else:
        return ""


# функция парсит URL и возвращает словарь со значениями
def parse_full_URL(url):
    url_param_dict = {}
    url_params = url.split('&')
    for x in url_params:
        if x.find('vc1') == 0: url_param_dict.update({'idMakers':x[4:7]})
        if x.find('vc[0]') == 0: url_param_dict.update({'idGroupModel':x[6:20]})
        if x.find('vcx') == 0: url_param_dict.update({'idModel':x[4:15]})
        if x.find('pc1') == 0: url_param_dict.update({'idPartGroup':x[4:7]})
        if x.find('pc[0]') == 0: url_param_dict.update({'idPart':x[6:20]})
    return url_param_dict

def main():
    bot = ItemsListResult()
    bot.setup_cache(
        backend='mysql',
        database='cache_parser',
        user='root', passwd='1111',
    )
    bot.run()

    file = codecs.open('/home/freeman/items.txt', 'w', 'utf-8')
    for id in range(0, len(list_of_items), 1):
       file.write("%s;" % ";".join(["%s=%s" % (k, v) for k, v in list_of_items[id][0].items()]))
       file.write("%s;" % ";".join(["%s=%s" % (k, v) for k, v in list_of_items[id][1].items()]))
       file.write("%s" % ",".join(["%s" % (v) for v in list_of_items[id][2]]))
       file.write("\n")
    file.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()



