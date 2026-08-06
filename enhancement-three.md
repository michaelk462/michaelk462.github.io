# **Michael King CS-499 ePortfolio**

# **Enhancement Three: Databases**

## **Artifact Description**
The artifact for this milestone is the weight tracking Android mobile application I developed for **CS-360: Mobile Architecture and Programming**. I created this program in Java with the Android Studio platform. The app was originally designed to enable a user to create an account and log in, log and review weight info over time, set a goal weight, and receive a text message upon achieving that goal. All data, including user information, weight data, and the goal, were stored locally on the device in an SQLite database, accessed through an object that performed synchronous database queries on the UI thread.

## **Why This Artifact Was Selected**
I chose to demonstrate this artifact in the Databases category because the original storage scheme used a single device, unauthenticated local data store that, frankly, could not scale beyond a single phone or more than a casual single user. It was exactly what a database enhancement was supposed to fix. Looking at the original implementation also led me to produce an even more specific justification for the database build. There was no user ID column in the SQLite weight entry table, so that each user would have been reading and writing to the same pool of records in the early system, not their own.

## **How This Artifact Was Improved**
This enhancement involved migrating the application’s storage layer from local SQLite to a cloud-hosted MongoDB Atlas deployed on Amazon cloud infrastructure (exposed to the Android client as a RESTful API) driven by a Flask/PyMongo backend (containing the app.py script plus its dependencies and configuration files). The Android client was also rewritten to interact with the Python/Flask API over HTTP via Retrofit rather than directly access a local database. The improved artifact has two co-working parts: a Flask/PyMongo backend (*app.py* script plus its dependencies and configuration files) and an Android client (split into individual activities, a Retrofit client service interface, request, and response data classes, and an Android-managed token for session persistence).

## **Client-Side Changes**



## **Course Outcome Alignment**

### Outcome 1
Demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals.

### How This Outcome Is Demonstrated
This outcome is demonstrated using the completed migration involving the functioning Flask/PyMongo REST API with indexed collections, and an Android client built with Retrofit that calls that API asynchronously, and an authentication flow using JWT that links the two.

### Outcome 2
Develop a security mindset that anticipates adversarial exploits in software architecture and designs to expose potential vulnerabilities, mitigate design flaws, and ensure privacy and enhanced security of data and resources.

### How This Outcome Is Demonstrated
This outcome is demonstrated through hashing passwords, parameterized queries, and token-based authentication in the abstract. The implementation proved to be an extra, unplanned security insight: the core artifact’s prior data entry source file did not scope weighing any permanently entered items by user at all, rather than as a data-isolation bug. Addressing this flaw entailed scoping every read, update, and delete operation to the authenticated user identity, rather than to a record’s raw ID; this is, in spirit, a more concrete proactive step toward thwarting an attacker than the initial plan explicitly accounted for.

## **Narrative**
[Read Full Narrative](https://github.com/michaelk462/michaelk462.github.io/blob/7deacf8c832e1990d96aaec5dabe838a041d7d69/Narratives/CS-499%20Enhancement%20Three%20Narrative.pdf)

## **Original Project vs. Enhancement**

### Screenshots

### Original and Enhanced Artifact Files

## **Downloads**

[**Original** (~130 KB)](CS360Original.zip)

[**Enhancement** (~115 KB)](CS360Enhancement.zip)

# **Links**

[Code Review](code-review)

[Enhancement One: Software Design & Engineering](enhancement-one)

[Enhancement Two: Algorithms & Data Structures](enhancement-two)

[Main Page](index)
