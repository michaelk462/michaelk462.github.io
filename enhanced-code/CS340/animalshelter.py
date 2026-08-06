# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/24/2026
# File: animalshelter.py
# Assignment: CS-499 Milestone Three: Algorithms and Data Structures Enhancement
# University: SNHU
#
# *** ENHANCEMENT SUMMARY ***
# This module was originally built for CS 340 with a single read() method
# that returned the entire collection and relied on client-side pandas/Python
# filtering in the dashboard. That approach performs an O(n) collection scan on
# every request and re-filters the full result set in application memory even when
# the same filter was just requested seconds earlier.
# 
# *** ALGORITHMIC IMPROVEMENTS ***
# 1. Compound index on the fields used by the dashboard's rescue type filters
#    (breed, sex_upon_outcome, age_upon_outcome_in_weeks) and on the geolocation
#    fields (location_lat, location_long). This lets MongoDB satisfy filter queries
#    with an index lookup (O(log n)) instead of a full collection scan (O(n)).
# 
# 2. A read_with_filter() method that builds a server-side MongoDB aggregation pipeline
#    ($match / $project / $sort) for each rescue type, so filtering happens in the database
#    engine instead of in a pandas DataFrame after the entire collection has already been
#    pulled over the network.
# 
# 3. A dictionary-based memoization cache (query_cache) keyed by rescue type.
#    A repeated request for the same filter is now an O(1) dictionary lookup instead of
#    re-running the query. The cache is invalidated automatically on create/update/delete 
#    so it can never return stale data after a write.
# 
# The original read() method is preserved unchanged so any existing code
# (or the initial full-table load in the dashboard) continues to work.


# *** Mongo and Object Imports ***
from pymongo import MongoClient 
from bson.objectid import ObjectId 

