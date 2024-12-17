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
Create a Neo4j project and with a local DBMS. Install the Graph Data Science library and run the project. Update the password you set for the project in the ```UploadNeo4jData.py``` file on line 9 and the ```Neo4jRequest.py``` file on line 8.

### 3. Create a MongoDB database 
Create a MongoDB database on your local host called 'blogs_database' and a collection in it called 'blog_posts'. If wanting a different db name or collection, change lines 8 and 9 in ```MongoDBData.py```. Make sure the host is on port 27017 or change line 7 in ```MongoDBData.py```.

### 4. Download then upload the data
Download the blogs data from this link:
[Blogs Data](https://iowa-my.sharepoint.com/:f:/g/personal/spothitakis_uiowa_edu/ElLNFf8U2e5HsJw8LzzSCl4BVVOPnxouv_bFN41z_Q2llQ?e=agwV6T)

(The original data is from this site: https://u.cs.biu.ac.il/~koppel/BlogCorpus.htm, but data had be downloaded through inspect element. To save time and improve usability, data was put into One Drive.)

Open the zip file and save the folder of blogs in the project directory as 'blogs'.

To load both databases with the blogs data, run the following:

```
python MongoDBData.py
python UploadNeo4jData.py blogs
```
This may take some time.

### 5. Run the website
The website is run on a flask server. To start the website, run the following command:

```
python app.py
```

The website will be locally hosted at http://127.0.0.1:5001 or the specific address output by the previous command. Follow this to use the website.


## On the Website
On the website, you can search the blogs by search terms, look at blog posts from a blogger with a specific ID, or get recommendations for other bloggers based on a blogger that you like. The recommendations feature takes a few seconds as it creates a new graph projection, so hold tight! 


