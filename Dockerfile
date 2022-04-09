#syntax=docker/dockerfile:1.2
ARG BASE_IMAGE=python:3.9.9
FROM ${BASE_IMAGE}
LABEL mainteiner="jaroslav.kramar@datasentics.com"

WORKDIR /app
EXPOSE 5000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN cp /usr/share/zoneinfo/Europe/Prague /etc/localtime

#COPY /etc/model/ /app/model
COPY src/app_web /app/app_web
COPY src/fastai_classificator /app/fastai_classificator
COPY src/cli.py /app/cli.py

CMD [ "./cli.py" ]
