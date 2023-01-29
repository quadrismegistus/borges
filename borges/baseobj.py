from .imports import *


class BaseObject(object):
    @property
    def data(self): return self.__getattribute__('_data')

    def __getattr__(self, __name: str) -> Any:
        try:
            if __name in self.data: return self.data[__name]
            return super().__getattr__(__name)
        except AttributeError:
            return None

    def __init__(self, *args, **kwargs):
        self._data={**kwargs}




    @cached_property
    def db(self): 
        from .db import DB
        return DB()


    def search(self, term_or_phrase):
        return pd.DataFrame(self.db.pages.find({'$text':{'$search':term_or_phrase}})).set_index('_id')