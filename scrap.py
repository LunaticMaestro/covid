# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # COVID-19 DEATH RATE INDIA
# 
# This jupyter book tests the bits of the program which ensembles the 
# data from `Ministry of Health & Family Welfare India` for COVID-19 spread summary
# 
# STANDARDS
#  - Date_Format  `DD-MM-YYYY`
#  
# VERSION 1.0
#  - 19 MAR 20220
#  - Base program
#  - column value hardcoded due to heterogenous data

# %%
# libraries for the soup
import pandas as pd     # creating structured data
import requests         # fetching the page containing data
import re               # dissecting data
from bs4 import BeautifulSoup   # parsing the page to ease data extractioin


# %%
# checking connections
try:
    url = "https://www.mohfw.gov.in/"
    response = requests.get(url)
    print("Checking connections ...", response)
    if len(re.findall('200', str(response))) != 0:
        print("CONN OK")
    else: 
        print("CONN ERR\n EXIT")
        quit()
except Exception as e:
    print("Err Establishing Connection, Check connectivity.")
    quit()
# parsing retrieved html with beautiful soup
crude_data = BeautifulSoup(response.text, 'html.parser')


# %%
# Section last inspected date 19-03-2020
section = crude_data.findAll('ol', attrs = {'dir': 'ltr'})[0]
section

# %% [markdown]
# ![ref img: /log/screenshots](data_src_19_03_2020.png)
# %% [markdown]
# ## 1. Extracting META INFO
# 
# >each `META_DATA` set:
# - Total number of passengers screened at airport
# - Total number of Active COVID 2019 cases across India
# - Total number of Discharged/Cured COVID 2019 cases across India
# - Total number of Migrated COVID-19 Patient
# - Total number of Deaths due to COVID 2019 across India
# - remarks , *example* `(*including foreign nationals, as on 19.03.2020 at 05:00 PM)` 
#     - (self created column)
#     - data as its from source page
#     - this is parse to extract data and time information
# 
# Each set of above data is an `observation`

# %%
# Dictionary for storing set of observations
observation = dict()
#
# Extracting date, time, remakrs
meta_info  = section.findAll('p')
meta_date_time = meta_info[-1].text     
meta_date = re.findall("[0-3][0-9][.][0-1][0-9][.]202[0-9]", meta_date_time)    # DD-MM-YYYY formation
meta_time = re.findall("[0-9][0-9]:[0-9][0-9] [AP]M", meta_date_time)              # 12-hours HH:MM AM/PM
observation['date'] = meta_date
observation['time'] = meta_time
observation['remark'] = list()
observation['remark'].append(meta_date_time)
# print(observation)


# %%
# Extracting other informations of the META_DATA set
meta_info = section.findAll('p')
for info in meta_info[:-1]:
    col, val = info.text.split(":")
    observation[col.strip()] = [ int(val.replace(',', '')), ]   # indian number system uses <comma> as separated for lakh,thousands
print(observation)


# %%
# Loading past observations
file_meta = "covid_meta.csv"
try:
    df_meta = pd.read_csv(file_meta)
except FileNotFoundError:
    print("File 'covid_meta.csv' not found. CREATING")
    df_meta = pd.DataFrame()


# %%
observation


# %%
# Appending new observation with old
df_tmp = pd.DataFrame(observation)
df_meta = df_meta.append(df_tmp, sort=False)
df_meta.to_csv(file_meta, index = False)    # Writing to file


# %%
print("META FILE: OK")
print("PREVIEW")


# %%
# Preview information

df = pd.read_csv(file_meta)
df.set_index(['date', 'time'], inplace= True)
df.tail()

# %% [markdown]
# ## 2. Extracting state wise information
# 
# `observations` is a list of `observation` which has the following set of information.
# 
# 1. S.No. 
# 2. Name of State / UT
# 3. Total Confirmed cases (Indian National)
# 4. Total Confirmed cases ( Foreign National )
# 5. Cured/Discharged/Migrated
# 2. Death

# %%
# Getting column names
# Elementary check for change in table format
header_row = section.findAll('tr')[0]
crude_cols = header_row.findAll('th')
columns = []
for col in crude_cols:
    columns.append(col.text.strip())
if len(columns) != 6:
    print("Expected 6 columns, got ", len(columns))
    print("DATA INTEGRITY MISMATCH, Update Program, Exiting")
    quit()
#print(columns)


# %%
# Extracting each observation and appending to observations
rows = section.findAll('tr')
observations = []
for row in rows[1:-1]:    # 1st or 0th index belongs to header, last row refers to summed info (total)
    observation = {}
    values = row.text.strip('\n')
    values = values.replace(",", '')
    values_list  = values.split('\n')
    observation['date'] = meta_date[0]
    observation['time'] = meta_time[0]
    observation['Name of State / UT'] = str(values_list[1])
    observation['Total Confirmed cases (Indian National)'] = int(values_list[2])
    observation['Total Confirmed cases ( Foreign National )'] = int(values_list[3])
    observation['Cured/Discharged/Migrated'] = int(values_list[4])
    observation['Death'] = int(values_list[5])
    observations.append(observation)
#print(observation)

# %% [markdown]
#  draw a total day wise results when performing data analysis

# %%
# Loading past observations
file_data = "covid.csv"
try:
    df = pd.read_csv(file_data)
except FileNotFoundError:
    print("File 'covid' not found. CREATING")
    df= pd.DataFrame()


# %%
# Appending new observation with old
df_tmp = pd.DataFrame(observations)
df = df.append(df_tmp, sort=False)
df.to_csv(file_data, index = False)    # Writing to file


# %%
print("DATA : OK")


# %%
# Preview information

df = pd.read_csv(file_data)
df.set_index(['date', 'time'], inplace= True)
df.tail()

