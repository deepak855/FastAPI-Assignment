from fastapi import FastAPI, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, date
from pydantic import BaseModel, EmailStr

from models import (
    Item,
    ItemCreate,
    ItemUpdate,
    ClockInRecord,
    ClockInCreate,
    ClockInUpdate,
)
from database import items_collection, clockin_collection

app = FastAPI(
    title="FastAPI CRUD Application",
    description="A FastAPI application to perform CRUD operations on Items and User Clock-In Records.",
    version="1.0.0",
)

# -------------------- Helper Functions --------------------

def item_helper(item) -> dict:
    """Convert a MongoDB item document to a dict compatible with the Item Pydantic model."""
    print("item_helper :",item)
    return {
        "id": item["_id"],
        "name": item["name"],
        "email": item["email"],
        "item_name": item["item_name"],
        "quantity": item["quantity"],
        "expiry_date": item["expiry_date"],
        "insert_date": item["insert_date"],
    }

def clockin_helper(record) -> dict:
    """Convert a MongoDB clock-in record document to a dict compatible with the ClockInRecord Pydantic model."""
    return {
        "id": str(record["_id"]),
        "email": record["email"],
        "location": record["location"],
        "insert_datetime": record["insert_datetime"],
    }

# -------------------- Items API --------------------

@app.post("/items", response_description="Create a new item", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item in the database."""
    item_data = jsonable_encoder(item)
    item_data["insert_date"] = datetime.utcnow()
    new_item = await items_collection.insert_one(item_data)
    created_item = await items_collection.find_one({"_id": new_item.inserted_id})
    if created_item:
        return Item(**item_helper(created_item))  # Pydantic validator handles ObjectId conversion
    raise HTTPException(status_code=500, detail="Item creation failed")

@app.get("/items/{id}", response_description="Get a single item by ID", response_model=Item)
async def get_item(id: str):
    """Retrieve an item by its ID."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    item = await items_collection.find_one({"_id": ObjectId(id)})
    if item:
        return Item(**item)  # Pydantic validator handles ObjectId conversion
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/items/filter", response_description="List items with optional filters", response_model=List[Item])
async def filter_items(
    email: Optional[EmailStr] = Query(None, description="Filter by exact email"),
    expiry_date: Optional[date] = Query(None, description="Filter items expiring after this date (YYYY-MM-DD)"),
    insert_date: Optional[datetime] = Query(None, description="Filter items inserted after this datetime (ISO format)"),
    quantity: Optional[int] = Query(None, ge=0, description="Filter items with quantity >= this number"),
):
    """Filters items based on query parameters."""
    query = {}
    if email:
        query["email"] = email
    if expiry_date:
        query["expiry_date"] = {"$gt": expiry_date}
    if insert_date:
        query["insert_date"] = {"$gt": insert_date}
    if quantity is not None:
        query["quantity"] = {"$gte": quantity}
    
    items = []
    async for item in items_collection.find(query):
        items.append(Item(**item_helper(item)))  # Use helper function here
    return items

@app.get("/items/aggregate", response_description="Aggregate items count by email")
async def aggregate_items():
    """Aggregates the count of items grouped by email."""
    pipeline = [
        {"$group": {"_id": "$email", "count": {"$sum": 1}}},
        {"$project": {"email": "$_id", "count": 1, "_id": 0}},
    ]
    aggregation = []
    async for doc in items_collection.aggregate(pipeline):
        aggregation.append(doc)
    return aggregation

@app.delete("/items/{id}", response_description="Delete an item", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(id: str):
    """Deletes an item by its ID."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = await items_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{id}", response_description="Update an item", response_model=Item)
async def update_item(id: str, item: ItemUpdate):
    """Updates an item's details by ID (excluding the insert_date)."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    item_data = {k: v for k, v in item.dict().items() if v is not None}
    if "insert_date" in item_data:
        del item_data["insert_date"]  # Exclude insert_date from updates
    if item_data:
        update_result = await items_collection.update_one({"_id": ObjectId(id)}, {"$set": item_data})
        if update_result.modified_count == 1:
            updated_item = await items_collection.find_one({"_id": ObjectId(id)})
            print("updated_item :",updated_item)
            if updated_item:
                return Item(**item_helper(updated_item))  # Use helper function here
    # print("returned")
    # existing_item = await items_collection.find_one({"_id": ObjectId(id)})
    # if existing_item:
    #     return Item(**item_helper(existing_item))  # Use helper function here
    raise HTTPException(status_code=404, detail="Item not found")

# -------------------- Clock-In Records API --------------------

@app.post("/clock-in", response_description="Create a new clock-in record", response_model=ClockInRecord, status_code=status.HTTP_201_CREATED)
async def create_clockin(record: ClockInCreate):
    """Creates a new clock-in record in the database."""
    record_data = jsonable_encoder(record)
    record_data["insert_datetime"] = datetime.utcnow()
    new_record = await clockin_collection.insert_one(record_data)
    created_record = await clockin_collection.find_one({"_id": new_record.inserted_id})
    if created_record:
        return ClockInRecord(**clockin_helper(created_record))  # Use helper function here
    raise HTTPException(status_code=500, detail="Clock-In record creation failed")

@app.get("/clock-in/{id}", response_description="Get a clock-in record by ID", response_model=ClockInRecord)
async def get_clockin(id: str):
    """Retrieves a clock-in record by its ID."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    record = await clockin_collection.find_one({"_id": ObjectId(id)})
    if record:
        return ClockInRecord(**clockin_helper(record))  # Use helper function here
    raise HTTPException(status_code=404, detail="Clock-In record not found")

@app.get("/clock-in/filter", response_description="Filter clock-in records", response_model=List[ClockInRecord])
async def filter_clockins(
    email: Optional[EmailStr] = Query(None, description="Filter by exact email"),
    location: Optional[str] = Query(None, description="Filter by exact location"),
    insert_datetime: Optional[datetime] = Query(None, description="Filter clock-ins after this datetime (ISO format)"),
):
    """Filters clock-in records based on query parameters."""
    query = {}
    if email:
        query["email"] = email
    if location:
        query["location"] = location
    if insert_datetime:
        query["insert_datetime"] = {"$gt": insert_datetime}
    
    records = []
    async for record in clockin_collection.find(query):
        records.append(ClockInRecord(**clockin_helper(record)))  # Use helper function here
    return records

