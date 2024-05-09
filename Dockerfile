FROM python:3.8-slim

# Update apt repositories and install curl
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Set a directory for the app
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application
CMD ["python", "./app.py"]

