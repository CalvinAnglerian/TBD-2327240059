
FROM python:3.12-slim

WORKDIR /app

RUN mkdir -p /app/data

RUN pip install --no-cache-dir pandas pyarrow boto3 cassandra-driver

CMD ["tail", "-f", "/dev/null"]
