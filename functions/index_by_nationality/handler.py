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
movies = (pd
          .read_parquet(bundle_root / 'common/movies_metadata.parquet' ,columns=['title', 'revenue', 'id'])
          .drop_duplicates(subset=['id'])
          .sort_values('id')
          .set_index('id'))
crew = (pd
        .read_parquet(bundle_root / 'common/crew_with_nationality.parquet', columns=['movie_id', 'nationality', 'job', 'name_'])
        .sort_values(['nationality','job'])
        .set_index(['nationality','job']) 
       )
# define metadata
crew = crew.loc[crew.groupby(level=[0,1]).size()[lambda x:x>100].index]
nationality_list = crew.index.get_level_values(0).unique()
job_list = crew.index.get_level_values(1).unique() 
joined_table = movies.join(crew.reset_index().set_index('movie_id'), how='inner')
joined_table_index_crew_member = joined_table.set_index(['nationality', 'job']).sort_index() .dropna(axis='rows')
joined_table_index_crew_detail = joined_table.set_index(['name_']).sort_index().dropna(axis='rows')

# output type
class crew_member(graphene.ObjectType):
    name = graphene.String(required=True)
    aggregate_revenue = graphene.Float(required=True)
    
    def __init__(self, row):  
        self.name = row['name']
        self.aggregate_revenue = row['aggregate_revenue']
        
class crew_detail(graphene.ObjectType):
    movie_title = graphene.String(required=True)
    movie_revenue = graphene.Float(required=True)
    
    def __init__(self, row):  
        self.movie_title = row['title']
        self.movie_revenue = row['revenue']
    
        
class Query(graphene.ObjectType):
    
    ## graphene 
    nationality_list = graphene.List(graphene.String,
                                     required=True,
                                     job=graphene.String(default_value='Director', required=False ))
    job_list = graphene.List(graphene.String,
                             required=True,
                             nationality=graphene.String(default_value='English', required=False ))
    crew_list = graphene.List(crew_member,
                               nationality = graphene.String(default_value='English', required=False),
                               job = graphene.String(default_value='Director', required=False)
                              )
    movie_list = graphene.List(crew_detail,
                               crew_member_name = graphene.String(required=True)
                              )
                        
    def resolve_nationality_list(self, info, job):
        if job:
            nationality_list = crew.xs(job, level=1).index.unique().tolist()
        return nationality_list
    
    def resolve_job_list(self, info, nationality):
        if nationality:
            job_list = crew.xs(nationality, level=0).index.unique().tolist()
        return job_list    
    
    def resolve_crew_list(self, info, nationality, job):     
        top_crew = (joined_table_index_crew_member
                    .loc[[nationality, job]]
                    .dropna(axis='rows')
                    .query('revenue > 1e6')
                    .groupby(['name_'])['revenue']
                    .sum()
                    .nlargest(5)
                    .to_frame('aggregate_revenue')
                    .reset_index()
                    .rename(columns={'name_':'name'})
                   )    
        return [crew_member(row) for _, row in top_crew.iterrows()]        
    
    def resolve_movie_list(self, info, crew_member_name):
        crew_details = (joined_table_index_crew_detail
                        .loc[[crew_member_name]]
                        .groupby(['title'])[['revenue']]
                        .sum()
                        .nlargest(5, 'revenue')
                        .reset_index()
                       )
        return [crew_detail(row) for _, row in crew_details.iterrows()]
        
    
schema = graphene.Schema(query=Query)#, types=[crew_member, crew_detail])


def handle(input_json: str) -> str:  
    # parse input
    try:
        input_dict = json.loads(input_json)
    except ValueError as e:
        return json.dumps({'data': None, 'errors': 'input must be json'}) 
    # get variables, query
    variables = input_dict.get('variables', None)
    
    query = input_dict.get('query', '').replace('\\n', '').replace('\n', '')
    # execute query
    output = schema.execute(query, variables=variables )
    if output.errors:
        errors = [str(err) for err in output.errors]
    else:
        errors = None
    return json.dumps({'data': output.data, 'errors': errors})



