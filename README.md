# ROSE-API: Reusable Open-Source Enviromental data management - OGC API

## Introduction:
ROSE-API is an open-source web-based API for exposing and managing environmental data and sensor observations. It uses the power of OGC APIs to provide standardized endpoints for the consumption and management of environmental data produced by sensor networks. Additionally, provides customizable processing capabilities through the OGC API - Processes standard for creating and exposing tailor-made functions for your own data.

ROSE-API implements OGC API - Common (link), OGC API - Features, OGC API - Processes, and the modern OGC API - Environmental Data Retrieval (EDR) standards for providing a state-of-the-art API structure.

Additionally, it uses the OpenAPI standard, so you can publish the API description using Swagger or any OpenAPI parser.

You can see [here]() the presentation of ROSE-API in FOSS4G Europe - Tartu 2024!

## Running ROSE-API:
ROSE-API uses multiple technologies:
- Django: Python-based web server.
- PostgreSQL + PostGIS: (Geospatial) Data Storage.
- Celery: Python-based job scheduler.
- RabbitMQ: Messaging queue for Celery.

Although all the components can be installed locally, it is possible to run one or more components of ROSE-API using Docker. 
The easiest approach for a use-ready instance of ROSE-API is the following:

### Running ROSE-API using Docker:
Assuming you have Docker installed in your machine, follow the steps:

1. Duplicate the file `.env.example` and rename it to `.env`. This file contains the environment variables that control several variables inside Docker. The possible options are listed in the "Docker options" section.

    Change the variable `HOST_OUTPUT_DIR` variable to a folder in the host machine where the results of the processes will be stored.

