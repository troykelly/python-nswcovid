# -*- coding: utf-8 -*-

import pytest
import logging

from nswcovid import NSWCovid

logger = logging.getLogger(__name__)

__author__ = "Troy Kelly"
__copyright__ = "Troy Kelly"
__license__ = "mit"


@pytest.mark.asyncio
async def test_app():
    api = NSWCovid()
    await api.refresh()
    logger.debug(api.statistics["locally_active"].status)
    assert api.statistics["locally_active"].status >= 0
