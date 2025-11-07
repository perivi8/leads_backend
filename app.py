from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for production frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://nexoventlabs-leads.vercel.app",
            "http://localhost:5173",  # For local development
            "http://localhost:5174"
        ]
    }
})

# MongoDB connection - Lazy initialization to avoid blocking startup
MONGODB_URL = os.getenv('MONGODB_URL')
client = None
db = None
collection = None

def get_db_connection():
    """Lazy initialization of MongoDB connection"""
    global client, db, collection
    if client is None:
        try:
            client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000
            )
            db = client['business_tracker']
            collection = db['businesses']
            # Test connection
            client.admin.command('ping')
            print("✅ MongoDB connection successful!")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            client = None
    return client, db, collection

# Test route
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Backend API is running',
        'status': 'success'
    })

# Lightweight health check for cron jobs (minimal response)
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# Test MongoDB connection
@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    try:
        # Initialize connection if needed
        client, db, collection = get_db_connection()
        if client is None:
            raise Exception("Failed to establish MongoDB connection")
        # Ping the database
        client.admin.command('ping')
        return jsonify({
            'message': 'MongoDB connection successful',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'message': 'MongoDB connection failed',
            'status': 'error',
            'error': str(e)
        }), 500

# Get all businesses
@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    try:
        client, db, coll = get_db_connection()
        if coll is None:
            raise Exception("Database connection not available")
        businesses = list(coll.find({}, {'_id': 0}))
        return jsonify({
            'data': businesses,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'message': 'Error fetching businesses',
            'status': 'error',
            'error': str(e)
        }), 500

# Create a new business
@app.route('/api/businesses', methods=['POST'])
def create_business():
    try:
        client, db, coll = get_db_connection()
        if coll is None:
            raise Exception("Database connection not available")
        data = request.get_json()
        # Add createdAt timestamp if not present
        if 'createdAt' not in data:
            data['createdAt'] = datetime.utcnow().isoformat()
        result = coll.insert_one(data)
        return jsonify({
            'message': 'Business created successfully',
            'status': 'success',
            'id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({
            'message': 'Error creating business',
            'status': 'error',
            'error': str(e)
        }), 500

# Update a business
@app.route('/api/businesses/<business_id>', methods=['PUT'])
def update_business(business_id):
    try:
        client, db, coll = get_db_connection()
        if coll is None:
            raise Exception("Database connection not available")
        data = request.get_json()
        result = coll.update_one(
            {'id': int(business_id)},
            {'$set': data}
        )
        if result.matched_count > 0:
            return jsonify({
                'message': 'Business updated successfully',
                'status': 'success'
            })
        else:
            return jsonify({
                'message': 'Business not found',
                'status': 'error'
            }), 404
    except Exception as e:
        return jsonify({
            'message': 'Error updating business',
            'status': 'error',
            'error': str(e)
        }), 500

# Delete a business
@app.route('/api/businesses/<business_id>', methods=['DELETE'])
def delete_business(business_id):
    try:
        client, db, coll = get_db_connection()
        if coll is None:
            raise Exception("Database connection not available")
        result = coll.delete_one({'id': int(business_id)})
        if result.deleted_count > 0:
            return jsonify({
                'message': 'Business deleted successfully',
                'status': 'success'
            })
        else:
            return jsonify({
                'message': 'Business not found',
                'status': 'error'
            }), 404
    except Exception as e:
        return jsonify({
            'message': 'Error deleting business',
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
