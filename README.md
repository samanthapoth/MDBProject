# Blog Explorer

Blog explorer is a project that allows users to search over 15,000 blog posts and find recommended authors. To run this application follow the instructions below:

### 1. Setup virtual environment with requirements:
   
  MacOS or Linux:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


  Windows:
  
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create a Neo4j project
Create ad Neo4j project. Install the Graph Data Science library and run the project.

### 3. Create a MongoDB database 
Create a MongoDB database on your local host called 'blogs_database'. Make sure the host is on port 27017 or change line 7 in ```MongoDBData.py```.

### 4. Upload the data
To load both databases with the blogs data, run the following:

```
python MongoDBData.py
python UploadNeo4jData.py blogs
```

### 5. Run the website
The website is run on a flask server. To start the website, run the following command:

```
python app.py
```

The website will be locally hosted at http://127.0.0.1:5001 or the specific address output by the previous command. Follow this to use the website.


## On the Website
On the website, you can search the blogs by search terms, look at blog posts from a blogger with a specific ID, or get recommendations for other bloggers based on a blogger that oyu like. 
