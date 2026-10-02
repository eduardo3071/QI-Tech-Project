FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY tests ./tests
COPY database ./database
COPY pytest.ini .

CMD ["uvicorn", "src.app:application", "--host", "0.0.0.0", "--port", "8000"]
