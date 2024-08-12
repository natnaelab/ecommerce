FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

RUN chmod +x /code/entrypoint.sh


CMD [ "sh", "/code/entrypoint.sh" ]
