FROM python:3.6
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install --upgrade pip setuptools
RUN pip install -r /requirements.txt
RUN pip install numpy
RUN pip install scipy
RUN pip install scikit-learn

RUN mkdir /src
WORKDIR /src
COPY ./src /src
