# *****CODE INFORMATION*****
# Name: Michael King
# File: animalshelter.py
# Assignment: CS 340 Animal Shelter Dashboard (Original)
# University: SNHU

# ***Mongo and Object Imports***
from pymongo import MongoClient 
from bson.objectid import ObjectId 

# ***AnimalShelter Class***
class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

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

    # ***CREATE Method***
    def create(self, data):
        if data is not None: #if data is not empty
            try:
                #insert_one returns an object with the inserted_id
                insert_result = self.collection.insert_one(data)
                
                # returns true if create method is successful
                # otherwise returns false
                return True if insert_result.inserted_id else False
            except Exception as createError:
                # if there are errors, implement exception and return False
                print (f"ERROR: {createError}")
                return False        
        else: 
            # implement exception if data is empty
            raise Exception("ERROR: Data is empty") 

    # ***READ method***
    def read(self, query):
        # queries for documents in the specified collection
        if query is not None: #if query is not empty
            #Find() returns a cursor converted to a list
            cursor = self.database.animals.find(query)
            result_list = list(cursor)
            return result_list # list result is returned
        else: # Return empty list if query is empty or fails
            return [] # [] is an empty list
        
    # ***UPDATE method****
    def update(self, query, update_data):
        # queries for documents in the specified collection
        if query is not None: # if query is not empty
            #updates a specific number of documents in animal collection
            result = self.database.animals.update_many(query, {"$set": update_data})
            return result.modified_count #returns number of modified documents
        else: 
            # implements exception if data is empty 
            raise Exception("ERROR: Data is empty")
            
    # ***DELETE method
    def delete(self, query):
        # queries for documents in the specified collection
        if query is not None: # if query is not empty
            #deletes a number of documents
            result = self.database.animals.delete_many(query)
            return result.deleted_count #returns number of deleted documents
        else:
            # implements exception if data is empty
            raise Exception("ERROR: Data is empty")