# -*- coding: utf-8 -*-
import logging
import asyncio

from ..protocol import statistics, protocol

_logger = logging.getLogger(__name__)


class NSWCovid(object):
    def __init__(self, loop=None):
        super().__init__()
        self.__loop = loop if loop else asyncio.get_event_loop()
        self.__protocol = protocol.Protocol(loop=self.__loop)
        self.__statistics_handler = None
        self.__statistics = None
        self.__track = None
        self.__event_listeners = list()

    async def refresh(self):
        _logger.debug("Refresing...")
        if not self.__statistics:
            self.__statistics_handler = statistics.StatisticHandler(
                protocol=self.__protocol, event_listeners=self.__event_listeners
            )
            await self.__statistics_handler.build()
            self.__statistics = self.__statistics_handler.statistics
            self.__track = self.__statistics_handler.track
        else:
            self.__statistics_handler.build()
        return True

    def addListener(self, event_listener):
        _logger.debug("Adding event receiver")
        if not event_listener in self.__event_listeners:
            self.__event_listeners.append(event_listener)
        return event_listener

    def removeListener(self, event_listener):
        _logger.debug("Removing event receiver")
        if event_listener in self.__event_listeners:
            self.__event_listeners.remove(event_listener)
        else:
            return False
        return True

    @property
    def statistics(self):
        if not self.__statistics:
            _logger.error("No known statistics. Make sure to refresh() first.")
            return {}
        return self.__statistics

    @property
    def track(self):
        if not self.__track:
            _logger.error("Unable to track, no devices available.")
            return None
        return self.__track
