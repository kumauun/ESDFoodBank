# Use the Python 3 slim image as the base image
FROM python:3-slim

# Set the working directory for the application
WORKDIR /usr/src/app

# Copy the requirements.txt file from the foodbank folder into the working directory
COPY ../foodbank/requirements.txt ./

# Install the dependencies listed in the requirements.txt file
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the source code for the driver microservice from the foodbank folder into the working directory
COPY ../foodbank/foodbank.py .

# Copy the foodbankUI folder and its contents, including index.html, into the working directory
COPY ./ ./foodbankUI

# Expose the port the application will run on
EXPOSE 8083

# Set the command to start the application
CMD [ "python", "./foodbank.py" ]

