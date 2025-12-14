# 🏀 NBA Hub 🏀 

## 📝 Table of Contents

- [Introduction](#-introduction)
- [Prerequisites](#-prerequisites)
- [Cloning the Repository](#-cloning-the-repository)
- [Running the Project](#-running-the-project)
  - [Option 1: Docker (Recommended)](#option-1-docker-recommended)
  - [Option 2: Vagrant (Virtual Machine)](#option-2-vagrant-virtual-machine)
  - [Option 3: Local Execution with Flask](#option-3-local-execution-with-flask)
- [Running Tests](#-testing)


##  Introduction

**NBA Hub** is a dynamic web application designed for viewing and querying real-time data from the NBA basketball league.

This project aims to provide an intuitive interface for accessing key statistics of teams and players, as well as relevant information about games and the current season. The application is designed to be easily deployable using virtualization and containerization technologies such as **Docker** and **Vagrant**, ensuring a consistent execution environment.



##  Prerequisites

Before proceeding with the download and execution, ensure you have the following software installed on your system, depending on your chosen execution option:

| Requirement | Purpose | Required For |
| :--- | :--- | :--- |
| **Git** | Cloning the repository. | All |
| **Python 3.x** | Local execution (Flask) and dependency installation. | Flask |
| **Docker & Docker Compose** | Building and running the container. | Docker |
| **Vagrant & VirtualBox** | Spinning up the development virtual machine. | Vagrant |


## Cloning the Repository

To get a local copy of the project, open your terminal and execute the following command:

```bash
git clone https://github.com/EGC-G2-M/nba-hub.git
cd nba-hub
```
##  Running the Project

Below are the three methods for running the application, depending on your environment preference.

### Option 1: Docker (Recommended)

Utilizing Docker is the fastest and cleanest way to run the application, as it manages all dependencies and the environment internally, based on the `Dockerfile` and `docker-compose.yml` files in the repository, guaranteeing consistency.

1.  **Build and Run the Container:**
    Ensure you are in the root directory of the repository (`nba-hub`) and execute:

    ```bash
    docker-compose up
    ```

2.  **Access the Application:**
    Once the container is up, the application will be available in your browser at:
    [http://localhost:5000](http://localhost:5000)

3.  **Stop the Container:**
    When you are finished, you can stop and remove the container with:

    ```bash
    docker-compose down
    ```

### Option 2: Vagrant (Virtual Machine)

This option allows you to package a complete and isolated development environment in a virtual machine using VirtualBox, ensuring the host system remains clean.

1.  **Start the Virtual Machine:**
    From the root of the repository, execute:

    ```bash
    vagrant up
    ```
    This will download, configure, and start the virtual machine, installing all necessary dependencies as provisioned in the `Vagrantfile`.

2.  **Access the Application:**
    The application runs inside the VM and is accessed via port forwarding. By default, look for the application at:
    [http://localhost:5000](http://localhost:5000) (Verify the forwarded port in your Vagrant configuration).

3.  **Stop/Destroy the Machine:**
    * To suspend the VM (save state): `vagrant suspend`
    * To stop the VM: `vagrant halt`
    * To completely remove the VM and free up resources: `vagrant destroy`

### Option 3: Local Execution with Flask

If you prefer to run the project directly in your local environment, you must have **Python** and a virtual environment set up.

1.  **Install Dependencies:**
    It is highly recommended to create and activate a virtual environment before installing requirements:

    ```bash
    # 1. Create and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate  # For Linux/macOS
    # or: .\venv\Scripts\activate  # For Windows
    ```
    If you have Linux or macOS activate the virtual enviroment like this:
    ```bash
    source venv/bin/activate
    ```
    If you have Windows use this command instead:
    ```bash
    .\venv\Scripts\activate
    ```
    Once our virtual enviroment is running we can install all the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    Execute the Flask server. Be sure to set the environment variable to point to the main application file:

    ```bash
    flask run --host=0.0.0.0 --reload --debug
    ```

3.  **Access the Application:**
    The application will be available by default at:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)


## Testing

The project includes unit and integration tests to ensure the application's stability and correctness. We recommend executing tests within the same environment where the dependencies were installed (either local virtual environment or inside the Docker container/Vagrant VM).

### Executing Tests

To run all tests using the `pytest` framework, use the following command from the root directory:

```bash
pytest