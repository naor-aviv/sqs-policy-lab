# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY main.py .

# Install any dependencies your script requires
# Example: RUN pip install -r requirements.txt
RUN pip install boto3

# Run the Python script when the container launches
CMD ["python", "main.py"]
