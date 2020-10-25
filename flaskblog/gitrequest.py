# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 17:19:36 2020

This class is responsible for requesting and processing API requests.
https://jobs.github.com/api

@author: abbos
"""

import requests
from requests.exceptions import HTTPError
import pandas as pd
import re



class GitRequest:
    github_link = 'https://jobs.github.com/positions.json?'
    
    def __init__(self, description, location, full_time=False):
        self.description = description.replace(" ", "+")
        self.location = location.replace(" ", "+")
        self.full_time = full_time

    # Method to remove HTML tags
    TAG_RE = re.compile(r'<[^>]+>')
    def remove_tags(text):
        return TAG_RE.sub('', text)

    
    def create_link(self):
        link = f'{self.github_link}description={self.description}&location={self.location}&full_time={self.full_time}'
        return link
    
    def make_request(self, link):
        try:
            response = requests.get(link)
            jsonResponse = response.json()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        finally:
            return jsonResponse
        
    def get_table(self, response):
        job_storage = pd.DataFrame(columns=['title','description','company_name','date_posted','link','source'])
        title = list()
        description = list()
        company_name = list()
        date_posted = list() 
        link = list()
        for i in response:
            for key, value in i.items():
                if key == 'title':
                    title.append(value)
                elif key == 'description':
                    description.append(value)
                elif key == 'company':
                    company_name.append(value)
                elif key == 'created_at':
                    date_posted.append(value)
                elif key == 'how_to_apply':
                    link.append(value)
        job_storage['title'] = title
        job_storage['description'] = description
        job_storage['company_name'] = company_name
        job_storage['date_posted'] = date_posted
        job_storage['link'] = link
        job_storage['source'] = 'GitHub Jobs'
        
        # FILTERING
        red_flag_words = ['TS/SCI', 'clearance',
            'DoD SECRET','SECRET','Federal Government',
            'Department of Defense','federal contractor',
            'US Citizen','U.S. citizen','Government',
            'DHS','VEVRAA']
        job_storage.drop(job_storage[job_storage['description'].astype(str).str.contains('|'.join(red_flag_words), case=False, na=False) | 
                                   job_storage['date_posted'].astype(str).str.contains('2020') != True].index, inplace=True)
        return job_storage


