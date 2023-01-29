import os,sys
sys.path.insert(0,os.path.abspath('/Users/ryan/github/yapmap'))
from yapmap import *
from pathlib import Path
import logging,html
# import pysolr
from typing import *
from functools import cached_property, lru_cache as cache
import pandas as pd
import shutil
import numpy as np
import warnings
warnings.filterwarnings('ignore')

log = logging.getLogger('contxt')

TMP_CORPUS='tmp'
PATH_USER_HOME = str(Path.home())
PATH_HOME = os.path.join(PATH_USER_HOME,'contxt_data')
PATH_CORPORA = os.path.join(PATH_HOME,'corpora')
PATH_CONFIG = os.path.join(PATH_HOME,'config')

KEY_ID = '_id'

from .tools import *
from .baseobj import *
from .db import *
from .corpus import *
from .text import *
from .page import *
from .passage import *