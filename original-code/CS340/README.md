# How to Run CS-340 Animal Shelter Dashboard (without Codio or Jupyter)

## Download Required Tools
1. **The latest version of Python.** It ensures that the code runs smoothly.

    - **Download:** https://www.python.org/

2. **MongoDB.** This tool is essential for installing the animal database.

    - **Download:** https://www.mongodb.com/try/download/community     
    - Download latest version, MSI, Windows x64     
    - Run Installer, Choose **"Complete"** setup.  
    - Keep `Install MongoDB as a Service` checked. It will auto-start on boot and listen on `localhost:27017`.     
    - Also, make sure `mongosh` (Mongo Shell) is installed. The Installer usually offers this, or you can download it separately from the same page.

## Create the Database
1. Open a Command Prompt or Terminal and run:
```
mongosh
```
2. At the `test>` prompt, run:
```js
use admin
db.createUser({
    user: "aacuser"
    pwd: "password1"
    roles: [ { role: "readWrite", db: "aac" } ]
})
```

This matches the credentials already hardcoded in
app.py/animalshelter.py
(username `aacuser`, password `password1`, database `aac`).

3. Type `exit` to leave mongosh.

## Install Python Packages
1. Type in the Command Prompt or Terminal:
```
pip install -r requirements.txt
```
Or, if that doesn't work, type:
```
python -m pip install -r requirements.txt
```
2. Type in the Command Prompt or Terminal:
```
python load_data.py
```
Or, go to the `load_data.py` file and click "Run Python File".

You should see
`Inserted 10000 documents into aac.animals`.
This only needs to be run **once.**
Re-run it any time you want to reset/reload the data.

## Run the Dashboard
1. To start the Dash app and run the Animal Shelter Dashboard, type in the Command Prompt or Terminal:
```
python app.py
```
Or, go to the `app.py` file and click "Run Python File".

2. While the server is running,
Open a browser to **http://127.0.0.1:8050**.
Leave the Command Prompt/Terminal window open while using it.
Press `Ctrl+C` to stop the server when you are done using it.