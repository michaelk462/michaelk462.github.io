# **Michael King CS-499 ePortfolio**

# **Professional Self-Assessment**

## **Introduction**
**Hi, I am Michael King. Welcome to my GitHub Pages ePortfolio!**

I have been enrolled in the Computer Science program at Southern New Hampshire University for approximately a year and a half, navigating through required coursework in software development, data structures, computational graphics, mobile development, and database design. From that coursework, three concepts have influenced my approach to a piece of code more strongly than any other: object-oriented design as a way to keep a system maintainable over time, algorithmic thinking as a field for trying to determine if a machine running a program is actually at peak efficiency, and a security way of thinking that considers every restriction to an existing data-processing route as a potential target for an attack.

## **Collaborating in a Team Environment**
In this program, **collaboration** was implemented in well-defined code reviews rather than group projects. In CS-320, I learned how to brand a test suite as an artifact of communication that a teammate could read to learn about a module’s behavior, corner cases, and assumptions, and I applied this lesson to the Milestone One code review video by explaining my code to an audience the way I would for my manager for a new hire. I integrated instructor feedback into Milestone submissions like a developer integrates pull request feedback into code-based projects. Overall, I have learned that collaboration is about developing work that other people can read, trust, and advance.

## **Communicating with Stakeholders**
Every class I have taken involved some text, oral presentation, or other **communication** intended for a target and sometimes nontechnical reader. The enhancement plan I provided in Module One, these milestone stories, and the code review video I created in this capstone project were designed for different audiences and in different tones and levels of detail. I also authored the enhancement plan structure for a professor to review for campus readiness, the milestone stories for a review committee member to evaluate my technical judgment, and the code review for a peer or manager to help them understand the rationale behind the decisions I had made. In IT-145 and CS-250, I have learned how to translate functional requirements into user stories and acceptance criteria. This process takes stakeholder requirements and filters them through features that I can implement as a developer.

## **Data Structures and Algorithms**
In CS-260, I was given **mathematical concepts (arrays, linked lists, trees, hash maps, Big O)** and have used them beyond that single class. The Algorithms and Data Structures enhancement in this ePortfolio, which takes the Grazioso Salvare Animal Shelter dashboard to another level through compound MongoDB indexes, a server-side aggregation pipeline, and a memoization cache, is a great example of that: it obliged me to identify where linear search was silently obstructing the complete user experience, select one index or caching scheme compatible with the current data values and more clearly state the performance gains rather than state the net acceleration. That same scientific approach to performance design emerges outside of the ePortfolio artifacts, in my sensitive treatment of any dataset before I start writing code against it. With each CSV export or new database collection, I have developed a notion to investigate what fields will be used most often for filtering, sorting, or presentation, because that line of thinking guides whether I set up a cache, a materialized view, or an index, rather than defaulting to whatever library I last learned.

## **Software Engineering and Database**
All along, the **software engineering and database** work overlapped the entirety of the program, from the object-oriented roots I started in IT-145 through the mobile architecture and persistence work I continued in CS-360. The Software Design and Engineering enhancement I have collected in this ePortfolio, the transformation of a single, monolithic CS-330 OpenGL scene into a logically classed set of components (Shader, Mesh, Texture, Camera, and Scene), is by definition the same approach I practiced first in IT-145 and IT-315; that software should be maintainable because it is built around single responsibilities, not because it is ordered around the features that happened to get tacked on first. The Databases enhancement extended that rule to preservation; it is the migration of the CS-360 inventory application from local device-bound SQLite to host-based MongoDB with a Flask REST API. Apart from the artifacts I have collected here, this program has also provided me with practical experience using both relational and non-relational data modeling and schema design, and using those schemas to load, update, and present data, mastering the principles of which I believe will be essential for any IT position I work in.

## **Security**
If there is a common thread linking all aspects of the capstone, it is **security awareness,** and it is also where my thinking evolved most during the program. In the first courses, I learned to think of security as a series of checklists to work through during design: hash the password, sanitize the input. This portfolio's Databases enhancement took that one step further. When I migrated the CS-360 weight-tracking app, I realized that the existing data-access layer had never scoped records to the current user, leaving a security hole in such a way that a user could read or write another user’s record by ID alone. Fixing that hole required rethinking my complete approach to security: the code required query-level checks, not just screen-level authentication. As a result, I have since become increasingly aware of issues in any system I write or inherit, actively working to understand the implicit trust boundaries and asking what the system’s response looks like from an authenticated but unprivileged agent.

