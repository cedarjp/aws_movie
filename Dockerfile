FROM python:3.7

RUN apt-get update -y && \
    apt-get install -yq make cmake gcc g++ unzip wget build-essential gcc zlib1g-dev libgl1-mesa-dev \
    libglib2.0-0 libsm6 libxext6 libxrender1 redis-server rsync vim

ENV PYTHONUNBUFFERED 1

WORKDIR /app/
ADD requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

ADD . /app/

RUN mkdir -p /app/static
RUN mkdir -p /app/tmp

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
