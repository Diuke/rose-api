# ROSE-API: Reusable Open-Source Enviromental data management - OGC API

## Introduction:
ROSE-API is an open-source web-based API for exposing and managing environmental and sensor data. It uses the power of OGC APIs to provide an standardized API for the consumption and management of environmental data produced by sensor networks. Additionally, provides customizable processing capabilities through the OGC API - Processes standard for creating and exposing tailor-made functions for your own data.

ROSE-API implements OGC API - Common (link), OGC API - Features, OGC API - Processes, and the modern OGC API - Environmental Data Retrieval (EDR) standards for providing a state-of-the-art API structure.

Additionally, it uses OpenAPI standards for exposing a swagger API document that can be consumed by any OpenAPI parser.

** ROSE-API is in beta.

## Running ROSE-API:
ROSE-API uses multiple technologies, in particular for providing its synchronous and asynchronous processing capabilities:
- Celery: Python-based job scheduler.
- RabbitMQ: Messaging queue for Celery.
- PostgreSQL + PostGIS: For storing data.

To run an instance of ROSE-API it is possible to use docker or run the additional dependencies locally. We advise to use the Docker approach.

### Before starting: 
Setup the environment with the .env file.
We provide an example environment file (.env.example) but it is strongly suggested to modify it, as it contains default passwords.

Change the name of the file to .env

### Docker:
Install Docker in your machine and follow the steps:

Run the docker container using the docker-compose.yaml file provided.

Run the command:
```
docker-compose up
```

This command will create a container with all dependencies installed and the ROSE-API server installed. Visit <a href="http://localhost:8080/admin">http://localhost:8080/admin</a> to access the 

If necessary, it is possible to run only the 

### Locally