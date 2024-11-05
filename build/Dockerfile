FROM python:3

RUN mkdir /app

COPY entrypoint.sh /app/entrypoint.sh
COPY requirements.txt /app/requirements.txt
COPY halotone2mqtt.py /app/halotone2mqtt.py

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]