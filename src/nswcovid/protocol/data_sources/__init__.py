# -*- coding: utf-8 -*-
import json
import logging
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

_logger = logging.getLogger(__name__)

DATA_SOURCES = None
try:
    with open(f"{dir_path}/data.json") as jsonFile:
        DATA_SOURCES = json.load(jsonFile)
        jsonFile.close()
except Exception as err:
    _logger.error(err)
