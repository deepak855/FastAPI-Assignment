from fastapi import FastAPI, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, date
from pydantic import EmailStr
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


# -------------------- Items API --------------------

@app.post("/items", response_description="Create a new item", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """
    Creates a new item in the database.
    """
    item = jsonable_encoder(item)
    item["insert_date"] = datetime.utcnow()
    new_item = await items_collection.insert_one(item)
    created_item = await items_collection.find_one({"_id": new_item.inserted_id})
    if created_item:
        return Item(**created_item)  
    raise HTTPException(status_code=500, detail="Item creation failed")


@app.get("/items/{id}", response_description="Get a single item by ID", response_model=Item)
async def get_item(id: str):
    """
    Retrieves an item by its ID.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    item = await items_collection.find_one({"_id": ObjectId(id)})
    if item:
        return Item(**item) 
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/items/filter", response_description="List items with optional filters", response_model=List[Item])
async def filter_items(
    email: Optional[EmailStr] = Query(None, description="Filter by exact email"),
    expiry_date: Optional[date] = Query(None, description="Filter items expiring after this date (YYYY-MM-DD)"),
    insert_date: Optional[datetime] = Query(None, description="Filter items inserted after this datetime (ISO format)"),
    quantity: Optional[int] = Query(None, ge=0, description="Filter items with quantity >= this number"),
):
    """
    Filters items based on query parameters.
    """
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
        items.append(Item(**item))  
    return items



@app.delete("/items/{id}", response_description="Delete an item", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(id: str):
    """
    Deletes an item by its ID.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = await items_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{id}", response_description="Update an item", response_model=Item)
async def update_item(id: str, item: ItemUpdate):
    """
    Updates an item's details by ID (excluding the insert_date).
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    item_data = {k: v for k, v in item.dict().items() if v is not None}
    if "insert_date" in item_data:
        del item_data["insert_date"]  
    if item_data:
        update_result = await items_collection.update_one({"_id": ObjectId(id)}, {"$set": item_data})
        if update_result.modified_count == 1:
            updated_item = await items_collection.find_one({"_id": ObjectId(id)})
            if updated_item:
                return Item(**updated_item)  
    existing_item = await items_collection.find_one({"_id": ObjectId(id)})
    if existing_item:
        return Item(**existing_item)  
    raise HTTPException(status_code=404, detail="Item not found")

# -------------------- Clock-In Records API --------------------

@app.post("/clock-in", response_description="Create a new clock-in record", response_model=ClockInRecord, status_code=status.HTTP_201_CREATED)
async def create_clockin(record: ClockInCreate):
    """
    Creates a new clock-in record in the database.
    """
    record = jsonable_encoder(record)
    record["insert_datetime"] = datetime.utcnow()
    new_record = await clockin_collection.insert_one(record)
    created_record = await clockin_collection.find_one({"_id": new_record.inserted_id})
    if created_record:
        return ClockInRecord(**created_record)  
    raise HTTPException(status_code=500, detail="Clock-In record creation failed")

@app.get("/clock-in/{id}", response_description="Get a clock-in record by ID", response_model=ClockInRecord)
async def get_clockin(id: str):
    """
    Retrieves a clock-in record by its ID.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    record = await clockin_collection.find_one({"_id": ObjectId(id)})
    if record:
        return ClockInRecord(**record)  
    raise HTTPException(status_code=404, detail="Clock-In record not found")

@app.get("/clock-in/filter", response_description="Filter clock-in records", response_model=List[ClockInRecord])
async def filter_clockins(
    email: Optional[EmailStr] = Query(None, description="Filter by exact email"),
    location: Optional[str] = Query(None, description="Filter by exact location"),
    insert_datetime: Optional[datetime] = Query(None, description="Filter clock-ins after this datetime (ISO format)"),
):
    """
    Filters clock-in records based on query parameters.
    """
    query = {}
    if email:
        query["email"] = email
    if location:
        query["location"] = location
    if insert_datetime:
        query["insert_datetime"] = {"$gt": insert_datetime}
    
    records = []
    async for record in clockin_collection.find(query):
        records.append(ClockInRecord(**record))  
    return records

@app.delete("/clock-in/{id}", response_description="Delete a clock-in record", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clockin(id: str):
    """
    Deletes a clock-in record by its ID.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = await clockin_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    raise HTTPException(status_code=404, detail="Clock-In record not found")

@app.put("/clock-in/{id}", response_description="Update a clock-in record", response_model=ClockInRecord)
async def update_clockin(id: str, record: ClockInUpdate):
    """
    Updates a clock-in record by ID (excluding insert_datetime).
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    record_data = {k: v for k, v in record.dict().items() if v is not None}
    if "insert_datetime" in record_data:
        del record_data["insert_datetime"]  
    if record_data:
        update_result = await clockin_collection.update_one({"_id": ObjectId(id)}, {"$set": record_data})
        if update_result.modified_count == 1:
            updated_record = await clockin_collection.find_one({"_id": ObjectId(id)})
            if updated_record:
                return ClockInRecord(**updated_record)  
    existing_record = await clockin_collection.find_one({"_id": ObjectId(id)})
    if existing_record:
        return ClockInRecord(**existing_record)  
    raise HTTPException(status_code=404, detail="Clock-In record not found")

# -------------------- Root Endpoint --------------------

@app.get("/", response_description="Welcome message")
async def root():
    return {"message": "Welcome to the FastAPI CRUD Application!"}
