FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY bot/ bot/

EXPOSE 5432

VOLUME /usr/src/app/logs

CMD ["python", "./main.py"]