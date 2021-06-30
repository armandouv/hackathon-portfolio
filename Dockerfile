FROM python:3.8-slim-buster

RUN mkdir /portfolio
COPY requirements.txt /portfolio
WORKDIR /portfolio
RUN pip3 install -r requirements.txt

COPY . /portfolio

CMD ["gunicorn", "wsgi:app", "-w 4", "-b 0.0.0.0:80"]
