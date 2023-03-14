FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /docmument
COPY requirements.txt /docmument/
RUN apt-get update && \
    apt-get install -y nano && \
    pip install -r requirements.txt
COPY . /docmument/
