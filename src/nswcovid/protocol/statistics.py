# -*- coding: utf-8 -*-
"""
Statistic handler for NSWCovid
"""

import logging
from datetime import datetime, timedelta
import asyncio
import re
import pytz
import jello
from jello.lib import opts, load_json, pyquery, Schema, Json
import inspect

from .data_sources import DATA_SOURCES
from .event_payload import event_payload

_logger = logging.getLogger(__name__)

TZ = pytz.timezone("Australia/Sydney")
ATTRIBUTION = "© State of New South Wales NSW Ministry of Health. For current information go to www.health.nsw.gov.au"

# This is for testing mostly
# ENABLED_DATA_SOURCES = [
#     "published",
#     "locally_active",
#     "lives_lost_male_0_9",
#     "lives_lost_male_70_79",
# ]
ENABLED_DATA_SOURCES = list()


class StatisticHandler(object):
    def __init__(self, protocol, event_listeners=None):
        super().__init__()
        self.__protocol = protocol
        self.__event_listeners = event_listeners
        self.__statistics = {}

    @property
    def loop(self):
        if not self.__protocol.loop:
            return None
        return self.__protocol.loop

    @property
    def __list(self):
        if not self.__statistics:
            return []
        return [*self.__statistics]

    @property
    def statistics(self):
        try:
            return self.__statistics
        except AttributeError:
            return None

    async def build(self, limit=20, page=1):
        all_statistics = await self.__listall(limit=limit, page=page)
        while all_statistics:
            for statistic_reference in all_statistics:
                if "id" in statistic_reference:
                    statistic_id = statistic_reference["id"]
                    if len(ENABLED_DATA_SOURCES) > 0:
                        if statistic_id in ENABLED_DATA_SOURCES:
                            self.__statistics[statistic_id] = Statistic(
                                handler=self,
                                id=statistic_id,
                                data=statistic_reference,
                                event_listeners=self.__event_listeners,
                            )
                    else:
                        self.__statistics[statistic_id] = Statistic(
                            handler=self,
                            id=statistic_id,
                            data=statistic_reference,
                            event_listeners=self.__event_listeners,
                        )
            page += 1
            all_statistics = await self.__listall(limit=limit, page=page)
        statistic_ids = self.__statistics.keys()
        tasks = list()
        for id in statistic_ids:
            task = self.__protocol.loop.create_task(self.__statistics[id].refresh())
            tasks.append(task)
            await task
        return self.__statistics

    async def __listall(self, limit=20, page=1):
        keys = list(DATA_SOURCES.keys())
        pagination = list()
        start = (page - 1) * limit
        end = start + limit
        if end > len(keys):
            end = len(keys)
        if start > end:
            return None
        for i in range(start, end):
            key = keys[i]
            DATA_SOURCES[key]["id"] = key
            pagination.append(DATA_SOURCES[key])
        return pagination

    async def details(self, id):
        """Get device details

        Attributes:
            id (string): The device id
        """
        if not id in self.__statistics:
            return None
        statistic = self.__statistics[id]
        _logger.debug("%s getting value (%s)", statistic.name, statistic.id)
        try:
            get = await self.__protocol.api_get(
                host=statistic.host, path=statistic.path
            )
        except Exception as err:
            _logger.error(err)
            return statistic

        if not get:
            _logger.error("No response from server")
            return statistic

        retrieved = None
        if "retrieved" in get:
            retrieved = get["retrieved"]

        if not "body" in get:
            _logger.error("No body from server")
            return statistic

        value = None

        if (
            hasattr(statistic, "selector")
            and statistic.selector is not None
            and get["soup"] is not None
        ):
            reference = get["soup"].select_one(statistic.selector)

            if not reference:
                _logger.error(
                    "%s could not find selector %s", statistic.id, statistic.selector
                )
                return statistic

            value = reference.string

        if (
            hasattr(statistic, "xpath")
            and statistic.xpath is not None
            and get["dom"] is not None
        ):
            reference = get["dom"].xpath(statistic.xpath)

            if not reference and reference[0]:
                _logger.error(
                    "%s could not find xpath %s", statistic.id, statistic.selector
                )
                return statistic

            value = reference[0]

        if (
            hasattr(statistic, "json_search")
            and statistic.json_search is not None
            and get["json_data"] is not None
        ):
            # https://blog.kellybrazil.com/2020/03/25/jello-the-jq-alternative-for-pythonistas/
            # load the JSON or JSON Lines
            list_dict_data = None
            try:
                list_dict_data = load_json(get["body"])
            except Exception as e:
                msg = f"""JSON Load Exception: Cannot parse the data (Not valid JSON or JSON Lines)
            {e}
            """
                _logger.error(f"jello:  {msg}")
                return statistic

            try:
                value = pyquery(list_dict_data, statistic.json_search)
                if type(value) == list:
                    value = value[0]
            except Exception as e:
                _logger.exception(e)
                return statistic

            if statistic.typeName == "integer" and value is None:
                value = 0

        if (
            hasattr(statistic, "regex")
            and statistic.regex is not None
            and value is not None
        ):
            match = statistic.regex.search(str(value))
            if not match:
                return statistic

            value = match.group()

        if (
            hasattr(statistic, "typeName")
            and statistic.typeName is not None
            and value is not None
        ):
            if statistic.typeName == "integer":
                if isinstance(value, str):
                    try:
                        value = int(re.sub("[^0-9]", "", value))
                    except Exception as err:
                        _logger.error(
                            "Failed converting %s to integer: %s", statistic.id, value
                        )
                        _logger.error(err)
                else:
                    value = int(value)
            elif statistic.typeName == "float":
                if isinstance(value, str):
                    value = float(value.replace(",", ""))
                else:
                    value = float(value)
            elif statistic.typeName == "boolean":
                value = bool(value)
            elif statistic.typeName == "string" and not isinstance(value, str):
                value = str(value)
            elif statistic.typeName == "nswcoviddate":
                value = datetime.strptime(value.upper(), "%I%p %d %B %Y")
                value = TZ.localize(value)
            elif statistic.typeName == "dateymd":
                value = datetime.strptime(value, "%Y-%m-%d")
            elif statistic.typeName == "date":
                value = datetime.strptime(value, "%d/%m/%Y")
            elif statistic.typeName == "datetime":
                value = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
            elif statistic.typeName == "time":
                value = datetime.strptime(value, "%H:%M:%S")
            elif statistic.typeName == "enum":
                value = str(value)
            else:
                value = str(value)

        statistic.status = value
        if retrieved:
            statistic.updated = retrieved
        _logger.debug(
            "%s got value (%s): %s", statistic.name, statistic.id, statistic.status
        )
        return statistic

    async def __refresh(self, event_receiver=None):
        await self.__protocol.api_get()
        statistic_ids = self.__statistics.keys()
        tasks = list()
        for id in statistic_ids:
            task = self.__protocol.loop.create_task(
                self.__statistics[id].refresh(event_receiver)
            )
            tasks.append(task)
            await task

    async def __track(self, interval, event_receiver=None):
        while True:
            _logger.debug("track is checking for changes...")
            await self.__refresh(event_receiver)
            await asyncio.sleep(interval.total_seconds())

    def track(self, interval=None, event_receiver=None):
        if not self.__protocol.loop:
            return None

        if not interval:
            interval = timedelta(seconds=60)

        if not isinstance(interval, timedelta):
            interval = timedelta(seconds=interval)

        _logger.debug(
            "Tracking statistics every %d seconds...", interval.total_seconds()
        )

        task = self.__protocol.loop.create_task(
            self.__track(interval=interval, event_receiver=event_receiver)
        )

        return task


