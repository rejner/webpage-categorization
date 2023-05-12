# WebCat - Webpage Content Analysis Tool

This software is a part of Master's Thesis "Automatic Webpage Content Categorisation and Extraction" by Michal Rein at
Faculty of Information Technology, Brno University of Technology, 2023


# How to run

## Prerequisites

- Docker and Docker Compose (All in one Docker Desktop is recommended)
- Python 3.9 or higher (only for running on Apple Silicon)
- Unix-like terminal capable of running bash scripts (for Windows, Git Bash is recommended)

## Supported platforms
- Linux
- macOS
- Windows

## Running

1. Clone this repository
2. Depending on your system, run one of the following scripts:
    - `run.cpu.sh` - for machines without dedicated NVIDIA GPU (Intel/AMD)
    - `run.gpu.sh` - for machines with dedicated NVIDIA GPU (recommended)
    - `run.apple-silicon.sh` - for Apple Silicon machines (experimental, see below for more info *)
3. Wait for the Docker image to build and the containers to start
4. Open http://localhost:80 in your browser


## Apple Silicon (M1, M2) support

* Due to not existing Pytorch Docker Images for Arm64 architecture with the MPS (Metal Programming Framework) support, the worker service has to run directly on the host machine. This is achieved by running the worker service in a separate Python virtual environment. The worker service is started automatically by the `run.apple-silicon.sh` script. The script also installs the required dependencies into venv environment and starts the rest of the services in Docker containers.
* It is recommended to use this for Apple Silicon chips, as it highly accelerates the inference speed (5x times aprox. compared to running on bare M1).

# How to use

 - For experimenting with the tool, you can use the Interactive Parser tool, which is available through the main menu. This tool accepts raw text input and outputs annotated text with categories and entities. Hypothesis templates, labels and models can be changed directly in the tool.

 - For processing a large number of webpages, you can use the Files Parser tool, which is available through the main menu. This tool accepts a path to HTML file(s) and performs analysis on them.
    - Note, that template needs to be created first, before using this tool. This can be done in the Template Maker tool, which is available through the main menu.
    - Template Maker tool allows for either manual creation of templates or automatic creation using the Template Engine, that uses technologies such as ChatGPT to generate templates from a given webpage. However, this feature requires a OpenAPI key as it is a paid service.

# Project structure

```
.
├── data                              # Put data for processing here
├── migrations                        # Database migrations
├── scripts                           # Helper scripts
├── webcat                            # Main package with the business logic
│   ├── analyzer                      # Module for analyzing webpages
│   │   └── models                    # Models used for analysis
│   ├── db_models                     # Database models
│   ├── model_repository              # Module for storing and loading deep learning models
│   ├── parser                        # Module for parsing webpages and extracting data
│   │   └── parsing_strategy          # Different parsing strategies (e.g. for parsing HTML, CSV, etc.)
│   └── template_engine               # Module for generating templates from webpages
├── webcat_api                        # REST API service
│   └── api                           # API endpoints
│       └── v1
├── webcat_client                     # Frontend client service
│   ├── public                        # Static files
│   └── src                           # Source code
│       ├── components
│       ├── models
│       └── pages
├── .env                              # Environment variables for docker-compose
├── config.py                         # Configuration file for Flask applications - shared
├── alembic.ini                       # Configuration file for Alembic, used for database migrations
├── webcat_scheduler                  # Scheduler service code for worker task management
├── webcat_templates                  # Templates service code for managing templates
├── webcat_worker                     # Worker service code for processing webpages
├── docker-compose.apple-silicon.yaml # Docker Compose file for Apple Silicon
├── docker-compose.cpu.debug.yaml     # Docker Compose file for debugging
├── docker-compose.cpu.yaml           # Docker Compose file for CPU
├── docker-compose.gpu.debug.yaml     # Docker Compose file for debugging
├── docker-compose.gpu.yaml           # Docker Compose file for GPU
├── run.apple-silicon.sh              # Script for running on Apple Silicon
├── run.cpu.sh                        # Script for running on CPU
├── run.gpu.sh                        # Script for running on GPU
└── README.md                         # Project documentation

```
