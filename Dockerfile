FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /ws
WORKDIR /ws
COPY . /ws
RUN pip install -r requirements.txt

RUN adduser -D user
USER user