class Statistic(object):
    def __init__(self, handler=None, id=None, data=None, event_listeners=None):
        super().__init__()

        self.__handler = handler
        self.__id = id
        self.__event_listeners = event_listeners

        if data:
            if "host" in data:
                self.__host = data["host"]
            if "path" in data:
                self.__path = data["path"]
            if "name" in data:
                self.__name = data["name"]
            if "type" in data:
                self.__type = data["type"]
            if "unit" in data:
                self.__unit = data["unit"]
            if "selector" in data:
                self.__selector = data["selector"]
            if "xpath" in data:
                self.__xpath = data["xpath"]
            if "json_search" in data:
                self.__json_search = data["json_search"]
            if "regex" in data:
                self.__regex = data["regex"]
            if "typeId" in data:
                self.__typeId = data["typeId"]
            if "icon" in data:
                self.__icon = data["icon"]
            if "iconId" in data:
                self.__iconId = data["iconId"]
            if "measurement" in data:
                self.__measurement = bool(data["measurement"])
            else:
                self.__measurement = False
            if "resetting" in data:
                self.__resetting = bool(data["resetting"])
            else:
                self.__resetting = False

        self.__attribution = ATTRIBUTION
        self.__previous_value = None
        self.__value = None

    def __check_changed(self):
        changed = False
        if not self.__previous_value == self.__value:
            changed = True

        self.__previous_value = self.__value

        return changed

    async def refresh(self, event_receiver=None):
        if not self.__id:
            return
        await self.__handler.details(self.__id)
        if self.changed:

            payload = event_payload("statistic_updated", self, self.updated)

            if type(self.__event_listeners) == list and self.__event_listeners:
                for event_listener in self.__event_listeners:
                    if callable(event_listener):
                        _logger.debug(
                            "Event triggered for %s to %s",
                            self.id,
                            event_listener.__name__,
                        )
                        try:
                            if inspect.iscoroutinefunction(event_listener):
                                await event_listener(payload)
                            else:
                                event_listener(payload)
                        except Exception as err:
                            _logger.error(
                                "Event trigger failed for %s to %s",
                                self.id,
                                event_listener.__name__,
                            )
                            _logger.exception(err)
                    else:
                        _logger.warning(
                            "An uncallable event listener exists of type %s",
                            type(event_listener),
                        )

            if event_receiver is not None:
                if callable(event_receiver):
                    _logger.debug(
                        "Event triggered for %s to %s", self.id, event_receiver.__name__
                    )
                    try:
                        if inspect.iscoroutinefunction(event_receiver):
                            await event_receiver(payload)
                        else:
                            event_receiver(payload)
                    except Exception as err:
                        _logger.error(
                            "Event trigger failed for %s to %s",
                            self.id,
                            event_receiver.__name__,
                        )
                        _logger.exception(err)
                else:
                    _logger.warning(
                        "An uncallable event receiver exists of type %s",
                        type(event_receiver),
                    )

    @property
    def id(self):
        try:
            return self.__id
        except AttributeError:
            return None

    @property
    def changed(self):
        try:
            return self.__changed
        except AttributeError:
            return None

    @property
    def status(self):
        try:
            return self.__value
        except AttributeError:
            return None

    @status.setter
    def status(self, value):
        try:
            self.__value = value
            self.__changed = self.__check_changed()
        except AttributeError:
            pass
        _logger.debug("Updating statistic %s: %s", self.__id, self.status)

    @property
    def attribution(self):
        try:
            return self.__attribution
        except AttributeError:
            return None

    @property
    def updated(self):
        try:
            return self.__retrieved
        except AttributeError:
            return None

    @updated.setter
    def updated(self, value):
        try:
            self.__retrieved = value
        except AttributeError:
            pass

    @property
    def age(self):
        if not self.updated:
            return None

        time_delta = datetime.now() - self.updated
        return round(time_delta.total_seconds())

    @property
    def name(self):
        try:
            return self.__name
        except AttributeError:
            return None

    @property
    def published(self):
        try:
            return self.__handler.statistics["published"].status
        except AttributeError:
            return None

    @property
    def typeName(self):
        try:
            return self.__type
        except AttributeError:
            return None

    @property
    def typeId(self):
        try:
            return self.__typeId
        except AttributeError:
            return None

    @property
    def iconId(self):
        try:
            return self.__iconId
        except AttributeError:
            return None

    @property
    def measurement(self):
        try:
            return self.__measurement
        except AttributeError:
            return None

    @property
    def resetting(self):
        try:
            return self.__resetting
        except AttributeError:
            return None

    @property
    def host(self):
        try:
            return self.__host
        except AttributeError:
            return None

    @property
    def icon(self):
        try:
            return self.__icon
        except AttributeError:
            return None

    @property
    def path(self):
        try:
            return self.__path
        except AttributeError:
            return None

    @property
    def unit(self):
        try:
            return self.__unit
        except AttributeError:
            return None

    @property
    def selector(self):
        try:
            return self.__selector
        except AttributeError:
            return None

    @property
    def xpath(self):
        try:
            return self.__xpath
        except AttributeError:
            return None

    @property
    def json_search(self):
        try:
            return self.__json_search
        except AttributeError:
            return None

    @property
    def regex(self):
        regex = None
        try:
            regex = self.__regex
        except AttributeError:
            return None
        if not regex:
            return None
        return re.compile(regex, re.IGNORECASE)

    @property
    def loop(self):
        try:
            return self.__handler.loop
        except AttributeError:
            return None
