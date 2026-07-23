# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /code
ENV PORT=7779
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7779
CMD ["python", "server.py"]