import os,sys
from pathlib import Path
import logging 
from typing import *
from functools import cached_property, lru_cache as cache
import pandas as pd
import shutil
import numpy as np

log = logging.getLogger('borges')

TMP_CORPUS='tmp'
PATH_USER_HOME = str(Path.home())
PATH_HOME = os.path.join(PATH_USER_HOME,'borges_data')
PATH_CORPORA = os.path.join(PATH_HOME,'corpora')
PATH_CONFIG = os.path.join(PATH_HOME,'config')

KEY_ID = 'id'

from .tools import *
from .corpus import *
from .text import *
from .passage import *