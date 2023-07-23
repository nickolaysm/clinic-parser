# clinic-parser

* Что нужно установить
https://camelot-py.readthedocs.io/en/master/user/install.html
Доп. зависимости
https://camelot-py.readthedocs.io/en/master/user/install-deps.html#install-deps


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
