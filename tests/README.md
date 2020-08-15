# Dynamic sitemap
| master | dev |
| :---: | :---: |  
| [![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=master)](https://travis-ci.com/KazakovDenis/dynamic-sitemap) | [![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=dev)](https://travis-ci.com/KazakovDenis/dynamic-sitemap) |  

## Installation
- Download it from this [link](https://github.com/KazakovDenis/dynamic-sitemap/archive/master.zip) and unzip to your project
  
or
- Add it as a git submodule
```shell script
git submodule add -b master --name sitemap https://github.com/KazakovDenis/dynamic-sitemap path/to/app/sitemap
```

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
coverage run -m pytest && coverage report -m && coverage html
```
and open `htmlcov/index.html` in a browser
