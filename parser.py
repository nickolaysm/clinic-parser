import os
import fitz
import re

# Библиотека ищет в заданном каталоге pdf файлы от ЭндоМедЛаб с текстом
# Вытаскивает текст pdf и складывает результаты анализов в pandas DataFrame
# Колонки:
# "Название анализа" "Дата анализа 1" "Дата анализа 2" ... "Референсное значение"
# К колонках "Дата анализа х" собственно сами значения анализов по датам

READABLE_PDF_PATH = "./readablepdf/"

def parsedate(str_with_date):
    date_pattern = r'\d{2}\.\d{2}\.\d{4}'

    match = re.search(date_pattern, str_with_date)
    if match:
        date = match.group()
        return date
    return None

TABLE_IDENT = ["Тест", "Результат", "Ед. изм.", "Референсные значения", "Откл."]
# Разбирает один pdf
# Возвращает dic где ключем является дата взятия анализов, а значением массив из анализов
def open_pdf(file_path):
    doc = fitz.open(file_path)
    text = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        spl = page.get_text('text').split('\n')
        text.extend(spl)
    print(text)


    is_find_table = False
    date = None
    for line in text:
        if "Дата поступления образца" in line:
            date = parsedate(line)
        if any(head in line for head in TABLE_IDENT):
            #Нашли заголовки таблиц
            is_find_table = True
            print("нашли таблицу")
        elif is_find_table:
            None
            #Значит заголовок закончился, пора парсить саму таблицу

    # разбор таблиц


# Разбирает все pdf лежащие по пути и превращает их в DataFrame
def convert_pdf(path_from):
    pdf_list = [READABLE_PDF_PATH+name for name in os.listdir(path=READABLE_PDF_PATH) if name.lower().endswith('.pdf')]

    for file in pdf_list:
        date_analiz_dic = open_pdf(file)


open_pdf(READABLE_PDF_PATH+"6912578239 (Антиоксиданты и ПОЛ).pdf")