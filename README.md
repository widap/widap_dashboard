# widap_dashboard

1. Ensure that the 'dashboard_init_v4_4.py' file is in the same folder 
2. Launch Jupyter notebook: 'dashboard_MVP_onecell.ipynb'
3. Run the first cell
4. Select Plant and Unit

Use widgets for functionality to select time frame and emissions.


For questions, please email bclimate@stanford.edu


Ensure that the following packages are installed:
from __future__ import print_function
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import calendar
import seaborn as sns
import sqlite3 as sq3
import time
import datetime
import scipy as sc
import os
import mysql.connector
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from IPython.display import Javascript, display, Markdown
import ipywidgets as widgets
import warnings
