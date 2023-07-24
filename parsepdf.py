# import libraries
import os
from time import ctime

import ocrmypdf
import pandas as pd
import fitz  # !pip install PyMuPDF

# get pdf files
PATH = "./resources/" #os.getcwd()
PATH_RESULT = os.getcwd()+"/result/"

file_list = [f for f in os.listdir(path=PATH) if f.endswith('.pdf') or f.endswith('.PDF')]

'''
main ocr code, which create new pdf file with OCR_ ahead its origin filename, 
and error messege can be find in error_log
'''
print(file_list)
print(ctime())
error_log = {}
for file in file_list:
    try:
        result = ocrmypdf.ocr(PATH+file, PATH_RESULT+'OCR_' + file, output_type='pdf', skip_text=True, deskew=True)
        print(ctime())
    except Exception as e:
        if hasattr(e, 'message'):
            error_log[file] = e.message
        else:
            error_log[file] = e
        continue

'''
extract OCRed PDF using PyMuPDF and save into a pandas dataframe
'''
ocr_file_list = [f for f in os.listdir(path=PATH_RESULT) if f.startswith('OCR_')]
print("ocr_file_list", ocr_file_list)
# PDF extraction
# informations we want to extract
extraction_pdfs = {}

for file in ocr_file_list:
    # save the results
    pages_df = pages_df = pd.DataFrame(columns=['text'])
    # file reader
    doc = fitz.open(PATH_RESULT+file)
    #TODO: почему-то doc возвращается неинициализированный
    print(os.getcwd())
    print("doc:", doc)
    for page_num in range(doc.pageCount):
        page = doc.loadPage(page_num)
        pages_df = pages_df.append({'text': page.getText('text')}, ignore_index=True)

    extraction_pdfs[file] = pages_df

print(extraction_pdfs)