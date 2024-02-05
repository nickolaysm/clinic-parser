# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim
#FROM mirror.artifactory-jcr.krista.ru/python:3.11

#COPY ./ca_cert/cert.pem /usr/local/share/ca-certificates/

# RUN update-ca-certificates -v
# RUN pip config --global set global.index-url 'https://ntp-nexus3.krista.ru/repository/pypi-all/simple'
# RUN pip config --global set global.cert /usr/local/share/ca-certificates/cert.pem

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "start:app"]
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
