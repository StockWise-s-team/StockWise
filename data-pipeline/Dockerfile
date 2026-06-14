FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Pre-install CPU-only PyTorch to avoid heavy CUDA packages (~5.9 GB saved!)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
