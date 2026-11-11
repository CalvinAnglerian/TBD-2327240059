FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir boto3 pandas
COPY app.py .

CMD ["python", "app.py"]