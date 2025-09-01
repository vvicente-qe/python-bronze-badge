### My experience writing the service

I have zero experience working with Python, so this is totally new to me. Fortunately, the article provided was pretty straightforward, everything was included in the tutorial. However, it can be challenging to debug when something doesn’t work as expected. One of the more difficult parts for me was reading the article itself, as I’m the type of learner who absorbs more through video tutorials while applying things hands-on. That’s also why I didn’t fully understand some parts of the code and needed Copilot to explain them to me.

The article already had the API service set up, so I just followed the structure they built and tweaked some parts to fit my use case. I’m sure this isn’t what an enterprise-grade API looks like, but it was a great experience to write an API from scratch—even if I was just following along with the article—and to be able to provide my own insights on how to improve it.

Writing the tests was the part I enjoyed the most, probably because I’m a QE and already have a background in writing API tests. What was new to me was adding hard assertions and testing the API results directly in the database, which I found really cool. Learning new things is always exciting. The additional changes I made for data logging functionality and input validations didn’t have a huge impact on the project and only required a few lines of code. However, they added more complexity to the testing side rather than the coding itself.

2 changes implemeneted in the REST service:
- Returning consistent response formats (e.g., always JSON with status codes).
- closing db session every after db commit prevent connection leakage

Additional changes i think that can be added:
- input validations and error handling (applied)
- rate limiting
- logging for the crud. or even just adding the create date or last update date in the users model (applied)

Review comments
- [x] only display the relevant data (generated id, user details) --response in list is too crowded
- [x] set required fields
- [x] modules scope the fixture
- [x] fix sequencing of tests to only use one user 
- [x] cleanup code, remove unused codes
- [x] add .gitignore
- [x] research on environment variable management

Suggestions
- [x] include created_date and modify_date in the user model
- [x] Behavior: upon creation created data = modify date; upon record update, modify date should be updated
