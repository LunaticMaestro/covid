# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # COVID-19 DEATH RATE INDIA
# 
# This jupyter book tests the bits of the program which ensembles the 
# data from `Ministry of Health & Family Welfare India` for COVID-19 spread summary
# 
# STANDARDS
#  - Date_Format  `DD Month YYYY`
#  
# VERSION 3.0
#  - 31 MAR 2020
#  - source site formate changed
#  - date format changed
#
#  - 24hrs time format GMT+5:30
# VERSION 2.0
#  -  22 MAR 2020
#  - Source site formate changed
# 
# VERSION 1.0
#  - 19 MAR 2020
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

# %% [markdown]
# ### META INFO *snapshot*
# ![ref img: /log/screenshots](data_src_22_03_2020.png)
# 
# ### STATE-WISE INFORMAITION *snapshot*
# ![ref img: /log/screenshots](data_src_22_03_2020_2.png)
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


# %%
# Extracting date, time, remakrs
remark = crude_data.find('div', attrs = {'class': 'status-update'}).find('span').text
meta_date = re.findall("[0-3][0-9] [a-zA-Z]* 202[0-9]", remark)    # DD-MM-YYYY formation
meta_time = re.findall(" [0-9][0-9]:[0-9][0-9] ", remark)              # 12-hours HH:MM AM/PM
observation['date'] = meta_date
observation['time'] = meta_time
observation['remark'] = [remark]
print(observation)


# %%
# Extracting informations of the META_DATA set
# Block last inspected date 22-03-2020
block = crude_data.find('div', attrs = {'class': 'site-stats-count'}).findAll('li')

for row in block[:-1]:
    val = row.find('strong').text
    col = row.find('span').text
    try:
        observation[col.strip()] = [ int(val.replace(',', '')), ]   # indian number system uses <comma> as separated for lakh,thousands
    except ValueError :
        observation[col.strip()] = [ val, ]   # indian number system uses <comma> as separated for lakh,thousands

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
# Extracting each observation and appending to observations
rows = crude_data.find('section', attrs= {'id': 'state-data'}).find('table', attrs = {'class': 'table table-striped'}).findAll('tr')
rows[1]
observations = []
for row in rows[1:-1]:    # 1st or 0th index belongs to header, last row refers to summed info (total)
    observation = {}
    values = row.text.strip('\n')
    values = values.replace(",", '')
    values_list  = values.split('\n')
    observation['date'] = meta_date[0]
    observation['time'] = meta_time[0]
    observation['Name of State / UT'] = str(values_list[1])
    observation['Total Confirmed cases (Indian National)'] = (values_list[2])
    observation['Cured/Discharged/Migrated'] = (values_list[3])
    observation['Death'] = (values_list[4])
    observations.append(observation)
print(observation)

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


# %%


