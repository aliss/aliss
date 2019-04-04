# ALISS [![Build Status](https://travis-ci.org/aliss/ALISS.svg?branch=master)](https://travis-ci.org/aliss/ALISS)

> ALISS (A Local Information System for Scotland) is a service to help you find help and support close to you when you need it most.

## JS Plugin

Embed ALISS search features on your own site with the [aliss.js plugin](https://github.com/aliss/aliss.js).

## Links

- Production site: https://www.aliss.org
- Search API endpoint (v3): https://www.aliss.org/api/v3/search/
- API docs: http://docs.aliss.org
- API docs repo: https://github.com/aliss/Docs

## How to install ALISS
1. Clone repository https://help.github.com/en/articles/cloning-a-repository.
2. Install Python3 https://www.python.org/downloads/.
3. If not installed download pip3 https://pip.pypa.io/en/stable/installing/.
4. Use pip3 to install the dependancies in requirements.txt on MacOS this can be achieved with `pip3 install -r requirements.txt`.
5. If not already installed download NPM https://www.npmjs.com/get-npm.
6. Install the npm packages using command `npm i`.

## How to setup ALISS
To run the ALISS project it is necessary to setup the environment on your machine and import data.
1. Create a hidden file `.env` this will store necessary environment variables.
2. With the use of `.env.example` copy the contents and customise with the relevant information for your environment.



### Requirements

- Python 3
- pip3
- See `requirements.txt` for pip packages
- Elasticsearch >=6.1.3
- Postgres >= 9.0
