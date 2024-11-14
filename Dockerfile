# Use an official Ubuntu image as the base image
FROM python:3.10-slim-bookworm

# Set the working directory
WORKDIR /src

# Install system dependencies, including python3-venv
RUN apt-get update && apt-get install -y python3-venv

# Install dependencies and create a virtual environment
RUN python3 -m venv /venv
RUN /venv/bin/pip install --upgrade pip

# Install your requirements
COPY requirements.txt /src/
RUN /venv/bin/pip install -r requirements.txt

# Use the virtual environment's Python interpreter
CMD ["/venv/bin/python", "main.py"]
