# **Michael King CS-499 ePortfolio**

# **Enhancement Two: Algorithms & Data Structures**

## **Artifact Description**
The artifact is the Grazioso Salvare Animal Shelter Dashboard created for **CS 340: Advanced Programming Concepts**. It is an interactive web application built with Python, MongoDB, and Plotly Dash. The application functionality consists of a CRUD module, *animalshelter.py*, that interacts with a collection of 10,000 animal shelter outcomes in a Mongo database, and a Dash-based dashboard (*app.py/ProjectTwoDashboard.ipynb*) that allows a user to filter animals based on rescue type (Water Rescue, Mountain/Wilderness, Disaster/Tracking), see the filtered data in an interactive data table, see a breed distribution pie chart, and see a geolocation map of a selected animal. The original version of this artifact was created earlier in the Computer Science program and was adopted into the ePortfolio during the CS 499 Module One planning process.

## **Why This Artifact Was Selected**
This artifact was selected for the Algorithms and Data Structures category mainly because it provided distinct opportunities to optimize the algorithms presented. The original artifact implemented each rescue type selection by issuing a full, unfiltered collection scan over the entire MongoDB collection, retrieving the data to the client, then applying Boolean masks over the pandas DataFrame of the query data to filter out unnecessary records. This meant that every filter request was an O(n) collection scan and then a re-filtering of the same data held in memory, even when it was a filter that had been requested a matter of seconds before. As the original dashboard already addressed the user-facing aspect of displaying and filtering data on animal shelters, the enhancement improved the efficiency, scalability, and responsiveness of this existing application.

## **The Three Algorithmic Improvements**

### Compound Indexes
Compound indexes on `breed`, `sex_upon_outcome`, and `age_upon_outcome_in_weeks`, the three fields every rescue-type filter searches on, along with a separate index on `location_lat` and `location_long` to enable the geolocation map to be rendered, so Mongo will be able to perform the index-assisted lookup, O(log n), instead of a complete collection scan, O(n), for this task.

### Aggregation Pipelines 
A new method, `read_with_filter(rescue_type)`, replaces client-side pandas filtering with a MongoDB aggregation pipeline (`$match`, `$project`, `$sort`), where filtering, field selection, and sorting all happen on the server side outside of Python, not after the collection has been fully streamed down to a Python DataFrame.

### Memoization Cache
A dictionary cache, `query_cache`, saves the result of each rescue-type query after the first run, so that a subsequent request for the same data can be an O(1) dictionary lookup, rather than an O(n) query, with its cache automatically cleared on the next `create()`, `update()`, or `delete()` call to ensure all data remains consistent at all times.

## **Complexity, Before and After**

| Path                         | Complexity                         |
|------------------------------|------------------------------------|
| Original unindexed find()    | O(n) - full collection scan        |
| Enhanced indexed aggregation | O(log n) - index-assisted lookup   |
| Cached repeated query        | O(1) - dictionary lookup           |

## **Enhanced CRUD Module (excerpt)**
```
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
```

## **Course Outcome Alignment**
### Outcome 1
**Design and evaluate computing solutions that solve a given problem using algorithmic principles and computer science practices and standards appropriate to its solution while managing the trade-offs involved in design decisions.**

### How This Outcome Is Demonstrated
Each of the three enhancement decisions was prefaced in the course by an explicit before/after complexity statement, from O(n) to O(log n) to O(1), for repeated queries. 

### Outcome 2
**Demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals.**

### How This Outcome Is Demonstrated
Indexing, aggregation pipelines, and memoization are well-founded, standard, and pragmatic techniques used in concurrency. No modifications were made to the original outcome coverage plan; the improvement was implemented as designed in Module One.

## **What I Learned**
One particular problem revealed only through *hands-on testing* and not inspection of the code was that after the dashboard’s callback was wired to call `read_with_filter()`, the rec_num column had disappeared from the data table in every case, including the “Reset All Animals” view, even though it was still being displayed correctly in the original version running on the same server. Regression traced back to the aggregation pipeline `$project` stage provided the answer: `$project` in inclusion mode is non-null fields only, and result fields have to be explicitly added with 1 to `PROJECTION_FIELDS`, but `rec_num` was missing. Because the original filtering in pandas sliced columns from an existing DataFrame that already had every column, there was no failure mode for this sort of null-value data loss with the original code; instead, this was a subtle, field-by-field database loss risk linked exclusively to context-specific projection implementations. This was fixed by just inserting `'rec_num': 1` into the projection, re-executing all three rescue-type filters plus the reset view, and confirming that it worked again against the live MongoDB instance.

## **Narrative**

[Read Full Narrative](https://github.com/michaelk462/michaelk462.github.io/blob/main/Narratives/CS-499%20Enhancement%20Two%20Narrative.pdf)

## **Original Project vs. Enhancement**

### Original and Enhanced Artifact Files

[Original Artifact Files](https://github.com/michaelk462/michaelk462.github.io/tree/main/original-code/CS340)

[Enhanced Artifact Files](https://github.com/michaelk462/michaelk462.github.io/tree/main/enhanced-code/CS340)

### Downloads

[**Original** (~700 KB)](CS340Original.zip)

[**Enhancement** (~704 KB)](CS340Enhancement.zip)

# **Links**

[Code Review](code-review)

[Enhancement One: Software Design & Engineering](enhancement-one)

[Main Page](index)

[Enhancement Three: Databases](enhancement-three)
