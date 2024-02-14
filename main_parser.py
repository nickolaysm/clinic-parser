from datetime import datetime
import os
import fitz
import re
import camelot
import pandas as pd
import uuid
import io
from minio import Minio

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

class ParserScript:

    # Возвращает двумерный массив:
    # ["Дата", "Тест", "Значение", "Ед. измерения", "Референсное значение", "Группа анализов"]
    # Группа анализов - некоторое уникальное значение анализов из одного документа, что бы потом можно было вывести вместе
    def parse_table(self, analiz_date, file_name):
        print("=================== parse_table ==============")
        print("===: "+ file_name)
        tables = camelot.read_pdf(file_name,
                                backend=ConversionBackend(),
                                strip_text='\n',
                                line_scale=30,
                                pages='all',
                                copy_text=['h'],)
        # print("===================")
        # print(tables)
        array_table = []
        for tbl in tables:
            df = tbl.df
            head = [df.at[0, value] for value in list(df.columns)]
            # Строим dict что бы знать под каким индексом колонка с каким наименованием
            col_idx = {}
            for i, n in enumerate(head):
                col_idx[head[i]] = i
            
            TEST_NAME_COL = ""
            if(col_idx.get("Тест", "") != ""):
                TEST_NAME_COL = "Тест"
            elif(col_idx.get("Название теста", "") != ""):
                TEST_NAME_COL = "Название теста"

            TEST_REF_COL = ""
            if(col_idx.get("Ед. изм.", "") != ""):
                TEST_REF_COL = "Ед. изм."
            elif(col_idx.get("Интерпретация", "") != ""):
                TEST_REF_COL = "Интерпретация"
            

            # print("head_dict")
            # print(head_dict)
            # print(df)
            # Идем по всей таблице исключая первую запись, т.к. она содержит наименование колонок
            for i in range(1, len(df.index)):                
                test_name = df.at[i, col_idx[TEST_NAME_COL]] if col_idx.get(TEST_NAME_COL, "") != "" else ""
                if test_name != "":
                    array_table.append([
                        analiz_date,
                        test_name,                    
                        df.at[i, col_idx["Результат"]] if col_idx.get("Результат", "") != "" else "",
                        df.at[i, col_idx[TEST_REF_COL]] if col_idx.get(TEST_REF_COL, "") != "" else "",
                        df.at[i, col_idx["Референсные значения"]] if col_idx.get("Референсные значения", "") != "" else ""
                    ])
        print(array_table)
        return array_table

    DATE_FORMAT = '%d.%m.%Y'

    def parsedate(self, str_with_date):
        date_pattern = r'\d{2}\.\d{2}\.\d{4}'
        match = re.search(date_pattern, str_with_date)
        if match:
            date = match.group()
            return datetime.strptime(date, self.DATE_FORMAT)
        return None


    TABLE_IDENT = ["Тест", "Результат", "Ед. изм.", "Референсные значения", "Откл."]

    # Поиск даты поступления образца
    def find_entrance_date(self, doc):
        text = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            spl = page.get_text('text').split('\n')
            text.extend(spl)
        date = None
        for line in text:
            if "Дата поступления образца" in line:
                date = self.parsedate(line)
        return date        
    
    # Разбирает один pdf по локальному пути
    # Возвращает dic где ключем является дата взятия анализов, а значением массив из анализов
    def open_pdf(self, file_path):
        doc = fitz.open(file_path)
        date = self.find_entrance_date(doc)
        print("Дата поступления образца:" + str(date))
        # разбор таблиц
        return self.parse_table(date, file_path)


    # Выкачиваем все документы из minio
    # Начинаем их парсить
    def convert_pdf_from_s3(self):
        # client = Minio("host.docker.internal:9001",
        client = Minio("localhost:9000",
            access_key="KGV9jzIWmf6pa3TJcmp9",
            secret_key="2us5h6X0EeeLdfQ1NNqsmK0UEfCcYIhnPwq6EG6U",
            secure=False,
        )        
        bucket_name = "system"
        objects = client.list_objects(bucket_name)
        pdf_list = []
        for obj in objects:
            print(obj.object_name)
            if(obj.object_name != "output.xlsx"):
                pdf_list.append(obj)                
        
        date_analiz_dic = []
        for pdf in pdf_list:
            try:
                response = client.get_object(bucket_name, pdf.object_name)
                # docbytes = response.data;
                # doc = fitz.open(stream=docbytes)
                # date = self.find_entrance_date(doc)
                # print("Дата поступления образца:" + str(date))
                
                filepath = "./" + pdf.object_name + ".pdf";
                with open(filepath, 'wb') as temp_file:
                    try:
                        temp_file.write(response.data)
                    finally:
                        temp_file.close
                    date_analiz_dic.extend( self.open_pdf(filepath) )
                os.remove(filepath)
            finally:
                response.close()
                response.release_conn()
        return date_analiz_dic
        
    # Разбирает все pdf лежащие по пути и превращает их в DataFrame
    def convert_pdf(self, path_from):
        pdf_list = [READABLE_PDF_PATH+name for name in os.listdir(path=READABLE_PDF_PATH) if name.lower().endswith('.pdf')]

        date_analiz_dic = []
        for file in pdf_list:
            date_analiz_dic.extend(self.open_pdf(file))
        # print(date_analiz_dic)
        return date_analiz_dic
    
    def main(self):

        # open_pdf(READABLE_PDF_PATH+"6912578239 (Антиоксиданты и ПОЛ).pdf")
        # open_pdf(READABLE_PDF_PATH+"6912580007 (Дисбактериоз).pdf")
        
        # date_analiz_dic = self.convert_pdf(READABLE_PDF_PATH)
        date_analiz_dic = self.convert_pdf_from_s3()

        dates_set = set(val[0] for val in date_analiz_dic)
        dates_set = sorted(dates_set)

        #формируем уникальный список тестов сохраняя их порядок, в котором они были прочитаны из таблиц
        test_set = set({});
        test_list = []
        for item in date_analiz_dic:
            if(item[1] not in test_set):
                test_set.add(item[1])
                test_list.append(item[1])

        dates_col = [date.strftime(self.DATE_FORMAT) for date in dates_set]

        cols = dates_col + ["Ед. измерения", "Референсное значение"]

        df = pd.DataFrame(index=test_list, columns=cols)

        for item in date_analiz_dic:
            df.at[item[1], item[0].strftime(self.DATE_FORMAT)] = item[2]
            df.at[item[1], "Ед. измерения"] = item[3]
            df.at[item[1], "Референсное значение"] = item[4]

        # print(df)

        filepath = READABLE_PDF_PATH+'/'+str(uuid.uuid4())+'.xlsx';
        df.to_excel(filepath)
        
        client = Minio("localhost:9000",
            access_key="KGV9jzIWmf6pa3TJcmp9",
            secret_key="2us5h6X0EeeLdfQ1NNqsmK0UEfCcYIhnPwq6EG6U",
            secure=False,
        )
        
        with open(filepath, 'rb') as output_file:
            content = output_file.read()
            client.put_object(
                "system", "output.xlsx", io.BytesIO(content), len(content),
            )
            output_file.close
        os.remove(filepath);



###########################################        
print("start");
parse_script = ParserScript();
parse_script.main();