## **Career Goals and Values**
My **career goal** is to work in IT management and networking positions, such as IT manager or systems analyst, where I can combine the technical hands-on assessment skills with the communication and organizational skills I believe are necessary to lead technical teams. That research revealed that employers value secure code development, cloud and database architecture experience, and the ability to explore trade-offs as much as project management skills. I designed this capstone with that in mind: each artifact was selected and built to showcase a different aspect of my professional technical breadth *(systems, level software design, code optimization, secure database architecture)* so they would best prove the assortment of technical credibility I want to project into management. I also utilize open, truthful communication on technical trade-offs; whether I am documenting a performance improvement or explaining why a security patch is larger than its initial scope, I have always tried to establish a baseline and base my arguments on concrete examination instead of assumptions. I plan to do the same in my career.

## **The Three ePortfolio Artifacts**
The **three artifacts** in this ePortfolio provide evidence of progress in the three main areas of this capstone: Software Design & Engineering, Algorithms & Data Structures, and Databases. While each artifact individually demonstrates technical expertise, they collectively provide narratives of technical breadth grounded in a security-aware, systems-oriented mindset.

### **Artifact One: Software Design & Engineering**
![Artifact One](assets/images/CS-330%20Enhancement.jpg)

The first artifact is a **3D graphics scene originally built in CS-330 using C++ and OpenGL.** The initial implementation performs correctly, but places all logic in a single large main() function, with duplicated mesh initialization code, and no exception handling for missing texture files. The enhanced artifact refactors this project into ShaderProgram, Mesh, Texture, Camera, and Scene classes, improving correctness and documentation, and providing reliable exception handling for missing textures, while achieving the same rendering solution. This is shown to be a creative and established software engineering technique and communicates the technical tone of my portfolio.

[**Explore This Artifact**](enhancement-one)

### **Artifact Two: Algorithms & Data Structures**
![Artifact Two](assets/images/CS-340%20Dashboard%20Screenshot.jpg)

The second artifact is the **the Grazioso Salvare animal shelter dashboard, originally built in CS-340 as a Python/Dash app with a MongoDB backend.** The artifact used client-side filtering of the entire dataset for each query, resulting in an O(n) linear scan, where n was the dataset size. The enhanced artifact I built used compound indexes on the database, a server-side aggregation pipeline, and a memoization caching layer on the application, each detailed with an analysis comparing the before-and-after complexities. Every query is now a lookup requiring O(log n) or O(1) time.

[**Explore This Artifact**](enhancement-two)

### **Artifact Three: Databases**
![Artifact Three](assets/images/CS-360%20Enhancement%20Screenshot.jpg)

The third artifact is **the weight-tracking app, originally built for CS-360 in Java with a primitive local SQLite database.** It stored passwords in plain, unencrypted text, established SQL statements via string concatenation, and stored everything on the mobile device. The enhancement relocated this application to a Flask REST API with a cloud-hosted MongoDB Atlas database, JWT authentication, parameterized queries, and stored tokens encrypted on the device. This gives the clearest example of the security mindset that threads through this entire portfolio and also anchors the final category of database enhancement.

[**Explore This Artifact**](enhancement-three)

## **Course Outcomes**

### **Course Outcome 1**
**I Employed strategies for building collaborative environments that enable diverse audiences to support organizational decision making in the field of computer science.**

This outcome is demonstrated in the [**Code Review**](code-review), which walks a non-technical, peer/manager-level audience through each artifact's existing functionality, weaknesses, and enhancement plan.

### **Course Outcome 2**
**I Designed, developed, and delivered professional-quality oral, written, and visual communications that are coherent, technically sound, and appropriately adapted to specific audiences and contexts.**

This outcome is demonstrated across the [**Code Review**](code-review) and the written narratives for all three enhancements, each documenting design rationale in technical standards-grounded language.

### **Course Outcome 3**
**I Designed and evaluated computing solutions that solve a given problem using algorithmic principles and computer science practices and standards appropriate to its solution, while managing the trade-offs involved in design choices.**

This outcome is demonstrated primarily in [**Algorithms & Data Structures**](enhancement-two), with explicit before/after complexity analysis (O(n) -> O(log n) -> O(1)) for every optimization.

### **Course Outcome 4**
**I Demonstrated an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals.**

This outcome is demonstrated in [**Software Design & Engineering**](enhancement-one)'s cross-language graphics migration and in [**Databases**](enhancement-three)'s REST API and cloud database architecture.

### **Course Outcome 5**
**I Developed a security mindset that anticipates adversarial exploits in software architecture and designs to expose potential vulnerabilities, mitigate design flaws, and ensure privacy and enhanced security of data and resources.**

This outcome is demonstrated in [**Databases**](enhancement-three), which replaces plain-text credentials and string-concatenated queries with hashed passwords, parameterized queries, JWT authentication, and per-user data scoping.

# **Links**

[**Professional Self-Assessment**](index)

[**Code Review**](code-review)

[**Enhancement One: Software Design & Engineering**](enhancement-one)

[**Enhancement Two: Algorithms & Data Structures**](enhancement-two)

[**Enhancement Three: Databases**](enhancement-three)

