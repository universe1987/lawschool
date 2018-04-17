import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict

import scipy
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from StopWatch import StopWatch

if __name__ == '__main__':
    draw_app_char()
    draw_school_char()
    draw_para()
    pool_s1_t1=addup(all those receive offers in t1 and prefer s1)
    pool_s2_t2=

