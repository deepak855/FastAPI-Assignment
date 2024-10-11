# database.py

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING

MONGO_DETAILS = "mongodb://localhost:27017"  # Replace with your MongoDB URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.fastapi_db

# Collections
items_collection = database.get_collection("items_collection")
clockin_collection = database.get_collection("clockin_collection")

# Create indexes if necessary (e.g., for efficient querying)
# Example: items_collection.create_index([("email", ASCENDING)])
