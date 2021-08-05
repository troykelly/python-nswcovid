# -*- coding: utf-8 -*-


class event_payload(object):
    def __init__(self, event_type=None, subject=None, ts=None):
        super().__init__()
        self.__event_type = event_type
        self.__subject = subject
        self.__ts = ts

    @property
    def id(self):
        try:
            return self.__subject.id
        except AttributeError:
            return None

    @property
    def event_type(self):
        try:
            return self.__event_type
        except AttributeError:
            return None

    @property
    def subject(self):
        try:
            return self.__subject
        except AttributeError:
            return None

    @property
    def ts(self):
        try:
            return self.__ts
        except AttributeError:
            return None
