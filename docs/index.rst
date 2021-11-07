The simple sitemap generator
===========================================

Dynamic sitemap is a library for sitemaps generation in Python projects.


Contents
--------

.. toctree::

    api


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
            <priority>0.9</priority></url>
    </urlset>

You may want to write a sitemap to a file:

.. code-block:: python

    from datetime import datetime
    from dynamic_sitemap import SimpleSitemap, ChangeFreq

    sitemap = SimpleSitemap('https://site.com')
    sitemap.add_items(
        {'loc': '/about', 'priority': 0.9, 'lastmod': datetime.now().isoformat()},
    )
    sitemap.write('static/sitemap.xml')

Then check out ``static/sitemap.xml`` file.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
