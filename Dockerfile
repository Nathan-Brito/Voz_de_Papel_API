ENV RENDER=1

FROM python:3.12.2

RUN apt-get update && \
    apt-get install -y tesseract-ocr

RUN tesseract --version


COPY requirements.txt .
RUN pip install -r requirements.txt


COPY . /app
WORKDIR /app


EXPOSE 5000
CMD ["python", "app.py"]
