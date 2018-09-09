#! /usr/bin/env python3
#
# Copyright © 2018 dgarner <dgarner@mdx>
#
# Distributed under terms of the MIT license.

"""
Compares 2018 Crossfit Open data for athletes who also competed in
2018 TFX Qualifier. Intent is to help determine division boundaries
for althletes deciding which TFX division to compete in for 2019.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as mp
import seaborn as sb

# Inputs
sex = 'M'

# Data
pro  = {'M': 30, 'W': 20}
ama  = {'M': 80, 'W': 50}
intr = {'M': 85, 'W': 60}
scl  = {'M': 60, 'W': 40}


def main():
    # Get data
    op = pd.read_csv("Results_{}_WorldWide_Latest_Open2018.csv".format(sex))
    pa = pd.read_csv("tfx_qualifier_PA{}_2018.csv".format(sex))
    si = pd.read_csv("tfx_qualifier_IS{}_2018.csv".format(sex))
    #print(op.head())
    #print(pa.head())
    #print(si.head())
    #print(op.shape)

    # Analyze individuals
    #anz = op[['competitorName', 'rank_E1', 'score_E1', 'rank_E2', 'score_E2','rank_E3', 'score_E3', 'rank_E4', 'score_E4', 'rank_E5', 'score_E5', 'rank_E6', 'score_E6']]
    #print(anz[anz['competitorName'] == 'Mark Garner'])

    # Drop NaN data
    #op = op.dropna(how='any', subset=['rank_E1', 'rank_E2', 'rank_E3', 'rank_E4', 'rank_E5', 'rank_E6'])
    #print(op.shape)

    # Drop Open athletes that didnt complete every event
    for i in range(6):
        op = op[op['rank_E{}'.format(i+1)] != op['rank_E{}'.format(i+1)].max()]
        op = op[op['score_E{}'.format(i+1)] != 0.0]
    #print(op.shape)

    # Pair down data
    op = op[['competitorName', 'overallRank', 'regionId']]
    pa = pa[['Athlete', 'Rank']]
    si = si[['Athlete', 'Rank']]
    #print(op.head())
    #print(pa.head())
    #print(si.head())
    #print(pa)
    #print(op.shape)
    #print(pa.shape)
    #print(si.shape)

    # Drop Duplicates
    pa = pa.drop_duplicates(subset='Athlete', keep='first')
    si = si.drop_duplicates(subset='Athlete', keep='first')
    #print(pa.shape)
    #print(si.shape)

    # Rename columns
    op.rename({'competitorName': 'Athlete', 'overallRank': 'Open'}, axis=1, inplace=True)
    pa.rename({'Rank': 'TFX'}, axis=1, inplace=True)
    si.rename({'Rank': 'TFX'}, axis=1, inplace=True)
    #print(op.head())
    #print(pa.head())
    #print(si.head())

    # Correct Althlete Names
    si.replace(to_replace='Robert Alvarez', value='Roberto Alvarez Jr', inplace=True) # guess

    # Merge
    pa = pa.merge(op, how='inner', on='Athlete')
    si = si.merge(op, how='inner', on='Athlete')
    #print(si.head())
    #print(pa.head())
    #print(si.head())
    #print(pa.shape)
    #print(si.shape)

    # Drop duplicates in favor of athlete in South Central region
    pa = select_sc(pa)
    si = select_sc(si)
    #print(pa.shape)
    #print(si.shape)
    #print(pa)
    #print(si)

    # Drop outliers
    pa = pa.drop(pa[pa['Athlete'] == 'Marco Coppola'].index) # Score 1 rep in last 3 open events
    pa = pa.drop(pa[pa['Athlete'] == 'Mark Stewart'].index) # In Austrailasia region, probably didn't compete in the open
    si = si.drop(si[si['Athlete'] == 'Mark Garner'].index) # Probably didn't compete in the open

    # Sort
    pa = pa.sort_values('TFX', ascending=True)
    si = si.sort_values('TFX', ascending=True)
    pa = pa.reset_index().drop('index', 1)
    si = si.reset_index().drop('index', 1)

    p_q = get_index(pa, pro[sex])
    pa_q = get_index(pa, pro[sex]+ama[sex])
    i_q = get_index(si, intr[sex])
    si_q = get_index(si, intr[sex]+scl[sex])
    p = pa[:p_q]
    a = pa[p_q:pa_q]
    i = si[:i_q]
    s = si[i_q:si_q]
    #print(p)
    #print(a)
    #print(i)
    #print(s)

    # Plot
    #pa.plot.scatter('Open', 'TFX')
    #si.plot.scatter('Open', 'TFX')
    #pa[:pa_q].plot.kde()
    #si[:si_q].plot.kde()

    #title = 'Men: 2018 TFX Qualifier Rank vs 2018 Open Rank - Qualified'# {}'.format(sex)
    #mp.figure(title)
    #mp.title(title)
    #mp.plot(p['Open'], p['TFX'], '.b', label='Pro')
    #mp.plot(a['Open'], a['TFX'], '.r', label='Amateur')
    #mp.plot(i['Open'], i['TFX'], '.k', label='Int')
    #mp.plot(s['Open'], s['TFX'], '.g', label='Scaled')
    #mp.xlabel('Open Rank')
    #mp.ylabel('TFX Qualifier Rank')
    #mp.legend()

    ##
    #title = '2018 TFX Qualifier Rank vs 2018 Open Rank - All {}'.format(sex)
    #mp.figure(title)
    #mp.title(title)
    #mp.plot(pa['Open'], pa['TFX'], '.b', label='Pro-Amateur')
    #mp.plot(si['Open'], si['TFX'], '.k', label='Int-Scaled')
    #mp.xlabel('Open Rank')
    #mp.ylabel('TFX Qualifier Rank')
    #mp.legend()

    #mp.xkcd()
    title = '2018 Open Rank Per TFX Qualifier Division - All {}'.format(sex)
    #title = 'Women: 2018 Crossfit Open Rank for TFX Qualifier Divisions'# {}'.format(sex)
    mp.figure(title)
    mp.title(title)
    mp.boxplot([pa[:pa_q]['Open'], si[:si_q]['Open']], labels=["Pro-Ama", "Int-Scl"], whis=[5, 95], showfliers=False, vert=False)
    mp.xlabel('Crossfit Open Worldwide Rank')
    mp.ylabel('TFX Qualifier Division')
    mp.legend()

    title = '2018 Crossfit Open Rank Distributions for TFXQ Divisions {}'.format(sex)
    mp.figure(title)
    mp.title(title)
    #sb.kdeplot(pa[:pa_q]['Open'], clip=[0, 100000])
    #sb.kdeplot(si[:si_q]['Open'], clip=[0, 100000])
    sb.distplot(pa[:pa_q]['Open']).set(xlim=[0, 100000])
    sb.distplot(si[:si_q]['Open']).set(xlim=[0, 100000])

    # Stats
    #print('Pro {}.format(sex)')
    #print(p.describe(percentiles=[0.05, 0.95])['Open'])
    #print('Amatuer {}.format(sex)')
    #print(a.describe(percentiles=[0.05, 0.95])['Open'])
    #print('Intermediate {}.format(sex)')
    #print(i.describe(percentiles=[0.05, 0.95])['Open'])
    #print('Scaled {}.format(sex)')
    #print(s.describe(percentiles=[0.05, 0.95])['Open'])
    print('Pro-Amature {}'.format(sex))
    print(pa[:pa_q].describe(percentiles=[0.05, 0.1, 0.9, 0.95])['Open'])
    print('Int-Scaled {}'.format(sex))
    print(si[:si_q].describe(percentiles=[0.05, 0.1, 0.9, 0.95])['Open'])

    mp.show()

def get_index(df, x):
    return df.index[df['TFX'] <= x].tolist()[-1]

def select_sc(pa):
    pa['SC'] = (pa['regionId'] == 14)
    pa = pa.sort_values('SC', ascending=False)
    #print(pa)
    pa = pa.drop_duplicates(subset='Athlete', keep='first').drop(['regionId', 'SC'], 1)
    #print(pa.shape)
    pa = pa.sort_values('Open', ascending=True).drop_duplicates(subset='Athlete', keep=False)
    #print(pa.shape)
    #print(pa)
    return pa

if __name__ == '__main__':
    main()
