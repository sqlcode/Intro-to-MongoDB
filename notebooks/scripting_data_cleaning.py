# -*- coding: utf-8 -*-

"""
This module achieves the same operations as Aggregation Framework pipeline using
PyMongo scripting.

Note that one key difference is that here we are UPDATING the documents
IN-PLACE, where with Aggregation Framework, we are dumping out the result to
another collection
"""

__author__ = 'Ziang Lu'

from datetime import datetime

from pymongo import MongoClient, UpdateOne

DB = 'mflix'
PASSWORD = 'Zest2016!'
BATCH_SIZE = 1000  # Batch size for batch updating with bulk_write()

conn_uri = 'mongodb://zianglu:' + PASSWORD + '@cluster0-shard-00-00-hanbs.mongodb.net:27017,cluster0-shard-00-01-hanbs.mongodb.net:27017,cluster0-shard-00-02-hanbs.mongodb.net:27017/' + \
    DB + '?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true'

cli = MongoClient(conn_uri)
movies = cli.mflix.movies

single_plural = {
    'genre': 'genres', 'director': 'directors', 'cast': 'actors',
    'writer': 'writers', 'language': 'languages', 'country': 'countries'
}
renaming = {'fullplot': 'fullPlot', 'rating': 'rated'}
imdb_renaming = {
    'imdbID': 'id', 'imdbRating': 'rating', 'imdbVotes': 'votes'
}

batch_updates = []
for movie in movies.find({}):
    # Construct the fields to update (set and unset, respectively)
    fields_to_set = {}
    fields_to_unset = {}

    # Delete all the fields with empty values
    for field, val in movie.copy().items():
        if val == '' or val == ['']:
            fields_to_unset[field] = ''
            # Delete the field in the current movie, for the convenience of
            # subsequent processing
            del movie[field]

    # Split some fields from string literals to arrays
    for single_field, plural_field in single_plural.items():
        if single_field in movie:
            # Set the new field, and remove the original field
            fields_to_set[plural_field] = movie[single_field].split(', ')
            fields_to_unset[single_field] = ''

    # Rename some fields
    for original, new in renaming.items():
        if original in movie:
            # Set the new named field, and remove the original named field
            fields_to_set[new] = movie[original]
            fields_to_unset[original] = ''

    # For some date-related fields, parse out the dates from their string
    # representations
    if 'released' in movie:
        fields_to_set['released'] = datetime.strptime(movie['released'],
                                                      '%Y-%m-%d')
    if 'lastupdated' in movie:
        # Note that we also do a rename here
        fields_to_set['lastUpdated'] = datetime.strptime(
            movie['lastupdated'].split('.')[0], '%Y-%m-%d %H:%M:%S'
        )
        fields_to_unset['lastupdated'] = ''

    # Reshape the IMDB-related fields into one single field (one single embedded
    # document)
    imdb_info = {}
    for original, new in imdb_renaming.items():
        if original in movie:
            imdb_info[new] = movie[original]
            fields_to_unset[original] = ''
    fields_to_set['imdb'] = imdb_info

    update = {}
    if fields_to_set:
        update['$set'] = fields_to_set
    if fields_to_unset:
        update['$unset'] = fields_to_unset

    # Instead of updating one document at a time:
    # movies.update_one(filter={'_id': movie['_id']}, update=update)
    # We will add the current update to a batch of updates, and when the current
    # batch size reaches the batch size limit, send the batch updates to the
    # server at once.
    batch_updates.append(
        UpdateOne(filter={'_id': movie['_id']}, update=update)
    )
    if len(batch_updates) == BATCH_SIZE:
        movies.bulk_write(requests=batch_updates)
        print(f'Finished updating a batch of {BATCH_SIZE} documents')
        batch_updates = []
# Take care of the last batch of updates
if batch_updates:
    movies.bulk_write(requests=batch_updates)
    print(f'Finished updating a last batch of {len(batch_updates)} documents')

print('Finshed all the updates.')
