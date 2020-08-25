# Dynamic sitemap
Branch "dev" status:  
[![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=dev)](https://travis-ci.com/KazakovDenis/dynamic-sitemap)
[![codecov](https://codecov.io/gh/KazakovDenis/dynamic-sitemap/branch/dev/graph/badge.svg)](https://codecov.io/gh/KazakovDenis/dynamic-sitemap)


## Installation
- clone the repo
```shell script
git clone https://github.com/KazakovDenis/dynamic-sitemap.git
```
or
- download it from this [link](https://github.com/KazakovDenis/dynamic-sitemap/archive/master.zip) and unzip

## Testing  
Install dependencies before
```shell script
pip install -r tests/requirements/all.txt
```
or
```shell script
pip install -r tests/requirements/base.txt
```
to install with no supported frameworks.

### Unit testing
Execute the command below to run unit tests
```shell script
python -m pytest
```

### Coverage
Execute the command below to check test coverage
```shell script
coverage run && coverage report && coverage html
```
and open `htmlcov/index.html` in a browser
