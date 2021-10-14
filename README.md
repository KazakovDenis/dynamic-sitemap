# Dynamic sitemap  
![Python version](https://img.shields.io/badge/python-3.6%2B-blue)
[![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=master)](https://travis-ci.com/KazakovDenis/dynamic-sitemap)
[![codecov](https://codecov.io/gh/KazakovDenis/dynamic-sitemap/branch/master/graph/badge.svg)](https://codecov.io/gh/KazakovDenis/dynamic-sitemap)
![PyPI - Downloads](https://img.shields.io/pypi/dm/dynamic-sitemap)

A simple sitemap generator for Python projects.

Already implemented:
- SimpleSitemap
- FlaskSitemap

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
sitemap = SimpleSitemap(urls, 'https://mysite.com')
sitemap.write('static/sitemap.xml')
```
### Dynamic
Only FlaskSitemap is implemented yet, so there is an example:
```python
from flask import Flask
from dynamic_sitemap import FlaskSitemap

app = Flask(__name__)
sitemap = FlaskSitemap(app, 'https://mysite.com')
sitemap.update()
```
Then run your server and visit http://mysite.com/sitemap.xml.  

Basic example with some Models:
```python
from flask import Flask
from dynamic_sitemap import FlaskSitemap
from models import Post, Tag

app = Flask(__name__)
sitemap = FlaskSitemap(app, 'https://mysite.com', orm='sqlalchemy')
sitemap.config.IGNORED.update(['/edit', '/upload'])
sitemap.config.TEMPLATE_FOLDER = 'templates'
sitemap.config.TIMEZONE = 'Europe/Moscow'
sitemap.update()
sitemap.add_elem('/faq', changefreq='monthly', priority=0.4)
sitemap.add_rule('/blog', Post, lastmod_attr='created', priority=1.0)
sitemap.add_rule('/blog/tag', Tag, changefreq='daily')
```

Also you can set configurations from your class (and __it's preferred__):
```python
class Config:
    TEMPLATE_FOLDER = os.path.join(ROOT, 'app', 'templates')
    IGNORED = {'/admin', '/back-office', '/other-pages'}
    ALTER_PRIORITY = 0.1

sitemap = FlaskSitemap(app, 'https://myshop.org', config_obj=Config)
sitemap.add_elem('/about', changefreq='monthly', priority=0.4)
sitemap.add_rule('/goods', Product, loc_attr='id', lastmod_attr='updated')
```

Some important rules:  
- use update() method after setting configuration attributes directly (not need if you pass your config object to init)
- use get_dynamic_rules() to see which urls you should add as a rule or to ignored
- *config.IGNORED* has a priority over *add_rule*
- use helpers.Model if your ORM is not supported

Not supported yet:
- urls with more than 1 converter, such as `/page/<int:user_id>/<str:slug>`

Check out the [Changelog](https://github.com/KazakovDenis/dynamic-sitemap/blob/master/CHANGELOG.md)