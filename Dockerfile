FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update

COPY ./entrypoint.sh /bin/entrypoint.sh

RUN chmod +x /bin/entrypoint.sh

RUN mkdir /code
WORKDIR /code
ADD ./src /code/
ADD requirements.txt /code

RUN pip install -r requirements.txt