# Pull official base image.
FROM python:3.8-slim-buster

# Prevents Python from writing .pyc files,
# equivalent to python -B.
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and 
# stderr, equivalent to python -u.
ENV PYTHONUNBUFFERED=1

# Set work directory, create if not existing.
WORKDIR /home/app

# Install system dependencies.
# Fix libmysqlclient-dev has no installation candidate:
# libmysqlclient-dev -> default-libmysqlclient-dev,
# specific to Docker.
# RUN apt update \
#     && apt install -y --no-install-recommends \
#         gcc netcat \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies.
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt