### Leveraging Large Language Models for Efficient Retrieval of Electronic Health Records: Incorporating Long-Term Memory into End-to-End Task-Oriented Dialogue System

Python Package that enables Multi-Turn Conversations to use Long-Term Memory.
Disclaimer: This repository is under active development and might therefore change in unforeseeable ways and reasons.

### Prerequisites

What things you need to install the software and how to install them:

- Docker
- Python 
- Poetry for Python dependency management. You can install Poetry by following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).
  
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Running the Application
The whole application is run through Docker.
This starts up a LiteLLM proxy instance, a PostgreSQL database and the actual Python program running the memory pipeline.

For a closer look on what's happening, see the `docker-compose.yml` in the root directory.

```bash
docker compose up
```
