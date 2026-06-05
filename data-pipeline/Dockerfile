FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use main module (not main.py directly) so imports resolve correctly
CMD ["python", "-m", "app.main"]
