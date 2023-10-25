# ML Platform
*********************

## Project Structure

    ├──docs/
    ├── scripts/                <- Utils scripts to automate task
    │   └── create_env.sh
    │   └── deploy.sh
    │   └── helpers.sh
    │   └── run.sh
    │   └── run_test.sh
    │   └── build_docker.sh
    │
    |── src/                    <- Source code for use in this project.
    |   ├── api/                
    |   │   └── views
    │   │   │   └── login.py       <- Module for login user and keep sessions
    │   │   │   └── model_view.py  <- List of endpoints (it only defines them)
    |   │   └── router
    |   ├── core/               <- train models and then use trained models to make predictions
    |   │   └── databricks/     <-  Functions to communicate with DataBricks API
    |   │   └── storage/        <-  Functions to communicate with Azure Storage
    │   │   └── job_thread.py   <- Worker module to run a model in different threads
    │   │   └── models.py       <- Logic module for endpoints (one function per each endpoint)
    |   │
    |   ├── db/                 <- DataBase connections
    |   │
    |   ├── schemas/            <- ORM - Classes with entities used.
    |   │
    |   ├── settings/           <- Config file for API
    |   │
    |   ├── test/               <- Testing module
    |   │
    |   └── main.py             <- Run application
    |
    ├── Dockerfile              <- to build docker image
    ├── requirements.txt        <- Libraries required
    ├── requirements-dev.txt    <- Libraries required for develop
    ├── docker-compose          <- Up API and mongodb
    ├── mkdocs.yml              <- config file for docs 
    ├── LICENSE
    ├── README.md           <- README for developers using this project.
    ├── .gitignore          <- folders and files to exclude for git
    ├── .dockerignore       <- folders and files to exclude for docker context
    ├── .flake8             <- config file for flake8