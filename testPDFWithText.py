import fitz
import pandas as pd
import re

def parsedate(str_with_date):
    date_pattern = r'\d{2}\.\d{2}\.\d{4}'

    match = re.search(date_pattern, str_with_date)
    if match:
        date = match.group()
        return date
    return None

file = "./resources/input.pdf"

pages_df = pd.DataFrame(columns=['text'])

with fitz.open(file) as doc:
    for page in doc: print("page %i" % page.number)

doc = fitz.open(file)

extraction_pdfs = {}
arr = []

for page_num in range(doc.page_count):
    page = doc.load_page(page_num)
    spl = page.get_text('text').split('\n')
    arr.extend(spl)
    # print(spl)
    s1 = pd.DataFrame(spl, columns=['text'])
    # print(s1)
    pages_df = pd.concat([pages_df, s1], ignore_index=True)

extraction_pdfs[file] = pages_df

for line in arr:
    # print(line)
    if "Дата поступления образца" in line:
        print(parsedate(line))
