FROM python:3.11.11-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./setup /app/setup

COPY ./classes /app/classes

COPY ./database /app/database

COPY worker.py /app

ENTRYPOINT ["python", "worker.py"]