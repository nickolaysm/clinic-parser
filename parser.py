import os
import fitz
import re
import camelot

# Библиотека ищет в заданном каталоге pdf файлы от ЭндоМедЛаб с текстом
# Вытаскивает текст pdf и складывает результаты анализов в pandas DataFrame
# Колонки:
# "Название анализа" "Дата анализа 1" "Дата анализа 2" ... "Референсное значение"
# К колонках "Дата анализа х" собственно сами значения анализов по датам

READABLE_PDF_PATH = "./readablepdf/"


class AnalizTable:
    def __init__(self, date, name, value, measure, reference):
        self.date = date
        self.name = name
        self.value = value
        self.measure = measure
        self.reference = reference


class ConversionBackend(object):
    def convert(self, pdf_path, png_path):
        # Открываем документ
        doc = fitz.open(pdf_path)
        for page in doc.pages():
            # Переводим страницу в картинку
            pix = page.get_pixmap()
            # Сохраняем
            pix.save(png_path)


# Возвращает двумерный массив:
# ["Дата", "Тест", "Значение", "Ед. измерения", "Референсное значение"]
def parse_table(analiz_date, file_name):
    tables = camelot.read_pdf(file_name,
                              backend=ConversionBackend(),
                              strip_text='\n',
                              line_scale=30,
                              pages='all',
                              copy_text=['h'],)
    print("===================")
    print(tables)
    array_table = []
    for tbl in tables:
        df = tbl.df
        head_index = list(df.columns)
        head = [df.at[0, value] for value in head_index]
        head_dict = {}
        for i, n in enumerate(head):
            head_dict[head[i]] = i

        print("head_dict")
        print(head_dict)
        print(df)
        for i in range(1, len(df.index)):
            test_name = df.at[i, head_dict["Тест"]] if head_dict.get("Тест", "") != "" else ""
            if test_name != "":
                array_table.append([
                    analiz_date,
                    df.at[i, head_dict["Тест"]] if head_dict.get("Тест", "") != "" else "",
                    df.at[i, head_dict["Результат"]] if head_dict.get("Результат", "") != "" else "",
                    df.at[i, head_dict["Ед. изм."]] if head_dict.get("Ед. изм.", "") != "" else "",
                    df.at[i, head_dict["Референсные значения"]] if head_dict.get("Референсные значения", "") != "" else ""
                ])
    print(array_table)
    return array_table


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
    date = None
    for line in text:
        if "Дата поступления образца" in line:
            date = parsedate(line)
    # разбор таблиц
    return parse_table(date, file_path)


# Разбирает все pdf лежащие по пути и превращает их в DataFrame
def convert_pdf(path_from):
    pdf_list = [READABLE_PDF_PATH+name for name in os.listdir(path=READABLE_PDF_PATH) if name.lower().endswith('.pdf')]

    date_analiz_dic = []
    for file in pdf_list:
        date_analiz_dic.extend(open_pdf(file))
    print(date_analiz_dic)
    return date_analiz_dic

# open_pdf(READABLE_PDF_PATH+"6912578239 (Антиоксиданты и ПОЛ).pdf")
# open_pdf(READABLE_PDF_PATH+"6912580007 (Дисбактериоз).pdf")

convert_pdf(READABLE_PDF_PATH)