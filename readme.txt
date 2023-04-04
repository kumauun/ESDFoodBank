SAVOOD - FOODBANK

This README file contains instructions on how to set up and run the Docker-based project. Please follow the steps outlined below to get started.

Prerequisites

Ensure that you have Docker and Docker Compose installed on your machine before proceeding.

Getting Started

    Open your terminal (or command prompt on Windows).

    Navigate to the directory containing the docker-compose.yml file for this project:

    cd /esdfoodbank

    Build the Docker images:

        docker-compose build

This command will download and build the necessary images for the project. Please be patient, as this process may take a while depending on your internet connection.

Run the Docker containers:

    docker-compose up

    This command will start the containers specified in the docker-compose.yml file. You should see the output logs in your terminal.

Accessing the Application

    Open your preferred web browser.

    Navigate to the following URL: http://localhost:5000

    You should now see the project's web application running on your local machine.

Stopping the Application

    To stop the application, press Ctrl+C in the terminal where the containers are running.

    To remove the containers and their associated resources, run the following command:

    docker-compose down

Additional Information

For more information on using Docker and Docker Compose, please refer to the official documentation:

    Docker Documentation - https://docs.docker.com/
    Docker Compose Documentation - https://docs.docker.com/compose/ 