# Dynamic sitemap
| master | dev |
| :---: | :---: |  
| [![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=master)](https://travis-ci.com/KazakovDenis/dynamic-sitemap) | [![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=dev)](https://travis-ci.com/KazakovDenis/dynamic-sitemap) |  

A simple sitemap generator for Python projects.

Already implemented:
- metaclass SitemapMeta
- FlaskSitemap

## Installation
- Using pip  
```shell script
pip install dynamic-sitemap
```
or
- Download it from this [link](https://github.com/KazakovDenis/dynamic-sitemap/archive/master.zip) and unzip to your project

or
- Add it as a git submodule
```shell script
git submodule add -b master --name sitemap https://github.com/KazakovDenis/dynamic-sitemap path/to/app/sitemap
```
  
  
## Usage
Basic example:
```python
from framework import Framework
from dynamic_sitemap import FrameworkSitemap
from models import Post, Tag

app = Framework(__name__)
sitemap = FrameworkSitemap(app, 'https://mysite.com')
sitemap.config.IGNORED.update(['/edit', '/upload'])
sitemap.config.TEMPLATE_FOLDER = ['app', 'templates']
sitemap.update()
sitemap.add_rule('/app', Post, lastmod='created')
sitemap.add_rule('/app/tag', Tag, priority=0.4)
```
Then run your server and visit http://mysite.com/sitemap.xml.

Also you can set configurations from your class (and __it's preferred__):
```python
sm_logger = logging.getLogger('sitemap')
sm_logger.setLevel(30)

class Config:
    TEMPLATE_FOLDER = os.path.join(ROOT, 'app', 'templates')
    IGNORED = {'/admin', '/back-office', '/other-pages'}
    ALTER_PRIORITY = 0.1
    LOGGER = sm_logger

sitemap = FrameworkSitemap(app, 'https://myshop.org', config_obj=Config)
sitemap.add_rule('/goods', Product, slug='id', lastmod='updated')
```
Moreover you can get a static file by using:
```python
sitemap.build_static()
```

Some important rules:  
- use update() method after setting configuration attributes directly (not need if you pass your config object to init)
- use get_dynamic_rules() to see which urls you should add as a rule or to ignored
- *config.IGNORED* has a priority over *add_rule*
- use helpers.Model if your ORM is not supported
