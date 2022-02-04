FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["python3"]
CMD ["scraper.py"]