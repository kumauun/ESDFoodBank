# Use the Python 3 slim image as the base image
FROM python:3-slim

# Set the working directory for the application
WORKDIR /usr/src/app

# Copy the requirements.txt file into the working directory
COPY requirements.txt .

# Install the dependencies listed in the requirements.txt file
RUN python -m pip install --no-cache-dir -r requirements.txt




# Copy the source code for the restaurant microservice into the working directory
COPY . .



# Expose the port the application will run on
EXPOSE 5000

# Set the command to start the application
CMD [ "python", "./notif2.py" ]
