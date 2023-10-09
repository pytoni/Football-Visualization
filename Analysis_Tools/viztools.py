#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"></ul></div>

# In[12]:
"""Module containing functions to generate football data anlytics visuals.

Functions:
    shot_map_xg : Plot shot map
---------

"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import matplotlib.patches as patch
from matplotlib import transforms, patches
from mplsoccer import Pitch, VerticalPitch, FontManager
from scipy.interpolate import make_interp_spline
from matplotlib.colors import to_rgba
import matplotlib.ticker as ticker
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import urllib

from urllib.request import urlopen

import json
import re
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import ConvexHull
from scipy import stats
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
h_color = '#1984c5'
a_color = '#c23728'
cred = '#FF3333'
cblue = '#0092CC'
cyellow = '#DCD427'
cgreen = '#779933'

def shot_map_xg(data, 
                playerId=None, teamId=None, match_id=None, 
                orientation='v', 
                ax='T', 
                plot_title_size=12, y=0.98,
                s=100, 
                lw=0.5, 
                fontsize=8,  
                bgcolor='#0D182E', 
                alpha=0.8):
    """
    Function to plot Shot map from a whoscored-style event dataframe (from one or multiple matches)
    
    Args:
        data: events_df or xG_df (pandas.DataFrame) whoscored-style dataframe of event data with or without Expected Goal (xG) value .
        playerId: playerId, default is None
        teamId: default is None
        match_id: default is None
        orientation: 'v' or 'h' orientation of the pitch 
        ax: 'T'
        plot_title_size: Plot title font size, default is 12 
        y: position of Plot title along y-axis, default is 0.98
        s: size of shot position, default is 100 
        lw: linewidth of shot direction, default is 0.5 
        fontsize: font size, defaut is 8
        bgcolor: background color of plot, default is '#0D182E'
                
    """     
    df = data.copy()  
    if match_id:
        df = df[df['match_id']==match_id]
    if teamId:
        df = df[df['teamId']==teamId] 
    if playerId:
        df = df[df['playerId']==playerId] 
        
    hid = data[data['home_team_id']>0]['home_team_id'].unique()
    hid = hid[0]
    aid = data[data['away_team_id']>0]['away_team_id'].unique()
    aid=aid[0]
    
    #options for background color
    if bgcolor == 'white':
        fontcolor = 'black'
    else:
        fontcolor = 'white'
        
    pitch = Pitch(pitch_type='opta', pitch_color=bgcolor, line_color='#5B6378', linewidth=0.5)
    
    if ax=='T': 
        #set up the pitch
        fig, ax = plt.subplots(figsize=(10,6))
        fig.set_facecolor(bgcolor)
        ax.patch.set_facecolor('#0D182E')
                
    pitch.draw(ax=ax)  
    
    # Get shot events
    df = df[df['isShot']== True].reset_index(drop=True)
    
    # Set goalMouthX
    df['goalMouthX']=100
    
    # Change teamid if owngoal
    for idx, row in df.iterrows():
        if row.is_own_goal==True:
            row.x = 100.0 - row.x
            if row.teamId == hid:
                row.teamId = aid
            else:
                row.teamId = hid
                  
    h_df = df[df['teamId']==hid]
    h_df.reset_index(drop=True, inplace=True)

    a_df = df[df['teamId']==aid]
    a_df.reset_index(drop=True, inplace=True)
    a_df['x']=100-a_df['x']
    a_df['y']=100-a_df['y']
    a_df['goalMouthY']=100-a_df['goalMouthY']
    a_df['blockedX']=100-a_df['blockedX']
    a_df['blockedY']=100-a_df['blockedY']
    a_df['goalMouthX']=0
    
    # Plot shots 
    for idx, row in h_df.iterrows():
        if row.isGoal==True:
            S = row.xG * s if 'xG' in h_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, marker='football', c='orange', s=S, edgecolor='white', linewidth=0.5, alpha=0.9, zorder=120, ax=ax)
            pitch.lines(row.x, row.y, row.goalMouthX, row.goalMouthY, color='orange', 
                        linewidth=lw, alpha=alpha, zorder=5, ax=ax)
        elif row.isblocked==True:
            S = row.xG * s if 'xG' in h_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, facecolor='none', s=S, edgecolor=h_color, linewidth=0.8, zorder=5, ax=ax)
            pitch.lines(row.x, row.y, row.blockedX, row.blockedY, color=h_color, 
                        linewidth=lw, alpha=alpha, ax=ax)
            pitch.scatter(row.blockedX, row.blockedY, facecolor=h_color, s=5, marker='x', edgecolor=h_color, linewidth=0.8, zorder=5, ax=ax)
        elif row.type=='MissedShots':
            S = row.xG * s if 'xG' in h_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, facecolor='none', s=S, edgecolor=h_color, linewidth=0.8, zorder=5, ax=ax)
            pitch.lines(row.x, row.y, row.goalMouthX, row.goalMouthY, color='gray',linestyle='dashed',
                        linewidth=lw, alpha=alpha, ax=ax)
        else:
            S = row.xG * s if 'xG' in h_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, facecolor='none', s=S, edgecolor=h_color, linewidth=0.8, zorder=5, ax=ax)
            pitch.lines(row.x, row.y, row.goalMouthX, row.goalMouthY, color=h_color, 
                        linewidth=lw, alpha=alpha, ax=ax)

    for idx, row in a_df.iterrows():
        if row.isGoal==True:
            S = row.xG * s if 'xG' in a_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, marker='football',c='orange', s=S, edgecolor='white', linewidth=0.5, alpha=0.9, zorder=12, ax=ax)
            pitch.lines(row.x, row.y, row.goalMouthX, row.goalMouthY, color='orange',
                        linewidth=lw, alpha=alpha, ax=ax)
        elif row.isblocked==True:
            S = row.xG * s if 'xG' in a_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, facecolor='none', s=S, edgecolor=a_color, linewidth=0.8, zorder=5, ax=ax)
            pitch.lines(row.x, row.y, row.blockedX, row.blockedY, color=a_color,  
                        linewidth=lw, alpha=alpha, ax=ax)
            pitch.scatter(row.blockedX, row.blockedY, facecolor=a_color, s=5, marker='x', edgecolor=a_color, linewidth=0.8, zorder=5, ax=ax)
        elif row.type=='MissedShots':
            S = row.xG * s if 'xG' in a_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, facecolor='none', s=S, edgecolor=a_color, linewidth=0.8, zorder=5, ax=ax)
            pitch.lines(row.x, row.y, row.goalMouthX, row.goalMouthY, color='gray', linestyle='dashed',
                       linewidth=lw, alpha=alpha, ax=ax)
        else:
            S = row.xG * s if 'xG' in a_df.columns else 0.1 * s
            pitch.scatter(row.x, row.y, facecolor='none', s=S, edgecolor=a_color, linewidth=0.8, zorder=5, ax=ax)
            pitch.lines(row.x, row.y, row.goalMouthX, row.goalMouthY, color=a_color,
                        linewidth=lw, alpha=alpha, ax=ax)  
    if ax=='T':
        plt.show()
        
