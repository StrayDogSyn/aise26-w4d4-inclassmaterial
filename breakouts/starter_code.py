from fastapi import FastAPI, HTTPException
import time
import random
import uvicorn
from datetime import datetime

app = FastAPI()


@app.get("/")
def read_root():
    """Home endpoint - lists available endpoints"""
    return {
        "message": "E-commerce API Demo",
        "endpoints": ["/products", "/users", "/error"]
    }

@app.get("/products")
def get_products():
    """Get all products"""
    # Simulate database query
    time.sleep(0.05)
    
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "stock": 5},
        {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
        {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 25}
    ]
    
    return {"products": products, "total": len(products)}


@app.get("/users")
def get_users():
    """Get all users (admin only)"""
    # Simulate admin check
    time.sleep(0.1)
    
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "active": True},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "active": True},
        {"id": 3, "name": "Bob Wilson", "email": "bob@example.com", "active": False}
    ]
    
    return {"users": users, "total": len(users)}


@app.get("/error")
def trigger_error():
    """Trigger an error for testing error handling"""
    try:
        result = 10 / 0
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    print("🚀 Starting E-commerce API Demo")
    print("📋 TODO List:")
    print("   1. Create structured logger (logger.py)")
    print("   2. Add logging to all endpoints")
    print("   3. Test your logging with different scenarios")
    print("   4. Add error handling and logging")
    print("   5. Check your log file output")
    print("\n🔗 API will be available at: http://localhost:8000")
    
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
