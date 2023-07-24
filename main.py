import camelot

# Так импортируется PyMuPDF 
import sys, fitz

#OCR
# import easyocr

#For teaseract
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print(pytesseract.get_languages(config=''))

image_path = "./result/test.jpg"
img = Image.open(image_path)

text = pytesseract.image_to_string(Image.open(image_path), lang='rus')
# print(text)

with open("./result/test.txt", "w", encoding="utf-8") as file:
    file.writelines(text)

# print(pytesseract.image_to_string(Image.open('./result/test.jpg')))

class ConversionBackend(object):
    def convert(self, pdf_path, png_path):
        # Открываем документ
        doc = fitz.open(pdf_path) 
        for page in doc.pages():
            # Переводим страницу в картинку
            pix = page.get_pixmap()  
            # Сохраняем
            pix.save(png_path)

# easyOCR показал себя плохо
# reader = easyocr.Reader(['ru'])
# converter = ConversionBackend()
# converter.convert("./resources/input.pdf", "./result/test.jpg")
# result = reader.readtext('./result/test.jpg')
# print(result)


tables = camelot.read_pdf('./resources/input.pdf', 
                          backend=ConversionBackend(),
                          strip_text='\n', 
                          line_scale=30, 
                          pages='all',
                          copy_text=['h'],)

tables.export('./result/foo.csv', f='csv', compress=False)  # json, excel, html, sqlite
# camelot.plot(tables[0], kind='contour').show()

print(len(tables))

             
i = 0
for tbl in tables:
   tbl.to_json('./result/foo'+str(i)+'.json') 
   i+=1

#tables[0].parsing_report
#tables[0].to_csv('./result/foo.csv') # to_json, to_excel, to_html, to_sqlite
#tables[0].to_json('./result/foo.json')
#tables[0].df # get a pandas DataFrame!