# *** AnimalShelter Class ***
class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    # Rescue-type filter definitions used my read_with_filter().
    # Centralizing these here
    # (Instead of duplicating them in the dashboard callback)
    # means the filter logic only has to be written once and is
    # easy to verify/extend.
    RESCUE_FILTERS = {
        'Water Rescue': {
            'breed': {'$in': ['Labrador Retriever Mix',
                              'Chesapeake Bay Retriever',
                              'Newfoundland']},
            'sex_upon_outcome': 'Intact Female',
            'age_upon_outcome_in_weeks': {'$gte': 26, '$lte': 156}
        },
        'Mountain Rescue': {
            'breed': {'$in': ['German Shepherd',
                              'Alaskan Malamute',
                              'Old English Sheepdog',
                              'Siberian Husky',
                              'Rottweiler']},
            'sex_upon_outcome': 'Intact Male',
            'age_upon_outcome_in_weeks': {'$gte': 26, '$lte': 156}
        },
        'Disaster Rescue': {
            'breed': {'$in': ['Doberman Pinscher',
                              'German Shepherd',
                              'Golden Retriever',
                              'Bloodhound',
                              'Rottweiler']},
            'sex_upon_outcome': 'Intact Male',
            'age_upon_outcome_in_weeks': {'$gte': 20, '$lte': 300}
        }
    }

    # Fields returned by the aggregation pipeline. Kept identical to the
    # columns the dashboard's DataTable/graph/map callbacks rely on.
    PROJECTION_FIELDS = {
        '_id': 0,
        'rec_num': 1,
        'age_upon_outcome': 1,
        'age_upon_outcome_in_weeks': 1,
        'animal_id': 1,
        'animal_type': 1,
        'breed': 1,
        'color': 1,
        'date_of_birth': 1,
        'datetime': 1,
        'monthyear': 1,
        'name': 1,
        'outcome_subtype': 1,
        'outcome_type': 1,
        'sex_upon_outcome': 1,
        'location_lat': 1,
        'location_long': 1
    }

    def __init__(self, username, password):
        # Initializing the MongoClient. This helps to access the MongoDB 
        # databases and collections.
        
        # Connection Variables
        USER = username if username else 'aacuser'
        PASS = password if password else 'password1'# changed password
        HOST = 'localhost' 
        PORT = 27017 
        DB = 'aac' 
        COL = 'animals' 
        
        # Initialize Connection 
        # MongoClient, implements username, password, localhost, and port
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT)) 
        self.database = self.client['%s' % (DB)] #aac database
        self.collection = self.database['%s' % (COL)] #animal collection

        # *** ENHANCEMENT 1: INDEX CREATION ***
        # Compound index on the three fields every rescue-type filter
        # queries against. MongoDB can use this single index to satisfy
        # all three RESCUE_FILTERS queries via index-assisted lookups
        # (O(log n)) instead of scanning every document (O(n)).
        self.collection.create_index([
            ('breed', 1),
            ('sex_upon_outcome', 1),
            ('age_upon_outcome_in_weeks', 1)
        ], name='idx_breed_sex_age')

        # Separate index supporting the geolocation map lookups.
        self.collection.create_index([
            ('location_lat', 1),
            ('location_long', 1)
        ], name='idx_geolocation')

        # *** ENHANCEMENT 3: MEMOIZATION CACHE ***
        # In-memory dictionary cache keyed by rescue-type string.
        # Repeated identical filter requests become O(1) lookups
        # instead of re-querying MongoDB.
        self.query_cache = {}

    # *** CREATE Method ***
    def create(self, data):
        if data is not None: # if data is not empty
            try:
                # insert_one returns an object with the inserted_id
                insert_result = self.collection.insert_one(data)

                # Enhancement: clear the cache so a newly inserted document
                # is reflected the next time a filtered read is requested.
                self.query_cache.clear()

                # returns true if create method is successful
                # otherwise returns false
                return True if insert_result.inserted_id else False
            except Exception as createError:
                # if there are errors, implement exception and return False
                print(f"ERROR: {createError}")
                return False
        else:
            # implement exception if data is empty
            raise Exception("ERROR: Data is empty")
        
    # *** READ Method ***
    # Unchanged; full unfiltered read, 
    # used for the dashboard's initial full-table load
    def read(self, query):
        # queries for documents in the specified collection
        if query is not None: #if query is not empty
            #Find() returns a cursor converted to a list
            cursor = self.database.animals.find(query)
            result_list = list(cursor)
            return result_list # list result is returned
        else: # Return empty list if query is empty or fails
            return [] # [] is an empty list
        
    # *** ENHANCEMENT 2: read_with_filter Method ***
    # Server-side aggregation pipeline replacing client-side pandas
    # filtering. Results for a given rescue_type are cached so repeat
    # requests skip the database round trip entirely.
    def read_with_filter(self, rescue_type):
        # O(1) cache hit; no query executed at all.
        if rescue_type in self.query_cache:
            return self.query_cache[rescue_type]
        
        # 'Reset'/unrecognized values fall back to returning everything,
        # matching the dashboard's original "Reset All Animals" behavior.
        if rescue_type not in self.RESCUE_FILTERS:
            pipeline = [
                {'$project': self.PROJECTION_FIELDS}
            ]
        else:
            match_stage = self.RESCUE_FILTERS[rescue_type]
            pipeline = [
                {'$match': match_stage},                     #STAGE 1: filter (index-assisted)
                {'$project': self.PROJECTION_FIELDS},        #STAGE 2: return only required fields
                {'$sort': {'age_upon_outcome_in_weeks': 1}}  #STAGE 3: order by age ascending
            ]
        
        result = list(self.collection.aggregate(pipeline))

        # Store in cache for future O(1) lookups of this rescue_type.
        self.query_cache[rescue_type] = result
        return result
    
    # *** UPDATE Method ***
    def update(self, query, update_data):
        # queries for documents in the specified collection
        if query is not None: # if query is not empty
            #updates a specific number of documents in animal collection
            result = self.database.animals.update_many(query, {"$set": update_data})
            
            # Enhancement: invalidate cache so stale filtered results are
            # never served after a write.
            self.query_cache.clear()
            
            return result.modified_count #returns number of modified documents
        else: 
            # implements exception if data is empty 
            raise Exception("ERROR: Data is empty")
        
    # *** DELETE Method ***
    def delete(self, query):
        # queries for documents in the specified collection
        if query is not None: # if query is not empty
            #deletes a number of documents
            result = self.database.animals.delete_many(query)

            # Enhancement: invalidate cache so stale filtered results are
            # never served after a write.
            self.query_cache.clear()

            return result.deleted_count #returns number of deleted documents
        else:
            # implements exception if data is empty
            raise Exception("ERROR: Data is empty")