import pandas as pd
import numpy as np
from os.path import join as oj

def load_daily_data(usafacts_data_cases='usafacts/confirmed_cases.csv',
                    usafacts_data_deaths='usafacts/deaths.csv',
                    dir_mod = ""):
    usafacts_data_cases = oj(dir_mod, usafacts_data_cases)
    usafacts_data_deaths = oj(dir_mod, usafacts_data_deaths)
  
    cases = pd.read_csv(usafacts_data_cases, encoding="iso-8859-1", index_col=0).T
    deaths = pd.read_csv(usafacts_data_deaths, encoding="iso-8859-1", index_col=0).T
    if not 'countyFIPS' in deaths.keys():
        deaths = pd.read_csv(usafacts_data_deaths, encoding="utf-8", index_col=0).T
    # change to int type
    for col in cases.columns:
        if not 'county' in col.lower() and not 'state' in col.lower():
            if col[-4:] != '2020':
                cases = cases.rename(columns = {col: col + '20'})
                col = col + '20'
            cases[col] = cases[col].astype(float).astype(int)
    for col in deaths.columns:
        if not 'county' in col.lower() and not 'state' in col.lower():
            if col[-4:] != '2020':
                deaths = deaths.rename(columns = {col: col + '20'})
                col = col + '20'
            deaths[col] = deaths[col].astype(float).astype(int)
    # rename column names
    cases = cases.rename(columns={k: '#Cases_' + k for k in cases.keys()
                                  if not 'county' in k.lower()
                                  and not 'state' in k.lower()})

    deaths = deaths.rename(columns={k: '#Deaths_' + k for k in deaths.keys()
                                    if not 'county' in k.lower()
                                    and not 'state' in k.lower()})

    deaths.countyFIPS = deaths.countyFIPS.astype(int)
    cases.countyFIPS = cases.countyFIPS.astype(int)
    cases = cases[cases.countyFIPS != 0]  # ignore cases where county is unknown
    cases = cases.groupby(['countyFIPS']).sum().reset_index()  # sum over duplicate counties
    deaths = deaths[deaths.countyFIPS != 0]
    deaths = deaths.groupby(['countyFIPS']).sum().reset_index()

    df = pd.merge(cases, deaths, how='left', on='countyFIPS')
    df = df.fillna(0)
    
    # add time-series keys
    deaths_keys = [k for k in df.keys() if '#Deaths' in k and not 'Unnamed' in k]
    cases_keys = [k for k in df.keys() if '#Cases' in k and not 'Unnamed' in k]
    deaths = df[deaths_keys].values
    cases = df[cases_keys].values
    df['deaths'] = [deaths[i] for i in range(deaths.shape[0])]
    df['cases'] = [cases[i] for i in range(cases.shape[0])]
    df['tot_deaths'] = deaths[:, -1]
    df['tot_cases'] = cases[:, -1]
    return df
