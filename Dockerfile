FROM python:3.12-slim

WORKDIR /app

# Install git for publish functionality
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
