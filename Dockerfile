FROM python:3.8-slim-buster

RUN mkdir /blog
COPY requirements.txt /blog
WORKDIR /blog
RUN pip3 install -r requirements.txt

COPY . /blog

RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["sh","./entrypoint.sh"]
