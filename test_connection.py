"""
Quick script to test MongoDB connection
Run this to verify your MongoDB setup before starting the server
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')

if not MONGODB_URL:
    print("❌ Error: MONGODB_URL not found in .env file")
    print("📝 Please create a .env file with: MONGODB_URL=mongodb://localhost:27017/")
    exit(1)

print(f"🔗 Attempting to connect to: {MONGODB_URL}")

try:
    client = MongoClient(MONGODB_URL)
    # Test the connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # List databases
    databases = client.list_database_names()
    print(f"📊 Available databases: {databases}")
    
    # Check if business_tracker exists
    if 'business_tracker' in databases:
        db = client['business_tracker']
        collections = db.list_collection_names()
        print(f"📁 Collections in business_tracker: {collections}")
        
        if 'businesses' in collections:
            count = db['businesses'].count_documents({})
            print(f"📈 Number of businesses in database: {count}")
    else:
        print("ℹ️  Database 'business_tracker' will be created on first insert")
    
    print("\n✨ Everything is ready! You can now start the Flask server.")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {str(e)}")
    print("\n💡 Troubleshooting:")
    print("   1. Make sure MongoDB is running")
    print("   2. Check your MONGODB_URL in .env file")
    print("   3. For local MongoDB: mongodb://localhost:27017/")
    print("   4. For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
