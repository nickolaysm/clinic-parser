# clinic-parser

* Что нужно установить
https://camelot-py.readthedocs.io/en/master/user/install.html
Доп. зависимости
https://camelot-py.readthedocs.io/en/master/user/install-deps.html#install-deps

* Компиляция

Что бы компилировать внутри кристы:
--build-arg PLACE=krista

docker-compose build --build-arg PLACE=krista up -d 

* Интересная статья, где предлагается преобразовывать pdf  в картинку меньшими зависимостями

https://newtechaudit.ru/izvlechenie-tablicz-iz-pdf-s-pomoshhyu-camelot/

Нужно только
<pre>
pip install PyMuPDF
pip install "camelot-py[base]"
</pre>

Под Windows установка через pip так: py -m
<pre>
py -m pip install "camelot-py[base]"
</pre>


* Использование easyOCR
<pre>
pip install torch torchvision torchaudio
pip install easyocr
</pre>

* Нужно задайнгрейдить
<pre>
pip install --force-reinstall -v "Pillow==9.5.0"
</pre>

* Отличная статья про OCR

https://medium.com/social-impact-analytics/extract-text-from-unsearchable-pdfs-for-data-analysis-using-python-a6a2ca0866dd

* Очень подробная и качественная статья как разобрать pdf (текст, изображения, таблицы)

https://habr.com/ru/companies/ruvds/articles/765246/

* Как настроить keycloak и oauthproxy

https://habr.com/ru/articles/779924/


minikube start --vm-driver=hyperv  --no-vtx-check