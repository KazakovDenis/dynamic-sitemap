The simple sitemap generator
=============================

Dynamic sitemap is a library for sitemaps and sitemap indexes generation
based on `the protocol <https://www.sitemaps.org/protocol.html>`_.

The library provides API to generate sitemaps (sitemap indexes) manually or
autogenerate it for some frameworks (only FlaskSitemap is available yet).

Contents
--------

.. toctree::

    api
    changelog


Installation
------------

To use dynamic sitemap lib, first install it using pip:

.. code-block:: console

   (.venv) $ pip install dynamic-sitemap


Getting started
---------------

Try this small snippet:

.. code-block:: python

    from dynamic_sitemap import ChangeFreq, SimpleSitemap

    # items should be strings or dicts
    items = (
        '/about',
        {'loc': '/contacts', 'changefreq': ChangeFreq.NEVER.value},
    )
    sitemap = SimpleSitemap('https://site.com', items)
    print(sitemap.render())

In the output you will see something like this:

.. code-block:: xml

    <?xml version='1.0' encoding='UTF-8'?>
    <urlset
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    >
        <url>
            <loc>https://site.com/</loc>
        </url>
        <url>
            <loc>https://site.com/about</loc>
        </url>
        <url>
            <loc>https://site.com/contacts</loc>
            <lastmod>2021-11-07T19:54:04.848443</lastmod>
            <priority>0.9</priority>
        </url>
    </urlset>

You may want to write a sitemap to a file:

.. code-block:: python

    from datetime import datetime
    from dynamic_sitemap import ChangeFreq, SimpleSitemap

    sitemap = SimpleSitemap('https://site.com')
    sitemap.add_items(
        {'loc': '/about', 'priority': 0.9, 'lastmod': datetime.now().isoformat()},
    )
    sitemap.write('static/sitemap.xml')

Then check out ``static/sitemap.xml`` file.


Usage
------

Sitemap for Flask
`````````````````

'Hello world' example:

.. code-block:: python

    from dynamic_sitemap import FlaskSitemap
    from flask import Flask

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://site.com')
    sitemap.build()

Then visit `<http://localhost:5000/sitemap.xml>`_.

The basic example using some SQLAlchemy models:

.. code-block:: python

    from dynamic_sitemap import ChangeFreq, FlaskSitemap
    from flask import Flask
    from models import Post, Tag

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://site.com', orm='sqlalchemy')
    sitemap.config.ALTER_PRIORITY = 0.1
    sitemap.ignore('/edit', '/upload')
    sitemap.add_items('/faq', {'loc': '/about', 'priority': 0.7})
    sitemap.add_rule('/blog', Post, loc_from='slug', priority=1.0)
    sitemap.add_rule('/blog/tag', Tag, loc_from='id', changefreq=ChangeFreq.DAILY.value)
    sitemap.build()


**Not supported** yet:

* urls with more than 1 converter, such as ``/page/<int:user_id>/<str:slug>``.

Also you can set configurations from your class:

.. code-block:: python

    class Config:
        FILENAME = 'static/sitemap.xml'
        IGNORED = {'/admin', '/back-office', '/other-pages'}
        CONTENT_PRIORITY = 0.7

    sitemap = FlaskSitemap(app, 'https://myshop.org', config=Config, orm='sqlalchemy')
    sitemap.add_rule('/goods', Product, loc_from='id', lastmod_from='updated')
    sitemap.build()

Sitemap without ORM
```````````````````

If you do not use ORM, you may add rules via :ref:`add_raw_rule() <flask-sitemap>`
using :ref:`helpers.Model <helpers-model>`

.. code-block:: python

    from flask import Flask
    from db import connect

    app = Flask(__name__)
    db = connect(DB_ADDRESS)

    def extract_posts():
        query = 'SELECT slug, updated FROM posts;'
        with db.execute(query) as cursor:
            return iter(cursor.fetchall())

    post = Model(extract_posts)
    sitemap = FlaskSitemap(app, 'https://site.com')
    sitemap.add_raw_rule('/posts/', post)
    sitemap.build()


Changelog
---------

Check out :doc:`here <changelog>`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
