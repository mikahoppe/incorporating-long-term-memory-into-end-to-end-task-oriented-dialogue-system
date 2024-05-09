# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Make sure that Poetry is available in PATH
ENV PATH="$PATH:/root/.local/bin"

# Set the working directory in the container
WORKDIR /app

# Set Virtual Environment
RUN python -m venv venv
RUN . ./venv/bin/activate

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set the default command to run your application with watchgod
CMD ["python", "watch.py"]
