FROM python:3.12

ADD main.py .

RUN  pip install fastapi[all] --user