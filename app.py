from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from Neo4jRequest import Neo4jBloggerReq  # Import your Neo4j class
from MongoDBData import search_blog_posts
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Initialize Neo4j connection
neo4j_client = Neo4jBloggerReq()

client = MongoClient("mongodb://localhost:27017")  # Update with your MongoDB URI
db = client["blogs_database"] 
collection = db["blog_posts"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        print("Received request data:", data)  # Debug log
        search_type = data.get('search_type', '')

        # Handle different search types
        if search_type == 'posts':
            search_text = data.get('search_text')
            print("Searching for text:", search_text)  # Debug log
            if not search_text:
                return jsonify({"success": False, "error": "Search text is required"}), 400
            
            cursor_results = search_blog_posts(search_text)
            print("Raw cursor results:", cursor_results)  # Debug log
            
            results = []
            
            # Convert cursor to list first
            cursor_list = list(cursor_results)
            print("Cursor as list:", cursor_list)  # Debug log
            
            for doc in cursor_list:
                if 'posts' in doc:
                    blogger_info = {
                        'blogger_id': doc.get('blogger_id'),
                        'gender': doc.get('gender'),
                        'age': doc.get('age'),
                        'industry': doc.get('industry'),
                        'sign': doc.get('sign')
                    }
                    
                    for post in doc['posts']:
                        if isinstance(post, dict) and 'content' in post:
                            post_info = {
                                'content': post['content'],
                                'date': post.get('date'),
                                'author': blogger_info
                            }
                            results.append(post_info)
            
            print("Final results:", results)  # Debug log
            
            if not results:
                results = ["No matching posts found"]
            
        elif search_type == 'posts_by_gender':
            gender = data.get('gender')
            if not gender:
                return jsonify({"success": False, "error": "Gender is required"}), 400
            results = neo4j_client.GetPostsByGender(gender)
            
        elif search_type == 'posts_by_blogger':
            blogger_id = data.get('blogger_id')
            if not blogger_id:
                return jsonify({"success": False, "error": "Blogger ID is required"}), 400
            results = neo4j_client.GetPostsByBloggerID(int(blogger_id))
            
        elif search_type == 'recommendations':
            blogger_id = data.get('blogger_id')
            if not blogger_id:
                return jsonify({"success": False, "error": "Blogger ID is required"}), 400
            results = neo4j_client.Recommand(int(blogger_id), 10)
            
        else:
            return jsonify({"success": False, "error": "Invalid search type"}), 400

        response_data = {
            "success": True, 
            "data": results,
            "search_type": search_type
        }
        print("Sending response:", response_data)  # Debug log
        return jsonify(response_data)

    except ValueError as ve:
        print("ValueError:", str(ve))  # Debug log
        return jsonify({"success": False, "error": "Invalid input: " + str(ve)}), 400
    except Exception as e:
        print("Error in search route:", str(e))  # Debug log
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
