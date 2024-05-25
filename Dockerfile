FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install gunicorn
EXPOSE 8081

CMD [ "gunicorn", "-w 4", "-b 0.0.0.0:8081", "app:app" ]
