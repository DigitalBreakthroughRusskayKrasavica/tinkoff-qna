FROM python:3.11-slim

WORKDIR /tinkoff-qna

COPY . .

RUN apt-get update
RUN echo "Y" | apt-get install gcc
RUN apt-get install ffmpeg

RUN pip install .
