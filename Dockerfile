FROM python:2.7-slim


RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    python-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .  
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["python", "app.py"]