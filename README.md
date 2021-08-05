<img src=https://img.shields.io/github/license/kendrajmoore/hackathon-portfolio>
<p align="center">
 <img width="460" src="https://user-images.githubusercontent.com/51943194/121562739-98dd0680-c9ce-11eb-897a-579780e50c9a.jpg">
</p>

# Team KENARGI Portfolio Webpage
by Armando, Gigi, Kendra, Pod 3.3.5

## Introduction

Design and maintain a portfolio website for our open-source projects.

## Description

Working as a team, we created a website to track our projects and accomplishments. 

## Technologies Used

- Python-Flask
- HTML
- CSS
- JSON

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


Start flask development server
```bash
$ export FLASK_ENV=development
$ export URL=localhost:5000 
$ flask run
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
