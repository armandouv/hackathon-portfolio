# Blog website
by Moisés, Armando, Oscar and Anthony from Pod 3.3.5


## Description

A blog website.


## Technologies Used

- Python-Flask
- HTML
- CSS
- Postgres

## Installation

Make sure you have python3 and pip installed


Create and activate virtual environment using virtualenv
```bash
$ python -m venv python3-virtualenv
$ source python3-virtualenv/bin/activate
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependencies

```bash
pip install -r requirements.txt
```

## Usage

Create a .env file using the example.env template

Create a nginx-certbot.env file using the example-nginx-certbot.env template


Start detached server using Docker Compose
```bash
$ docker-compose up -d
```

## Usage with Github actions

Set up the following secrets:
- DISCORD_WEBHOOK
- PROJECT_ROOT
- SSH_IP
- SSH_PRIVATE_KEY
- SSH_USER


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
