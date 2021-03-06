# -*- coding: utf-8 -*-

"""
MongoDB Aggregation Framework demo4.

$project stage demo
"""

__author__ = 'Ziang Lu'

from pymongo import MongoClient

DB = 'mflix'
PASSWORD = 'Zest2016!'

conn_uri = 'mongodb://zianglu:' + PASSWORD + '@cluster0-shard-00-00-hanbs.mongodb.net:27017,cluster0-shard-00-01-hanbs.mongodb.net:27017,cluster0-shard-00-02-hanbs.mongodb.net:27017/' + \
    DB + '?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true'

cli = MongoClient(conn_uri)
movies_initial = cli.mflix.movies_initial

pipeline = [
    {
        '$limit': 100
    },  # stage1: 'limit' stage
    # $project stage can be used to do data transformation, e.g., cleaning up
    # the raw (messy) data, and maybe reshaping the data to what we desire.
    {
        '$project': {
            'title': 1,  # Keep it as it is
            'poster': 1,
            'genres': {'$split': ['$genre', ', ']},  # Split the "genre" field from a string literal to an array
            'plot': 1,
            'fullPlot': '$fullplot',  # (Rename)
            'directors': {'$split': ['$director', ', ']},
            'actors': {'$split': ['$cast', ',']},
            'writers': {'$split': ['$writer', ',']},
            'year': 1,
            'released': 1,
            'languages': {'$split': ['$language', ',']},
            'countries': {'$split': ['$country', ',']},
            'runtime': 1,
            'imdb': {
                'id': '$imdbID',
                'rating': '$imdbRating',
                'votes': '$imdbVotes'
            },  # Reshape some fields into one single field (one single embedded document)
            'rated': '$rating',
            'awards': 1,
            'lastUpdated': '$lastupdated'
        }
    },  # stage2: 'project' stage
    {
        '$out': 'movies_processed'
    }  # stage3: 'out' stage
]

# Since we already dump out the result to "movies_processed" collection, we
# don't need to iterate over the result.
movies_initial.aggregate(pipeline)
