# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install any dependencies you script requires
# Example: RUN pip install -r requirements.txt
RUN pip install boto3

# Install Bandit to scan code for Vulnerabilities
RUN pip install bandit

# Copy the Python script into the container
COPY main.py .

# # Run Bandit
# RUN bandit -r .

# Run the Python script when the container launches
CMD ["python", "main.py"]
