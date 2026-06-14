FROM python:3.12-slim

# System dependencies for WeasyPrint and psycopg2
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libcairo2 \
    libgirepository1.0-dev \
    fonts-liberation \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings_docker

# Create media directory
RUN mkdir -p /app/media

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
