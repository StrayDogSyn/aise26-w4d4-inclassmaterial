import requests
import random
import time

# Base URL for the server
BASE_URL = "http://localhost:8000"

# Valid data
valid_usernames = [
    "jenny99",
    "mike_smith23",
    "lucas1987",
    "sara_lee07",
    "david42",
    "laura88",
    "eric_turner15",
    "emma2002",
    "johnny_5",
    "chris_walker12"
]

valid_book_ids = list(range(1, 21))  # 1-20

# Invalid data
invalid_usernames = [
    "john_doe",
    "alice123",
    "bob_williams",
    "nobody",
    "fake_user99",
    "random_person",
    "test_user",
    "unknown_user"
]

invalid_book_ids = [0, 21, 22, 100, 999, -1, -5]

def make_request(url, description):
    """Make a request and print the result"""
    try:
        response = requests.get(url)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} [{response.status_code}] {description}")
        return response.status_code
    except Exception as e:
        print(f"✗ [ERROR] {description} - {str(e)}")
        return None

def chaos_test():
    """Run 100 random good and bad requests"""
    print("=" * 60)
    print("CHAOS TESTING - 100 Random Requests")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for i in range(100):
        # Randomly choose an endpoint type
        endpoint_type = random.choice([
            "root",
            "users_list",
            "user_valid",
            "user_invalid",
            "books_list",
            "book_valid",
            "book_invalid",
            "mock_error"
        ])
        
        if endpoint_type == "root":
            url = f"{BASE_URL}/"
            description = "GET /"
            
        elif endpoint_type == "users_list":
            url = f"{BASE_URL}/users"
            description = "GET /users"
            
        elif endpoint_type == "user_valid":
            username = random.choice(valid_usernames)
            url = f"{BASE_URL}/users/{username}"
            description = f"GET /users/{username} (valid)"
            
        elif endpoint_type == "user_invalid":
            username = random.choice(invalid_usernames)
            url = f"{BASE_URL}/users/{username}"
            description = f"GET /users/{username} (invalid)"
            
        elif endpoint_type == "books_list":
            url = f"{BASE_URL}/books"
            description = "GET /books"
            
        elif endpoint_type == "book_valid":
            book_id = random.choice(valid_book_ids)
            url = f"{BASE_URL}/books/{book_id}"
            description = f"GET /books/{book_id} (valid)"
            
        elif endpoint_type == "book_invalid":
            book_id = random.choice(invalid_book_ids)
            url = f"{BASE_URL}/books/{book_id}"
            description = f"GET /books/{book_id} (invalid)"
            
        elif endpoint_type == "mock_error":
            url = f"{BASE_URL}/mock_error"
            description = "GET /mock_error"
        
        status_code = make_request(url, f"#{i+1:3d} {description}")
        
        if status_code == 200:
            success_count += 1
        else:
            error_count += 1
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.05)
    
    print("=" * 60)
    print(f"SUMMARY:")
    print(f"  Total Requests: 100")
    print(f"  Successful (200): {success_count}")
    print(f"  Errors (4xx/5xx): {error_count}")
    print("=" * 60)

if __name__ == "__main__":
    print("\nMake sure your server is running on http://localhost:8000")
    print("Starting chaos test in 3 seconds...\n")
    time.sleep(3)
    
    chaos_test()

