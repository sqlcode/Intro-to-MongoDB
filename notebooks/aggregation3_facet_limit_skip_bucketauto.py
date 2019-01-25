# -*- coding: utf-8 -*-

"""
MongoDB Aggregation Framework demo3.

$facet, $limit, $skip and $bucketAuto stages demo
"""

__author__ = 'Ziang Lu'

import pprint

from pymongo import MongoClient

DB = 'mflix'
PASSWORD = 'Zest2016!'

conn_uri = 'mongodb://zianglu:' + PASSWORD + '@cluster0-shard-00-00-hanbs.mongodb.net:27017,cluster0-shard-00-01-hanbs.mongodb.net:27017,cluster0-shard-00-02-hanbs.mongodb.net:27017/' + \
    DB + '?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true'

cli = MongoClient(conn_uri)
movies_initial = cli.mflix.movies_initial

# Define top 100 language combinations as "usual"
TOP_LANGUAGE_COMBINATIONS = 100
# Rest: Unusual language combinations

# Main pipeline
pipeline = [
    {
        '$sortByCount': '$language'
    },  # stage1: 'sortByCount' stage

    # $facet stage processes the same input documents through multiple pipelines
    # in parallel.
    {
        '$facet': {  # Define multiple pipelines
            # pipeline1: 'top language combinations'
            'top language combinations': [
                {'$limit': TOP_LANGUAGE_COMBINATIONS}  # stage2.1: 'limit' stage
            ],
            # pipeline2: 'unsual combinations shared by'
            'unusual combinations shared by': [
                {'$skip': TOP_LANGUAGE_COMBINATIONS},  # 'skip' stage
                {'$bucketAuto': {
                    'groupBy': '$count',  # Identifier expression to group by
                    'buckets': 5,  # Create <= 5 buckets
                    # This will automatically calculate the range for each
                    # bucket, and put documents within the same range to the
                    # same bucket.
                    'output': {'language combinations': {'$sum': 1}}
                    # For each bucket, it will output the value we specified for
                    # the "output" key.
                }}  # stage2.2: 'bucketAuto' stage
            ]
        }
    }  # stage2: 'facet' stage
]

for result in movies_initial.aggregate(pipeline):
    pprint.pprint(result)
