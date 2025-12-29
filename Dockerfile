# Slim Python base
FROM python:3.12-slim

# Workdir inside image
WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY run.py /app/run.py

# Flask env defaults (can be overridden via .env / compose)
ENV FLASK_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose app port
EXPOSE 8000

# Default command (can be overridden by compose)
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "run:app"]