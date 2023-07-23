import camelot

# Так импортируется PyMuPDF 
import sys, fitz

class ConversionBackend(object):
    def convert(self, pdf_path, png_path):
        # Открываем документ
        doc = fitz.open(pdf_path) 
        for page in doc.pages():
            # Переводим страницу в картинку
            pix = page.get_pixmap()  
            # Сохраняем
            pix.save(png_path)


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