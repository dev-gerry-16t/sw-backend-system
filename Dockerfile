FROM python:3.11-slim

RUN apt-get update && apt-get install -y locales

RUN echo "es_MX.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen

ENV LC_ALL es_MX.UTF-8
ENV LANG es_MX.UTF-8
ENV LANGUAGE es_MX:es

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80","--forwarded-allow-ips", "*"]
