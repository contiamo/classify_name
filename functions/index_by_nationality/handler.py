import datetime
import graphene
import json
import os
import pathlib
import sys

import pandas as pd
from typing import List, Any

# add common to bundle root
bundle_root = pathlib.Path(os.environ['LABS_BUNDLE_ROOT'])
sys.path.append(str(bundle_root / 'common'))
# load data
movies = pd.read_parquet(bundle_root / 'common/movies_metadata.parquet').drop_duplicates(subset=['id']).sort_values('id').set_index('id')
crew = pd.read_parquet(bundle_root / 'common/crew_with_nationality.parquet').sort_values(['nationality','job']).set_index(['nationality','job']) 
# define metadata
nationality_list = crew.index.get_level_values(0).unique()
job_list =crew.index.get_level_values(1).unique()   

# output type
class movie(graphene.ObjectType):
    title = graphene.String(required=True)
    revenue = graphene.Int(required=True)
    def __init__(self, row):  
        self.title = row['title']
        self.revenue = row['revenue']
        
class Query(graphene.ObjectType):
    
    ## graphene 
    nationality_list = graphene.List(graphene.String, required=True, )
    job_list = graphene.List(graphene.String, required=True)   
    movie_list = graphene.List(movie,
                               nationality = graphene.String(default_value='English', required=False),
                               job = graphene.String(default_value='Director', required=False)
                              )
    
   
                        
    def resolve_nationality_list(self, info):
        return nationality_list
    
    def resolve_job_list(self, info):
        return job_list    
    
    def resolve_movie_list(self, info, nationality, job):     
        movie_info = (movies
                         .reindex(crew.loc[(nationality, job), 'movie_id'])
                         .dropna(axis='rows')
                         .groupby('title')['revenue']
                         .sum()
                         .nlargest(3)
                         .to_frame()
                         .reset_index()
                     )  
        return [movie(row) for _, row in movie_info.iterrows()]        
    
schema = graphene.Schema(query=Query, types=[movie])
default_query = """query metadata {nationalityList, jobList}"""

def handle(input_json: str) -> str:  
    # parse input
    try:
        input_dict = json.loads(input_json)
    except ValueError as e:
        return 'Input must be json.'    
    # get variables, query
    variables = input_dict.get('variables', None)
    query = input_dict.get('query', '').replace('\\n', '').replace('\n', '')
    # execute query
    output = schema.execute(query, variables=variables )
    
    return json.dumps({'data': output.data, 'errors': output.errors})



