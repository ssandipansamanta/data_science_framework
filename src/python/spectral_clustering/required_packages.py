def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        from pip._internal import main
        main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)

results = map(install_and_import, ('pandas', 'numpy','matplotlib','scipy','sklearn','datetime'))
set(results)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import gc
import scipy
import sklearn
from datetime import datetime
from scipy.sparse import csgraph
from numpy import linalg as LA
from scipy.spatial.distance import pdist, squareform
