# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/24/2026
# File: load_data.py
# Assignment: CS-499 Milestone Three: Algorithms and Data Structures Enhancement
# University: SNHU

# ***Imports***
import sys
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# ***Connection Variables***
CSV_PATH = "aac_shelter_outcomes.csv"
USER = "aacuser"
PASS = "password1"
HOST = "localhost"
PORT = 27017
DB_NAME = "aac"
COLLECTION = "animals"

# ***Main Method***
def main():
    try:
        # Connects to MongoDB Server
        client = MongoClient(
            f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/?authSource=admin",
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command("ping")
    except Exception as e:
        # Prints Error Message if there is no connection to MongoDB or
        # if the user fails to login to animal shelter database
        print("ERROR: Connection or Authentication Failure")
        print(f"Details: {e}")
        print("Ensure that MongoDB is running and the aacuser account exists")
        print("with the EXACT username and password above.")
        print("See README for a full setup guide.")
        sys.exit(1)

    db = client[DB_NAME] #aac database
    collection = db[COLLECTION] # animals collection

    df = pd.read_csv(CSV_PATH) # reads csv file
    df = df.where(pd.notnull(df), None) #NaN to None so Mongo can store real Nulls
    records = df.to_dict("records")

    try:
        existing = collection.count_documents({}) # Counts number of existing documents
        if existing: #Prints error message if documents already exist in the database
            print(f"Collection already has {existing} documents; clearing before reload.")
            collection.delete_many({}) # Deletes existing documents
        result = collection.insert_many(records) # Prints number of inserted documents
        # Prints message if documents are inserted into the database
        print(f"Inserted {len(result.inserted_ids)} documents into {DB_NAME}.{COLLECTION}")
    except OperationFailure as e: # Prints error message if no documents are inserted
        print (f"ERROR: Write Failed ({e}). Ensure aacuser has readWrite on '{DB_NAME}.")
        sys.exit(1)

# Starts Main Method
if __name__ == "__main__":
    main()