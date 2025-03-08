    FROM python:3.9-slim-buster

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Install FFmpeg
    RUN apt-get update && apt-get install -y ffmpeg

    COPY . .

    CMD python main.py