2. Run the container using the command:
    ```bash
    docker-compose up --build
    ```
    The container contains 3 services: 
    - web: Contains the Django application and the Celery service.
    - db: Contains the PostgreSQL instance with PostGIS.
    - rabbitmq: Contains a RabbitMQ instance as the messaging queue for the Celery service.

    Running the command above will activate all 3 services. 

    Now, ROSE-API will be available in [http://localhost:8000](http://localhost:8000).

    It is also possible to run the db and rabbitmq services individually. To do so, use the command:
    ```bash
    docker-compose up db rabbitmq
    ```

### Running locally:

It is also possible to run ROSE-API locally on your computer. To do so, you must install and run the individual components:

- PostgreSQL with the PostGIS extension.
- RabbitMQ messaging queue.

In case you do not need to use the processing capabilities of ROSE-API, you can skip the installation and configuration of the RabbitMQ component.

It is also possible to run these components using Docker and run the Celery + Django services locally. To do so, run the command:
```bash
docker-compose up db rabbitmq
```

When the PostgreSQL database is configured and the RabbitMQ service is working, it is now possible to run the Celery service and the Django web application locally on your computer.

1. **Creating a Python virtual enviroment and installing dependencies:**

    Assuming Python is installed on your machine, create a virtual environment to install all the dependencies of ROSE-API using the following command:

    ```bash
    python3 -m venv .venv 
    ```

    or 

    ```bash
    python3 -m venv .venv 
    ```

    This will create a virtual environment in the directory `.venv`. If created on the project root, this directory is automatically ignored by git.

    To activate the virtual environment, use the command:

    ```bash
    # For unix-based systems (linux/macos)
    source .venv/bin/activate

    # For Windows systems (PowerShell)
    .\.venv\Scripts\activate
    ```

    Now, install the dependencies using the command:
    ```bash
    pip install -r requirements.txt
    ```

2. **Setting up the local environment file:**

    Locate the file `roseapi/roseapi/.env.django`. This file contains the various environment variables that are necessary for running the Django application and the Celery service locally. Duplicate the file and name it `.env`.

    All the Docker environment options are explained in the Docker Options section.

3. **Running the Celery service:**
    
    Celery is a task queue implementation for Python web applications used to asynchronously execute work outside the HTTP request-response cycle. It is used to execute asynchronous processes according to the OGC API - Processes specification.

    If you are not planning to use the processing capabilities of ROSE-API, you can skip this step.

    To start the Celery service, open a terminal and access the ROSE-API application directory using 
    ```bash
    cd roseapi
    ```

    Then, start the Celery task manager with the command
    ```bash 
    celery -A roseapi worker --loglevel=info
    ```

    This will activate the Celery service, which will remain active until the console is closed or the command cancelled.

4. **Running ROSE-API web service:**

    ROSE-API uses Django to provide its API functionalities. Django is a python-based web framework for creating web applications.

    If you are not already on the `roseapi` directory, access it using the command:

    ```bash
    cd roseapi
    ```

    Before starting the ROSE-API application it is necessary to create the database tables and populate it with example data. To do so, run the following commands:
    ```bash
    python manage.py migrate
    python manage.py setup
    ```

    Now, run the ROSE-API web application with the following command:

    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

    Now the ROSE-API application should be available visiting [http://localhost:8000](http://localhost:8000).

## ROSE-API Features:

ROSE-API provides several capabilities for the management of enviromental data, specially sensor information.

- Dynamic collections: It is possible to create collections using the user interface on the fly. A collection is the equivalent of a layer.

- Related collections: One collection may contain information from other collection. For example, one collection contains the locations and information of monitoring stations, while other contains the sensor readings. With ROSE-API it is possible to take advantage of those relationships between collections and do many types of complex queries based on attributes from a related collection.

## Configuration options:

It is possible to set multiple configuration options through environment variables. To do so, create a file called `.env` in the project root and modify it to set the environment variables. A ready-to-use example environment is available within the file `.env.example`. This file must exist in order to run ROSE-API with Docker.

The configuration options are the following:

- Mandatory variables:
    
    These variables should be provided in the `.env` file in the root of the project if running with Docker, or in the 

    - `DJANGO_SECRET_KEY`: Secret key for the Django application.

    - `BASE_HOST`: The base URL where the service is hosted. This address is added to the whitelist of CSRF trusted origins. 

    - `POSTGRES_HOST`: The hostname where the PostgreSQL DBMS is located.

    - `POSTGRES_PORT`: The exposed port of the PostgreSQL DBMS.

    - `POSTGRES_DB`: The name of the database. When running in Docker, a database with the name specified in this variable will be created.

    - `POSTGRES_USER`: The username of a user with access to the specified database. When running in Docker, a user with this username will be created.

    - `POSTGRES_PASSWORD`: The password for the specified database. When running in Docker, the password specified in this variable will be set.

    - `CELERY_BROKER_URL`: The URL of the RabbitMQ service. This service is used as the Celery broker and is obligatory.

- Optional environment variables:

    - Web component variables:

        - `DEBUG`: Optional override of the Django debug mode. Recommended to be False for production environemnts.

        - `DJANGO_SUPERUSER_USERNAME`: Optional variable that overrides the default username for accessing the administrative interface.

        - `DJANGO_SUPERUSER_PASSWORD`: Optional variable that overrides the default password for accessing the administrative interface.

        - `DJANGO_SUPERUSER_EMAIL`: Optional variable that overrides the default email assigned to the superuser.

        - `HOST_HTTP_WEB_PORT`: The HTTP port exposed by Docker for the web application in the host. By default 

        - `HOST_HTTPS_WEB_PORT`: The HTTPS port exposed by Docker for the web application in the host.

        - `WEB_WORKERS`: ROSE-API web application runs using [gunicorn](https://gunicorn.org/). This variable controls the number of workers that are assinged to running ROSE-API web application in the gunicorn starting command.

        - `WEB_TIMEOUT`: ROSE-API web application runs using [gunicorn](https://gunicorn.org/). This variable controls the gunicorn timeout variable, which is the maximum time that the ROSE-API web application will process a response before sending a timeout.

        - `HOST_OUTPUT_DIR`: This is the directory where the processing results are stored. When using Docker, this folder in the host machine will be connected to a folder inside the Docker container called "results". 

    - Database component variables:
        - `HOST_DB_PORT`: (Docker-only) Port in the host machine where the PostgreSQL database will be available.

    - RabbitMQ component variables:

        - `RABBITMQ_DEFAULT_USER`: Optional variable for overriding the default RabbitMQ admin username.

        - `RABBITMQ_DEFAULT_PASS`: Optional variable for overriding the default RabbitMQ admin password.