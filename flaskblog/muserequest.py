# -*- coding: utf-8 -*-
"""

This class is responsible for requesting and processing API requests.
https://www.themuse.com/developers/api/v2

@author: JBB Team
"""

import requests
from requests.exceptions import HTTPError
import pandas as pd
import re

class MuseRequest:
    muse_link = 'https://www.themuse.com/api/public/jobs?'
    
    def __init__(self, position_name, category, page, level):
        self.position_name = position_name.replace(" ", "+")
        '''
        accepted values for category are ["Account Management", "Creative & Design", "Data Science", "Education",
        "Finance", "Healthcare & Medicine", "Legal","Operations", "Retail","Social Media & Community",
        "Business & Strategy","Customer Service","Editorial","Engineering","Fundraising & Development","HR & Recruiting",
        "Marketing & PR", "Project & Product Management", "Sales"]
        '''
        self.category = category.replace(" ", "+") 
        self.page = page
        '''
        accepted values for level are 
        ["Entry level", "Senior level", "Mid level", "Internship", "management"]
        '''
        self.level = level.replace(" ", "+")  
  
    # Method to remove HTML tags
    TAG_RE = re.compile(r'<[^>]+>')
    def remove_tags(text):
        return TAG_RE.sub('', text)
        
    def create_link(self):
        link = f'{self.muse_link}position_name={self.position_name}&category={self.category}&page={self.page}&level={self.level}'
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
        
    def get_jobs(self, response):
        job_storage = pd.DataFrame(columns=['title','description','company_name','date_posted','link','source'])
        title = list()
        description = list()
        company_name = list()
        date_posted = list()
        link = list()
        jobs = response['results']
        for row in jobs:
            for key, value in row.items():
                if key == "name":
                    title.append(value)
                elif key == "contents":
                    description.append(value)
                elif key == "company":
                    if type(value) is dict:
                        for item, company in value.items():
                            if item == "name":
                                company_name.append(company)
                    else:
                        company_name.append(value)
                elif key == "publication_date":
                    date_posted.append(value)
                elif key == "refs":
                    if type(value) is dict:
                        for item, ref in value.items():
                            if item == "landing_page":
                                link.append(ref)
                    else:
                        link.append(ref)
        job_storage['title'] = title
        job_storage['description'] = description
        job_storage['company_name'] = company_name
        job_storage['date_posted'] = date_posted
        job_storage['link'] = link
        job_storage['source'] = 'TheMuse Jobs'   
        
        # FILTERING
        red_flag_words = ['TS/SCI', 'clearance',
            'DoD SECRET','SECRET','Federal Government',
            'Department of Defense','federal contractor',
            'US Citizen','U.S. citizen','Government',
            'DHS','VEVRAA']
        job_storage.drop(job_storage[job_storage['description'].astype(str).str.contains('|'.join(red_flag_words), case=False, na=False) | 
                                   job_storage['date_posted'].astype(str).str.contains('2020') != True].index, inplace=True)
        return job_storage


