ARG PLACE

# Первый этап: подготовка среды
FROM mirror.artifactory-jcr.krista.ru/python:3.11 AS builder

WORKDIR /workdir

COPY ./ca_cert/cert.pem /usr/local/share/ca-certificates/ 

RUN     update-ca-certificates -v &&\
        pip config --global set global.index-url 'https://ntp-nexus3.krista.ru/repository/pypi-all/simple' &&\
        pip config --global set global.cert /usr/local/share/ca-certificates/cert.pem  &&\
        pip config --global set global.trusted-host ntp-nexus3.krista.ru

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Внутренний репозиторий с пакетами
RUN echo "deb http://cascad.krista.ru:9999/debian/ bookworm main" > /etc/apt/sources.list 

RUN apt-get update && apt-get install -y --no-install-recommends gcc 

# Install pip requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps --wheel-dir /workdir/wheels -r requirements.txt


# For more information, please refer to https://aka.ms/vscode-docker-python
#FROM python:3.10-slim
FROM mirror.artifactory-jcr.krista.ru/python:3.11

WORKDIR /workdir

#COPY ./ca_cert/cert.pem /usr/local/share/ca-certificates/

RUN     update-ca-certificates -v &&\
        pip config --global set global.index-url 'https://ntp-nexus3.krista.ru/repository/pypi-all/simple' &&\
        pip config --global set global.cert /usr/local/share/ca-certificates/cert.pem  &&\
        pip config --global set global.trusted-host ntp-nexus3.krista.ru

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
# COPY requirements.txt .
# RUN python -m pip install -r requirements.txt

# WORKDIR /app
COPY . /workdir

# скопировать все необходимые файлы в рабочую папку для сборки образа
COPY --from=builder /workdir/wheels /wheels
# COPY --from=builder /semantic-search/requirements.txt .

# Внутренний репозиторий с пакетами
RUN echo "deb http://cascad.krista.ru:9999/debian/ bookworm main" > /etc/apt/sources.list 

RUN apt-get update

# camelot dependencies
RUN apt-get install libgl1 -y
RUN apt-get install -y --no-install-recommends ghostscript python3-tk ocrmypdf
# tesseract dependencies
RUN apt-get install tesseract-ocr libtesseract-dev tesseract-ocr-rus

RUN pip install --upgrade pip && pip install --no-cache /wheels/*

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /workdir
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "start:app"]
#CMD ["uvicorn", "app.start:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
