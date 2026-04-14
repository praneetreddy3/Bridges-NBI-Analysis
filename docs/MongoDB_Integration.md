# MongoDB Integration Guide

## Overview

This guide explains how to integrate the Bridges NBI dataset with MongoDB for NoSQL querying and flexible data analysis.

## Prerequisites

- Python 3.7+
- PyMongo library installed: `pip install pymongo`
- Either MongoDB local installation OR MongoDB Atlas cloud account

## Option 1: MongoDB Local Installation

### Step 1: Install MongoDB

#### macOS (using Homebrew)
```bash
brew install mongodb-community
brew services start mongodb-community
```

#### Windows
1. Download MongoDB Community Edition from: https://www.mongodb.com/try/download/community
2. Run the installer
3. MongoDB service should start automatically
4. Verify: Open Command Prompt and run `mongosh`

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install -y mongodb

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
mongosh
```

### Step 2: Verify MongoDB is Running

```bash
# Connect to MongoDB shell
mongosh

# Should see a prompt like: test>
# Type: exit to quit
```

### Step 3: Import Data

#### Method A: Using mongoimport (Command Line)

```bash
# Navigate to data directory
cd Bridges-NBI-Analysis/data

# Import CSV to MongoDB
mongoimport --db bridge_db \
            --collection bridges \
            --type csv \
            --headerline \
            --file CleanedBridgeDataset_2024and2025.csv

# Expected output:
# Import success with message like:
# inserted 950000 documents into bridges
```

#### Method B: Using Python Script

Create file: `scripts/import_mongodb_local.py`

```python
#!/usr/bin/env python3
"""
Import Bridges dataset to local MongoDB
Run: python scripts/import_mongodb_local.py
"""

import pandas as pd
import pymongo
from pymongo import MongoClient
import sys

