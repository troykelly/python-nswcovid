NSW Covid Data
==============

NSW Health does not provide an API for accessing current Covid cases,
vaccinations and related information. This is a screen scaper to
facilitate programmatic access.

Look how easy it is to use::

    import logging
    import asyncio
    from nswcovid import NSWCovid

    _logger = logging.getLogger(__name__)

    loop = asyncio.get_event_loop()
    covid = NSWCovid(loop=loop)

    def event_receiver(event_type=None, statistic_id=None, statistic=None, ts=None):
        _logger.debug(event_type)
        _logger.debug(statistic_id)
        _logger.debug(statistic)
        _logger.debug(ts)

    async def get_data():
        await covid.refresh()
        covid.track(event_receiver=event_receiver)

    loop.run_until_complete(get_data())


Home Assistant
--------------

These library is primarily for the Home Assistant integration
https://github.com/troykelly/homeassistant-au-nsw-covid

Features
--------

- Easy access to Covid data
- Event push on change

Installation
------------

Install NSWCovid by running:

    install nswcovid

Contribute
----------

- Issue Tracker: https://github.com/troykelly/python-nswcovid/issues
- Source Code: https://github.com/troykelly/python-nswcovid

Support
-------

If you are having issues, please create an issue.
