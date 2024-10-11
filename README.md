# FastAPI Assignment

This project is a FastAPI application that provides various endpoints for managing items.

## Setup and Run the Project Locally

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/deepak855/FastAPI-Assignment.git
   cd fastapi_assignment

2. **Install Dependencies**
    pip install -r requirements.txt

3. **Run the Application**
    uvicorn app.main:app --reload
    The application will start running at http://127.0.0.1:8000

4. **Access the Interactive API Documentation**
    Once the server is running, you can access the interactive API documentation by visiting:
    Swagger UI: http://127.0.0.1:8000/docs
    Redoc: http://127.0.0.1:8000/redoc

**Endpoints**
    POST /items => Create a new item.
    GET /items => Retrieve a list of all items.
    GET /items/{item_id} => Retrieve a specific item by its ID.
        item_id: The unique identifier of the item you want to retrieve.
    DELETE /items/{item_id} => Delete a specific item by its ID. 
        item_id: The unique identifier of the item you want to delete.