def import_bridges_data(csv_path):
    """Import bridges CSV to MongoDB local instance"""
    
    # Connect to MongoDB (local default)
    client = MongoClient('mongodb://localhost:27017/')
    db = client['bridge_db']
    collection = db['bridges']
    
    print(f"Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"Preparing {len(df)} records for import...")
    records = df.to_dict('records')
    
    # Clear existing data (optional)
    # collection.delete_many({})
    
    print("Importing to MongoDB...")
    result = collection.insert_many(records, ordered=False)
    
    print(f"✓ Successfully imported {len(result.inserted_ids)} documents")
    print(f"  Database: bridge_db")
    print(f"  Collection: bridges")
    
    # Verify import
    count = collection.count_documents({})
    print(f"  Total documents in collection: {count}")
    
    # Create index on state_name for faster queries
    collection.create_index("state_name")
    print("✓ Created index on state_name")
    
    return True

if __name__ == "__main__":
    csv_path = "data/CleanedBridgeDataset_2024and2025.csv"
    
    try:
        import_bridges_data(csv_path)
        print("\n✓ Import completed successfully!")
    except FileNotFoundError:
        print(f"❌ Error: {csv_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during import: {e}")
        sys.exit(1)
```

Run:
```bash
python scripts/import_mongodb_local.py
```

### Step 4: Verify Data Import

```bash
# Connect to MongoDB shell
mongosh

# Switch to bridge_db
use bridge_db

# Count documents
db.bridges.countDocuments({})
# Expected: 950000

# View sample document
db.bridges.findOne()

# View document structure
db.bridges.findOne({}, {projection: {_id: 0}})
```

## Option 2: MongoDB Atlas (Cloud)

### Step 1: Create MongoDB Atlas Account

1. Go to: https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create organization and project

### Step 2: Create Free Cluster

1. Click "Create Deployment"
2. Select **M0 Free Tier**
3. Choose cloud provider (AWS/Google Cloud/Azure) - default fine
4. Choose region closest to you
5. Click "Create Deployment"

### Step 3: Get Connection String

1. Go to "Database" section
2. Click "Connect" on your cluster
3. Select "Connect your application"
4. Choose Python driver
5. Copy connection string (looks like):
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/bridge_db?retryWrites=true&w=majority
   ```

### Step 4: Create MongoDB User

1. In Atlas dashboard, go to "Database Access"
2. Click "Add New Database User"
3. Create username (e.g., "bridge_admin")
4. Create password (save securely)
5. Click "Add User"

### Step 5: Import Data to Atlas

Create file: `scripts/import_mongodb_atlas.py`

```python
#!/usr/bin/env python3
"""
Import Bridges dataset to MongoDB Atlas
Update CONNECTION_STRING with your Atlas credentials
Run: python scripts/import_mongodb_atlas.py
"""

import pandas as pd
import pymongo
from pymongo import MongoClient
import sys
import os

# Replace with your MongoDB Atlas connection string
CONNECTION_STRING = "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/bridge_db?retryWrites=true&w=majority"

def import_bridges_data_atlas(csv_path, connection_string):
    """Import bridges CSV to MongoDB Atlas"""
    
    # Connect to MongoDB Atlas
    client = MongoClient(connection_string)
    db = client['bridge_db']
    collection = db['bridges']
    
    print(f"Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"Preparing {len(df)} records for import...")
    records = df.to_dict('records')
    
    # Optional: Clear existing data
    # collection.delete_many({})
    
    print("Importing to MongoDB Atlas...")
    try:
        result = collection.insert_many(records, ordered=False)
        print(f"✓ Successfully imported {len(result.inserted_ids)} documents")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Verify import
    count = collection.count_documents({})
    print(f"✓ Total documents in collection: {count}")
    
    # Create indexes
    collection.create_index("state_name")
    collection.create_index("posting_code")
    print("✓ Created indexes for faster queries")
    
    return True

if __name__ == "__main__":
    csv_path = "data/CleanedBridgeDataset_2024and2025.csv"
    
    if CONNECTION_STRING == "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/bridge_db?retryWrites=true&w=majority":
        print("❌ Error: Please update CONNECTION_STRING with your MongoDB Atlas credentials")
        sys.exit(1)
    
    try:
        import_bridges_data_atlas(csv_path, CONNECTION_STRING)
        print("\n✓ Import to MongoDB Atlas completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
```

Run:
```bash
# First, update CONNECTION_STRING variable with your Atlas credentials
python scripts/import_mongodb_atlas.py
```

## MongoDB Query Examples

### Connect from Python

```python
from pymongo import MongoClient

# Local
client = MongoClient('mongodb://localhost:27017/')

# Or Atlas (replace with your connection string)
# client = MongoClient('mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/bridge_db?retryWrites=true&w=majority')

db = client['bridge_db']
collection = db['bridges']
```

### Basic Queries

```python
# Count total bridges
count = collection.count_documents({})
print(f"Total bridges: {count}")

# Find bridges in Texas
texas_bridges = list(collection.find({"state_name": "TX"}, limit=5))
print(f"Texas bridges: {texas_bridges}")

# Find posted bridges (restricted for trucks)
posted_bridges = collection.count_documents({"posting_code": 1})
print(f"Posted bridges: {posted_bridges}")

# Find high truck traffic bridges
high_truck = collection.find(
    {"truck_pct": {"$gt": 75}},
    {"state_name": 1, "truck_pct": 1, "_id": 0},
    limit=10
)
print("High truck traffic bridges:")
for bridge in high_truck:
    print(bridge)

# Find old bridges (built before 1900)
old_bridges = collection.count_documents({"year_built": {"$lt": 1900}})
print(f"Bridges built before 1900: {old_bridges}")
```

### Aggregation Queries

```python
# Average traffic by state (top 5)
pipeline = [
    {
        "$group": {
            "_id": "$state_name",
            "avg_traffic": {"$avg": "$avg_daily_traffic"},
            "bridge_count": {"$sum": 1}
        }
    },
    {"$sort": {"avg_traffic": -1}},
    {"$limit": 5}
]
results = list(collection.aggregate(pipeline))
for state in results:
    print(f"{state['_id']}: {state['avg_traffic']:.0f} avg traffic ({state['bridge_count']} bridges)")

# Posted vs Non-Posted by State
pipeline = [
    {
        "$group": {
            "_id": {
                "state": "$state_name",
                "posted": "$posting_code"
            },
            "count": {"$sum": 1}
        }
    },
    {"$sort": {"_id.state": 1, "_id.posted": -1}}
]
results = list(collection.aggregate(pipeline))
for result in results[:10]:
    status = "Posted" if result['_id']['posted'] else "Not Posted"
    print(f"{result['_id']['state']}: {status} - {result['count']} bridges")
```

### MongoDB Compass (GUI)

For visual browsing of data:

1. Download MongoDB Compass: https://www.mongodb.com/products/compass
2. Connect to MongoDB (local or Atlas)
3. Browse database and collections
4. View documents visually
5. Build queries without command line

## Security Notes

### Local MongoDB
- Default security: minimal authentication needed
- Only listen on localhost
- Suitable for development only

### MongoDB Atlas
- Always use strong passwords
- Store credentials in `.env` file, never in code
- Use Network Access whitelist to restrict IP addresses
- Enable encryption at rest
- Use VPC peering for production

### Environment Variables (.env)

```bash
# Create .env file in project root
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/bridge_db?retryWrites=true&w=majority
```

```python
# Load in Python
import os
from dotenv import load_dotenv

load_dotenv()
connection_string = os.getenv('MONGO_URI')
client = MongoClient(connection_string)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure MongoDB service is running: `sudo systemctl start mongod` |
| Authentication failed | Verify username/password in connection string; check Database Access in Atlas |
| Import timeout | For large datasets, import in batches; reduce batch size |
| No documents after import | Verify CSV file path is correct; check CSV has data before import |
| Collection not found in Atlas | Verify collection name matches in code; Atlas may be case-sensitive |
| Slow queries | Create indexes: `collection.create_index("field_name")` |

## Performance Tips

### Indexing
```python
# Create indexes for faster queries
collection.create_index("state_name")
collection.create_index("posting_code")
collection.create_index("bridge_age")
collection.create_index([("state_name", 1), ("posting_code", 1)])  # compound
```

### Batch Operations
```python
# For bulk inserts, use ordered=False for speed
records = df.to_dict('records')
collection.insert_many(records, ordered=False)
```

### Connection Pooling
```python
# Atlas auto-handles pooling; for local:
client = MongoClient(
    'mongodb://localhost:27017/',
    maxPoolSize=50,
    minPoolSize=10
)
```

## Resources

- MongoDB Documentation: https://docs.mongodb.com/
- PyMongo Documentation: https://pymongo.readthedocs.io/
- MongoDB Atlas Guide: https://docs.atlas.mongodb.com/
- MongoDB Aggregation: https://docs.mongodb.com/manual/aggregation/

---

**Last Updated:** April 2026

For questions, refer to MongoDB official documentation or project README.
