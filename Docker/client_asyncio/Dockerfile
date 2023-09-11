# Use an official Python runtime as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the local package directories to the container
COPY . /app

# Install the required packages
RUN pip install docker -r requirements.txt

# Make port 9001 available to the outside world (based on your code)
EXPOSE 9001

# Define the command to run the server when the container starts
CMD ["python", "client_asyncio.py"]  
