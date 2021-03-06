# -*- coding: utf-8 -*-

"""
This module converts any string value for "birthday" field to BSON dates.
"""

__author__ = 'Ziang Lu'

import dateparser
from pymongo import MongoClient, UpdateOne

DB = 'mflix'
PASSWORD = 'Zest2016!'
BATCH_SIZE = 1000  # Batch size for batch insertion with bulk_write()

conn_uri = 'mongodb://zianglu:' + PASSWORD + '@cluster0-shard-00-00-hanbs.mongodb.net:27017,cluster0-shard-00-01-hanbs.mongodb.net:27017,cluster0-shard-00-02-hanbs.mongodb.net:27017/' + \
    DB + '?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true'

cli = MongoClient(conn_uri)
people_raw = cli.cleansing['people-raw']

batch_updates = []
for person in people_raw.find({'birthday': {'$type': 'string'}}):
    update = {'$set': {'birthday': dateparser.parse(person['birthday'])}}
    # Instead of updating one document at a time, we will add the current update
    # to a batch of updates, and when the current batch size reaches the batch
    # size limit, send the batch updates to the server at once.
    batch_updates.append(
        UpdateOne(filter={'_id': person['_id']}, update=update)
    )
    if len(batch_updates) == BATCH_SIZE:
        people_raw.bulk_write(requests=batch_updates)
        print(f'Finished updating a batch of {BATCH_SIZE} documents')
        batch_updates = []
# Take care of the last batch of updates
if batch_updates:
    people_raw.bulk_write(requests=batch_updates)
    print(f'Finished updating a last batch of {len(batch_updates)} documents')

print('Finshed all the updates.')
