import os
import xmltodict
from pymongo import MongoClient
from xml.parsers.expat import ExpatError

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/Blogs")  # Update with your MongoDB URI
db = client["blogs_database"] #make sure the db and the client are named the same as this
collection = db["blog_posts"]

# Function to search blog posts
def search_blog_posts(keyword):
    """Perform a full-text search on blog posts."""
    query = {"$text": {"$search": keyword}}
    projection = {
        "blogger_id": 1,
        "gender": 1,
        "age": 1,
        "industry": 1,
        "sign": 1,
        "posts": 1,
        "score": {"$meta": "textScore"}
    }
    results = collection.find(query, projection).sort("score", {"$meta": "textScore"}).limit(1)

    print(f"Search results for '{keyword}':")
    count = 0
    for result in results:
        print(f"ID: {result['blogger_id']}, Gender: {result['gender']}, Age: {result['age']}")
        for post in result.get("posts", []):
            print(f"  - Date: {post['date']}, Content: {post['content']}")


search_keyword = "Samantha Pothitakis"  # Replace with the term you want to search
search_blog_posts(search_keyword)