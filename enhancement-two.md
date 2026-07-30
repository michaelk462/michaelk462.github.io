# **Michael King CS-499 ePortfolio**

# **Enhancement Two: Algorithms & Data Structures**

## **Introduction**

The artifact is the Grazioso Salvare Animal Shelter Dashboard created for **CS 340: Advanced Programming Concepts**. It is an interactive web application built with Python, MongoDB, and Plotly Dash. The application functionality consists of a CRUD module, *animalshelter.py*, that interacts with a collection of 10,000 animal shelter outcomes in a Mongo database, and a Dash-based dashboard (*app.py/ProjectTwoDashboard.ipynb*) that allows a user to filter animals based on rescue type (Water Rescue, Mountain/Wilderness, Disaster/Tracking), see the filtered data in an interactive data table, see a breed distribution pie chart, and see a geolocation map of a selected animal. The original version of this artifact was created earlier in the Computer Science program and was adopted into the ePortfolio during the CS 499 Module One planning process.

## **Why This Artifact Was Selected**
This artifact was selected for the Algorithms and Data Structures category mainly because it provided distinct opportunities to optimize the algorithms presented. The original artifact implemented each rescue type selection by issuing a full, unfiltered collection scan over the entire MongoDB collection, retrieving the data to the client, then applying Boolean masks over the pandas DataFrame of the query data to filter out unnecessary records. This meant that every filter request was an O(n) collection scan and then a re-filtering of the same data held in memory, even when it was a filter that had been requested a matter of seconds before. As the original dashboard already addressed the user-facing aspect of displaying and filtering data on animal shelters, the enhancement improved the efficiency, scalability, and responsiveness of this existing application.

## **How This Artifact Was Improved**
The enhancement targeted three specific, complementary improvements to this process:
1. The first was **a compound index** on breed, sex_upon_outcome, and age_upon_outcome_in_weeks, the three fields every rescue-type filter searches on, along with a separate index on location_lat and location_long to enable the geolocation map to be rendered, so Mongo will be able to perform the index-assisted lookup, O(log n), instead of a complete collection scan, O(n), for this task.
2. The second improvement was **a new method**, read_with_filter(rescue_type), which replaces client-side pandas filtering with a MongoDB aggregation pipeline ($match, $project, $sort), where filtering, field selection, and sorting all happen on the server side outside of Python, not after the collection has been fully streamed down to a Python DataFrame.
3. The third improvement was **a dictionary cache**, query_cache, which saves the result of each rescue-type query after the first run, so that a subsequent request for the same data can be an O(1) dictionary lookup, rather than an O(n) query, with its cache automatically cleared on the next create(), update(), or delete() call to ensure all data remains consistent at all times. This set of improvements exemplifies the process of analyzing a production system, pinpointing the true bottleneck, and applying multiple algorithmic solutions, from indexing through server-side query processing to caching, each of which addresses a small, distinct facet of the problem of speed.

## **Course Outcome Alignment**
The completion of the artifact satisfied the course outcome *"Design and evaluate computing solutions that solve a given problem using algorithmic principles and computer science practices and standards appropriate to its solution while managing the trade-offs involved in design decisions,"* because each of the three enhancement decisions was prefaced in the course by an explicit before/after complexity statement, from O(n) to O(log n) to O(1), for repeated queries. 

The artifact also satisfied the course outcome *"Demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals,"* because indexing, aggregation pipelines, and memoization are well-founded, standard, and pragmatic techniques used in concurrency. No modifications were made to the original outcome coverage plan; the improvement was implemented as designed in Module One.

## **Reflection**
This experience was an excellent reminder that enhancement work is not done when the code finally runs without errors; it is done when the output has been checked column by column against the source value. It also reinforced the need to run the original and enhanced versions side by side while developing, as the difference pointed out here was only visible when directly comparing the two dashboards visually.

## **Narrative**

[Read Full Narrative](https://github.com/michaelk462/michaelk462.github.io/blob/main/CS-499%20Enhancement%20Two%20Narrative.pdf)

## **Downloads**

[**Original** (700 KB)](CS340Original.zip)

[**Enhancement** (707 KB)](CS340Enhancement.zip)

# **Links**

[Code Review](code-review)

[Enhancement One: Software Design & Engineering](enhancement-one)

[Main Page](index)

[Enhancement Three: Databases](enhancement-three)
