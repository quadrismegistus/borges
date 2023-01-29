from .imports import *

import pymongo
from pymongo import MongoClient

class DB(BaseObject):
    @cached_property
    def client(self): return MongoClient()
    @cached_property
    def db(self): return self.client['borges']
    
    @cached_property
    def metadata(self): 
        coll=self.db['metadata']
        coll.create_index('year')
        coll.create_index('author')
        coll.create_index([('title', 'text')])
        return coll
    
    @cached_property
    def pages(self): 
        coll=self.db['pages']
        coll.create_index('text_id')
        coll.create_index('page_num')
        coll.create_index([('page', 'text')])
        return coll
