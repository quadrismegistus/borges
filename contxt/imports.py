import warnings
warnings.filterwarnings('ignore')
import os,sys,time,shutil
sys.path.insert(0,os.path.abspath('/Users/ryan/github/yapmap'))
from yapmap import *
import multiprocessing
from multiprocessing.pool import ThreadPool
NUM_CPU = multiprocessing.cpu_count()

from collections import UserDict
import flair, torch
# flair.device = torch.device('mps')
from pathlib import Path
import logging,html
# import pysolr
from typing import *
from functools import partial, cached_property, lru_cache
cache = lru_cache(maxsize=None)
from itertools import islice
import pandas as pd
import shutil
import numpy as np
import threading
from threading import Thread

import pymongo
from pymongo import MongoClient, UpdateOne, ReplaceOne
from pymongo.errors import DuplicateKeyError
import click,json
import numpy as np
from scipy.stats import percentileofscore


log = logging.getLogger('contxt')

TMP_CORPUS='tmp'
PATH_USER_HOME = str(Path.home())
PATH_HOME = os.path.join(PATH_USER_HOME,'contxt_data')
PATH_CORPORA = os.path.join(PATH_HOME,'corpora')
PATH_CONFIG = os.path.join(PATH_HOME,'config')
PATH_DATA = os.path.join(PATH_HOME,'data')

THREADWORKERS = None

CLAR_ID=f'_chadwyck/Eighteenth-Century_Fiction/richards.01'
KEY_ID = '_id'

from .etc import *
from .tools import *
from .baseobj import *
from .db import *
from .embed import *
from .corpus import *
from .text import *
from .sent import *
from .page import *
from .passage import *
from .corpora import *
from .absconc import *