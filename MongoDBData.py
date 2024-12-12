import os
import xmltodict
from pymongo import MongoClient
from xml.parsers.expat import ExpatError

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017")  # Update with your MongoDB URI
db = client["blogs_database"] #make sure the db and the client are named the same as this
collection = db["blog_posts"]

# Path to the directory containing .xml files
xml_directory = 'blogs'

def parse_filename(file_name):
    """Extract metadata from the filename."""
    parts = file_name.split('.')
    return {
        "blogger_id": parts[0],
        "gender": parts[1],
        "age": int(parts[2]),
        "industry": parts[3],
        "sign": parts[4] if len(parts) > 4 else None
    }

def clean_xml(xml_data):
    """Clean XML data to handle undefined entities."""
    return xml_data.replace('&', '&amp;')  # Get rid of the escape characters

def process_and_insert(file_path):
    """Process an XML file and insert its data into MongoDB."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            xml_data = clean_xml(file.read())
            parsed_data = xmltodict.parse(xml_data)  # Convert XML to dictionary
            
            blog_content = parsed_data.get("Blog", {})
            posts = []
            if "date" in blog_content and "post" in blog_content:
                posts.append({"date": blog_content["date"], "content": blog_content["post"]})
            elif isinstance(blog_content.get("date"), list):
                for date, post in zip(blog_content["date"], blog_content["post"]):
                    posts.append({"date": date, "content": post})

            metadata = parse_filename(os.path.basename(file_path))
            metadata["posts"] = posts

            collection.insert_one(metadata)
            print(f"Inserted data from {file_path} successfully.")
    except ExpatError as e:
        print(f"Skipping malformed XML in {file_path}: {e}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def add_files():
# Process all .xml files in the directory
    for file_name in os.listdir(xml_directory):
        if file_name.endswith(".xml"):
            file_path = os.path.join(xml_directory, file_name)
            process_and_insert(file_path)

    # Create a text index on posts.content
    collection.create_index([("posts.content", "text")], default_language="english")
    print("Text index on 'posts.content' created.")

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
    return results

if __name__ == "__main__":
    add_files()
    search_keyword = ""  # Replace with the term you want to search
    search_blog_posts(search_keyword)

    # Close MongoDB connection
    client.close()