#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"></ul></div>

# In[ ]:


"""Module containing functions to get events data from WhoScored-style data.

Functions:
    defend_metrics: get a defensive metric dataframe for a match or a player
    get_pass_df: get pass events from a events_df

"""
import pandas as pd
import numpy as np
import seaborn as sns

import urllib
from urllib.request import urlopen
import json
import requests
from bs4 import BeautifulSoup
import json
import re


from datetime import datetime
import os
import pickle
import calendar

from typing import Any, Dict, Tuple, List, cast
#from typing import List, Dict, Any

def defend_metrics(events_df, playerId=None):
    """
    Get defensive metrics from a match
    Agrs:
        events_df: events dataframe
        playerId: playerId, default is None
    Return:
        pivot_df: defensive metrics dataframe
    """
    legends ={'Tackle':'s', 'Aerial':'^', 'BallRecovery':'o', 'Clearance':'*', 'Interception':'X', 'BlockedPass': 'p',
         'Save': 'D'}
    if playerId==None:
        df = events_df.copy()       
    else:      
        df = events_df[events_df['playerId']==playerId]
        
    df = df[df['eventType'].isin(legends.keys())]
    #df.columns
    metrics = df[['eventType','outcomeType']].value_counts().reset_index()
    
    metrics.columns=['eventType', 'outcomeType', 'count']
    # Pivot the DataFrame
    pivot_df =metrics.pivot_table(index='eventType', columns='outcomeType', values='count', fill_value=0)
    try:
        pivot_df['total']= pivot_df['Successful']+pivot_df['Unsuccessful']
    except:
        pivot_df['total']= pivot_df['Successful']
    return pivot_df

def get_pass_df(events_df):
    """
    Filter pass events and add pass into final third, pass into penalty area
    Agrs:
        data = events_df
    Return:
        pass_df
    """
    df = events_df.copy()
    
    # Get passes
    pass_df=df[(df['eventType']=='Pass')|(df['eventType']=='OffsidePass')]
    
    # Add pass
    pass_df['thirdpass'] = (pass_df['endX'] >= 200/3) & (pass_df['x'] < 200/3)

    #JK definition
    point1 = ~((pass_df['x'] >= 83) & (pass_df['y'] >= 21.1) & (pass_df['y'] <= 78.9))
    point2 = (pass_df['endX'] >= 83) & (pass_df['endY'] >= 21.1) & (pass_df['endY'] <= 78.9)
    pass_df['ppa'] = 0  # Initialize the 'ppa' column with default value
    # Assign 1 to 'ppa' for rows that satisfy the conditions
    pass_df.loc[point1 & point2, 'ppa'] = 1
    return pass_df