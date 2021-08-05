# -*- coding: utf-8 -*-

import pytest
import logging
import datetime

from nswcovid import NSWCovid

logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

__author__ = "Troy Kelly"
__copyright__ = "Troy Kelly"
__license__ = "mit"


@pytest.mark.asyncio
async def test_app():
    def event_receiver(payload):
        _logger.debug(payload)

    api = NSWCovid()
    api.addListener(event_receiver)
    await api.refresh()
    assert (
        api.statistics["locally_active"].status
        and api.statistics["locally_active"].status >= 0
    )
    # assert api.statistics["interstate_active"].status >= 0
    # assert api.statistics["overseas_active"].status >= 0
    # assert api.statistics["last_24_hours_known"].status >= 0
    # assert api.statistics["last_24_hours_unknown"].status >= 0
    # assert api.statistics["last_24_hours_interstate"].status >= 0
    # assert api.statistics["last_24_hours_overseas"].status >= 0
    # assert api.statistics["last_24_hours_total"].status >= 0
    # assert api.statistics["last_24_hours_tests"].status >= 0
    # assert api.statistics["this_week_known"].status >= 0
    # assert api.statistics["this_week_unknown"].status >= 0
    # assert api.statistics["this_week_interstate"].status >= 0
    # assert api.statistics["this_week_overseas"].status >= 0
    # assert api.statistics["this_week_total"].status >= 0
    # assert api.statistics["this_week_tests"].status >= 0
    # assert api.statistics["last_week_known"].status >= 0
    # assert api.statistics["last_week_unknown"].status >= 0
    # assert api.statistics["last_week_interstate"].status >= 0
    # assert api.statistics["last_week_overseas"].status >= 0
    # assert api.statistics["last_week_total"].status >= 0
    # assert api.statistics["last_week_tests"].status >= 0
    # assert api.statistics["this_year_known"].status >= 0
    # assert api.statistics["this_year_unknown"].status >= 0
    # assert api.statistics["this_year_interstate"].status >= 0
    # assert api.statistics["this_year_overseas"].status >= 0
    # assert api.statistics["this_year_total"].status >= 0
    # assert api.statistics["this_year_tests"].status >= 0
    # assert api.statistics["last_24_hours_first_dose"].status >= 0
    # assert api.statistics["last_24_hours_second_dose"].status >= 0
    # assert api.statistics["last_24_hours_total_dose"].status >= 0
    # assert api.statistics["total_first_dose"].status >= 0
    # assert api.statistics["total_second_dose"].status >= 0
    # assert api.statistics["total_total_dose"].status >= 0
    assert (
        hasattr(api.statistics["lives_lost_male_0_9"], "status")
        and api.statistics["lives_lost_male_0_9"].status >= 0
    )
    assert (
        hasattr(api.statistics["lives_lost_male_70_79"], "status")
        and api.statistics["lives_lost_male_70_79"].status >= 0
    )
    assert isinstance(api.statistics["locally_active"].published, datetime.datetime)
    assert isinstance(api.statistics["published"].status, datetime.datetime)
