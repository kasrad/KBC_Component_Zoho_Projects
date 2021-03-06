#==============================================================================
from datetime import datetime, timedelta
import pytz
import json
import requests
import pandas as pd
import time 
import numpy as np
from pandas.io.json import json_normalize
#==============================================================================

#Authorization settings
with open('data.txt', 'r') as myfile:
    API_token=myfile.read().replace('\n', '')

parameters = {  'authtoken': API_token,
                'flag': 'internal'}


#==============================================================================
#Functions for extracting data from specific endpoints
#==============================================================================
def get_data_projects(target_df, endpoint, to_append,  url=''):

    req = requests.get(url=url, params=parameters)

    if req.status_code != 200:
        print('Warning: The returned status code is: ' + str(req.status_code))
        return(target_df)

    else:
        df_tmp = json_normalize(req.json()[endpoint][0])
        df_tmp['parent'] = to_append

    if target_df.empty:
        target_df = df_tmp
    else:
        target_df = target_df.append(df_tmp)

    return(target_df)

def get_data_tasklists(target_df, endpoint, to_append, url = ''):
    
    
    req = requests.get(url = url, params = parameters)

    if req.status_code != 200:
        print('Warning: The returned status code is: ' + str(req.status_code))
        return(target_df)

    else:
        df_tmp = json_normalize(req.json()[endpoint])
        df_tmp['parent'] = to_append
    
    if target_df.empty:
        target_df = df_tmp
    else:
        target_df = target_df.append(df_tmp)
  
    return(target_df)
        
def get_data_tasks(target_df, endpoint, to_append, url = ''):
    
    
    req = requests.get(url = url, params = parameters)
    
    if req.status_code != 200:
        print('Warning: The returned status code is: ' + str(req.status_code))
        return(target_df)
    
    else:
        df_tmp = json_normalize(req.json()[endpoint])
        df_tmp['parent'] = to_append
    
    
    if target_df.empty:
        target_df = df_tmp
    else:
        target_df = target_df.append(df_tmp)
  
    return(target_df)

def get_data_timelogs(target_df, endpoint, to_append, url = ''):
    
    req = requests.get(url = url, params = parameters)
    
    if req.status_code != 200:
        print('Warning: The returned status code is: ' + str(req.status_code))
        return(target_df)
    
    else:
        df_tmp = json_normalize(req.json()[endpoint]['tasklogs'])
        df_tmp['parent'] = to_append
    
    
    if target_df.empty:
        target_df = df_tmp
    else:
        target_df = target_df.append(df_tmp)
  
    return(target_df)
        

#Extract data for projects
url = 'https://projectsapi.zoho.eu/restapi/portal/20061034739/projects/'
req = requests.get(url=url, params=parameters)
base_df = json_normalize(req.json()['projects'])


projects_info = pd.DataFrame(np.zeros((0, 0)))
for i in base_df['link.self.url']:
    projects_info = get_data_projects(target_df=projects_info,
                                      url=i, endpoint='projects',
                                      to_append='Keboola')

#Extract data for tasklists
tasklists_info = pd.DataFrame(np.zeros((0,0)))
for counter, i in enumerate(projects_info['link.tasklist.url']):
    tasklists_info = get_data_tasklists(target_df = tasklists_info, url = i,
                              endpoint = 'tasklists', to_append = projects_info['id'].iloc[counter])

#Extract data for tasks
tasks_info = pd.DataFrame(np.zeros((0,0)))
for counter, i in enumerate(tasklists_info['link.task.url']):
    tasks_info = get_data_tasks(target_df = tasks_info, url = i,
                                endpoint = 'tasks',
                                to_append = tasklists_info['id'].iloc[counter])

#Extract data for timelogs
timelogs_info = pd.DataFrame(np.zeros((0,0)))
for counter, i in enumerate(tasks_info['link.timesheet.url']):
    timelogs_info = get_data_timelogs(target_df = timelogs_info, url = i,
                                endpoint = 'timelogs',
                                to_append = tasks_info['id'].iloc[counter])

