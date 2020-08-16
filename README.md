# Dynamic sitemap
| master | dev |
| :---: | :---: |  
| [![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=master)](https://travis-ci.com/KazakovDenis/dynamic-sitemap) | [![Build Status](https://travis-ci.com/KazakovDenis/dynamic-sitemap.svg?branch=dev)](https://travis-ci.com/KazakovDenis/dynamic-sitemap) |  

A simple sitemap generator for Python projects.

Already implemented:
- metaclass SitemapMeta
- FlaskSitemap

## Installation
- using pip  
```shell script
pip install dynamic-sitemap
```
or
- as a git submodule
```shell script
git submodule add -b master --name sitemap https://github.com/KazakovDenis/dynamic-sitemap path/to/app/sitemap
```
  
  
## Usage
"Hello world" example:
```python
from framework import Framework
from dynamic_sitemap import FrameworkSitemap

app = Framework(__name__)
sitemap = FrameworkSitemap(app, 'https://mysite.com')
sitemap.update()
```
Then run your server and visit http://mysite.com/sitemap.xml.  

Basic example with some Models:
```python
from framework import Framework
from dynamic_sitemap import FrameworkSitemap
from models import Post, Tag

app = Framework(__name__)
sitemap = FrameworkSitemap(app, 'https://mysite.com')
sitemap.config.IGNORED.update(['/edit', '/upload'])
sitemap.config.TEMPLATE_FOLDER = ['app', 'templates']
sitemap.update()
sitemap.add_rule('/blog', Post, lastmod='created')
sitemap.add_rule('/blog/tag', Tag, priority=0.4)
```

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

Check out the [Changelog](https://github.com/KazakovDenis/dynamic-sitemap/blob/master/CHANGELOG.md)