FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /document
COPY requirements.txt /document/
RUN apt-get update && \
    apt-get install -y nano && \
    pip install -r requirements.txt
COPY . /document/