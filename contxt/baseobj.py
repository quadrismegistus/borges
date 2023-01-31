from .imports import *


class BaseObject(object):
    def __init__(self, *args, **kwargs):
        for k,v in kwargs.items(): setattr(self,k,v)
        self._data=self.data={**kwargs}