FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
# It is located in the 'app' folder on your host
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
# This ensures 'app/', 'apprunner.yaml', etc. are present
COPY . .

# Set the environment variable for Flask
ENV PORT=8080

# App Runner listens on the port you define, but we'll expose it for clarity
EXPOSE 8080

# Run the webserver
# We run it as a module or direct path. 
# Since WORKDIR is /app, we point to the webserver file.
CMD ["python", "app/webserver.py"]
