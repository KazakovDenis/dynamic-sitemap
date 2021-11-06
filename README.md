# Dynamic sitemap  
![Python version](https://img.shields.io/badge/python-3.6%2B-blue)
[![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=master)](https://travis-ci.com/KazakovDenis/dynamic-sitemap)
[![codecov](https://codecov.io/gh/KazakovDenis/dynamic-sitemap/branch/master/graph/badge.svg)](https://codecov.io/gh/KazakovDenis/dynamic-sitemap)
![PyPI - Downloads](https://img.shields.io/pypi/dm/dynamic-sitemap)

The simple sitemap generator for Python projects.

## Installation
- using pip  
```shell script
pip install dynamic-sitemap
```
  
## Usage
### Static
```python
from datetime import datetime
from dynamic_sitemap import SimpleSitemap, ChangeFreq

urls = [
    '/',
    {'loc': '/contacts', 'changefreq': ChangeFreq.NEVER.value},
    {'loc': '/about', 'priority': 0.9, 'lastmod': datetime.now().isoformat()},
]
sitemap = SimpleSitemap('https://mysite.com', urls)
# or sitemap.render()
sitemap.write('static/sitemap.xml')
```
### Dynamic
Only FlaskSitemap is implemented yet, so there is an example:
```python
from dynamic_sitemap import FlaskSitemap
from flask import Flask

app = Flask(__name__)
sitemap = FlaskSitemap(app, 'https://mysite.com')
sitemap.build()
```
Then run your server and visit http://mysite.com/sitemap.xml.  

The basic example with some Models:
```python
from dynamic_sitemap import ChangeFreq, FlaskSitemap
from flask import Flask
from models import Post, Tag

app = Flask(__name__)
sitemap = FlaskSitemap(app, 'https://mysite.com', orm='sqlalchemy')
sitemap.config.TIMEZONE = 'Europe/Moscow'
sitemap.ignore('/edit', '/upload')
sitemap.add_items(
    '/contacts',
    {'loc': '/faq', 'changefreq': ChangeFreq.MONTHLY.value, 'priority': 0.4},
)
sitemap.add_rule('/blog', Post, loc_from='slug', priority=1.0)
sitemap.add_rule('/blog/tag', Tag, loc_from='id', changefreq='daily')
sitemap.build()
```

Also you can set configurations from your class (and __it's preferred__):

```python
from dynamic_sitemap import ChangeFreq, FlaskSitemap
from flask import Flask
from models import Product

class Config:
    FILENAME = 'static/sitemap.xml'
    IGNORED = {'/admin', '/back-office', '/other-pages'}
    ALTER_PRIORITY = 0.1

app = Flask(__name__)
sitemap = FlaskSitemap(app, 'https://myshop.org', config=Config)
sitemap.add_items(
    '/contacts',
    {'loc': '/about', 'changefreq': ChangeFreq.MONTHLY.value, 'priority': 0.4},
)
sitemap.add_rule('/goods', Product, loc_from='id', lastmod_from='updated')
sitemap.build()
```

Not supported yet:
- urls with more than 1 converter, such as `/page/<int:user_id>/<str:slug>`

Check out the [Changelog](https://github.com/KazakovDenis/dynamic-sitemap/blob/master/CHANGELOG.md).  

## Contributing
Feel free to suggest any improvements :)  

## Development
Fork this repository, clone it and install dependencies:
```shell
pip install -r requirements/all.txt 
```
Checkout to a new branch, add your feature and some tests, then try:
```shell
make precommit
```

If the result is ok, create a pull request to "dev" branch of this repo with a detailed description.  
Done!  
