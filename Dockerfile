FROM python:3.11-slim

WORKDIR /job_swipe

COPY . /job_swipe

RUN apt-get update

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

EXPOSE 5000

CMD [ "gunicorn", "-w 8", "-t 1800", "-b", "0.0.0.0:5000", "app:app" ]
