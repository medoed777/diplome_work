FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY='django-insecure-ptr_03x8t0u4i9d7ggr99z!!c3+f71!i95vv77lj=3rhywla0z'

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]