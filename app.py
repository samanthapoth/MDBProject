from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from Neo4jRequest import Neo4jBloggerReq
from MongoDBData import search_blog_posts, get_posts_by_blogger_id
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

try:
    neo4j_client = Neo4jBloggerReq()
    neo4j_available = True
except Exception as e:
    print(f"Warning: Neo4j connection failed: {str(e)}")
    neo4j_available = False

client = MongoClient("mongodb://localhost:27017")
db = client["blogs_database"] 
collection = db["blog_posts"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        search_type = data.get('search_type', '')

        if search_type == 'posts':
            search_text = data.get('search_text')
            if not search_text:
                return jsonify({"success": False, "error": "Search text is required"}), 400
            
            print(f"Searching for text: {search_text}")
            cursor_results = search_blog_posts(search_text)
            
            if cursor_results is None:
                print("No cursor results returned")
                return jsonify({
                    "success": True,
                    "data": ["No matching posts found"],
                    "search_type": search_type
                })
            
            results = []
            cursor_list = list(cursor_results)
            print(f"Found {len(cursor_list)} documents")
            
            for doc in cursor_list:
                if doc is None:
                    print("Skipping None document")
                    continue
                    
                blogger_info = {
                    'blogger_id': doc.get('blogger_id'),
                    'gender': doc.get('gender'),
                    'age': doc.get('age'),
                    'industry': doc.get('industry'),
                    'sign': doc.get('sign')
                }
                
                if not doc.get('posts'):
                    print(f"No posts found for blogger {blogger_info['blogger_id']}")
                    continue
                    
                for post in doc['posts']:
                    if not isinstance(post, dict):
                        print(f"Skipping invalid post format: {type(post)}")
                        continue
                        
                    dates = post.get('date', [])
                    contents = post.get('content', [])
                    
                    if not isinstance(contents, list):
                        print(f"Content is not a list: {type(contents)}")
                        continue
                        
                    for i, content in enumerate(contents):
                        if not content:
                            print(f"Skipping empty content at index {i}")
                            continue
                            
                        try:
                            if i < len(dates):
                                post_info = {
                                    'content': str(content),
                                    'date': dates[i],
                                    'author': blogger_info
                                }
                                results.append(post_info)
                        except Exception as e:
                            print(f"Error processing content: {e}")
                            continue
            
            print(f"Found {len(results)} matching posts")
            
            if not results:
                results = ["No matching posts found"]
            
        elif not neo4j_available:
            return jsonify({"success": False, "error": "Neo4j features are currently unavailable"}), 503
            
        elif search_type == 'posts_by_gender':
            gender = data.get('gender')
            if not gender:
                return jsonify({"success": False, "error": "Gender is required"}), 400
            results = neo4j_client.GetPostsByGender(gender)
            
        elif search_type == 'posts_by_blogger':
            blogger_id = data.get('blogger_id')
            print(type(blogger_id))
            if not blogger_id:
                return jsonify({"success": False, "error": "Blogger ID is required"}), 400
            print(f"Searching for blogger: {blogger_id}")
            cursor_results = get_posts_by_blogger_id(blogger_id)
            
            if cursor_results is None:
                print("No bloggers returned")
                return jsonify({
                    "success": True,
                    "data": ["No matching bloggers found"],
                    "search_type": search_type
                })
            
            results = []
            cursor_list = list(cursor_results)
            print(f"Found {len(cursor_list)} documents")
            
            for doc in cursor_list:
                if doc is None:
                    print("Skipping None document")
                    continue
                    
                blogger_info = {
                    'blogger_id': doc.get('blogger_id'),
                    'gender': doc.get('gender'),
                    'age': doc.get('age'),
                    'industry': doc.get('industry'),
                    'sign': doc.get('sign')
                }
                
                if not doc.get('posts'):
                    print(f"No posts found for blogger {blogger_info['blogger_id']}")
                    continue
                    
                for post in doc['posts']:
                    if not isinstance(post, dict):
                        print(f"Skipping invalid post format: {type(post)}")
                        continue
                        
                    dates = post.get('date', [])
                    contents = post.get('content', [])
                    
                    if not isinstance(contents, list):
                        print(f"Content is not a list: {type(contents)}")
                        continue

                    for i, content in enumerate(contents):
                        if not content:
                            print(f"Skipping empty content at index {i}")
                            continue
                            
                        try:
                            if i < len(dates):
                                post_info = {
                                    'content': str(content),
                                    'date': dates[i],
                                    'author': blogger_info
                                }
                                results.append(post_info)
                        except Exception as e:
                            print(f"Error processing content: {e}")
                            continue
                        
            
        elif search_type == 'recommendations':
            blogger_id = data.get('blogger_id')
            if not blogger_id:
                return jsonify({
                    "success": False,
                    "error": "Blogger ID is required for recommendations"
                })
                
            print(f"Getting recommendations for blogger: {blogger_id}")
            recommended_ids = neo4j_client.Recommand(int(blogger_id), 10)  # Get top 10 recommendations
            
            if not recommended_ids:
                return jsonify({
                    "success": True,
                    "data": ["No recommendations found"],
                    "search_type": search_type
                })
            
            # Get demographics for each recommended blogger
            recommendations_with_info = []
            for rec_id in recommended_ids:
                print(f"Processing recommendation for blogger: {rec_id}")  # Debug print
                # Query MongoDB for blogger demographics
                blogger_data = collection.find_one({"blogger_id": str(rec_id)})
                print(f"Found blogger data: {blogger_data}")  # Debug print
                
                # Format demographics string if data exists
                demographics = "N/A"
                if blogger_data:
                    demographics = f"{blogger_data.get('gender', 'Unknown')}, {blogger_data.get('age', 'Unknown')} years old, {blogger_data.get('industry', 'Unknown')}, {blogger_data.get('sign', 'Unknown')}"
                
                recommendation = {
                    'author': rec_id,
                    'demographics': demographics
                }
                print(f"Adding recommendation: {recommendation}")  # Debug print
                recommendations_with_info.append(recommendation)
            
            print(f"Final recommendations: {recommendations_with_info}")  # Debug print
            return jsonify({
                "success": True,
                "data": recommendations_with_info,
                "search_type": search_type
            })
            
        else:
            return jsonify({"success": False, "error": "Invalid search type"}), 400

        return jsonify({
            "success": True, 
            "data": results,
            "search_type": search_type
        })

    except Exception as e:
        print(f"Error in search route: {str(e)}")
        print(f"Error occurred at line: {e.__traceback__.tb_lineno}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
