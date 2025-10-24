from fastapi import FastAPI, Request
import uvicorn
from fastapi import HTTPException
# from logger import info, error, warning, debug
from logger import info, error, warning, debug
import time
app = FastAPI()

app_start_time = None;

@app.middleware('lifecycle')
async def startup_event(request: Request, call_next):
    global app_start_time
    if app_start_time is None:
        app_start_time = time.time()
        info("Starting the library server", extra_app_start_time=app_start_time)
    else:
        info("Library server already started", extra_app_start_time=app_start_time)
    return await call_next(request)

@app.middleware('lifecycle')
async def shutdown_event(request: Request, call_next):
    global app_start_time
    if app_start_time is not None:
        app_start_time = None
        info("Library server shutdown", extra_app_end_time=app_start_time)
    return await call_next(request)

@app.get("/health")
def health_check():
    uptime = time.time() - app_start_time
    if uptime < 10:
        return {"status": "healthy"}
    else:
        return {"status": "unhealthy"}

#liveness probe
######
# check if the database is connected
# check if the cache is connected
# return the value of these checks in a dictionary

#readiness probe
######
# check if the database is ready
# check if the cache is ready
# return the value of these checks in a dictionary

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

usernames = [
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

@app.get("/users/{username}")
def get_user(username: str):
    try:
        usernames.index(username)
        info("User found", extra_username=username)
    except ValueError:
        error("User not found", extra_username=username)
        raise HTTPException(status_code=404, detail="User not found")

    return {"username": username}


@app.get("/users")
def get_users():
    info("Getting all users")
    return {"users": usernames}

book_titles = {
    1: "Pride and Prejudice",
    2: "Moby Dick",
    3: "To Kill a Mockingbird",
    4: "1984",
    5: "The Great Gatsby",
    6: "War and Peace",
    7: "Jane Eyre",
    8: "The Catcher in the Rye",
    9: "The Odyssey",
    10: "Wuthering Heights",
    11: "Crime and Punishment",
    12: "Great Expectations",
    13: "Little Women",
    14: "Brave New World",
    15: "Anna Karenina",
    16: "The Brothers Karamazov",
    17: "Don Quixote",
    18: "The Grapes of Wrath",
    19: "Les Misérables",
    20: "Frankenstein"
}

@app.get("/books")
def get_books():
    info("Getting all books")
    return {"books": book_titles}

@app.get("/books/{book_id}")
def get_book(book_id: int):
    try:
        book_titles[book_id]
        info("Book found", extra_book_id=book_id)
    except KeyError:
        error("Book not found", extra_book_id=book_id)
        raise HTTPException(status_code=404, detail="Book not found")

    return {"book_id": book_id, "book_title": book_titles[book_id]}

@app.get("/mock_error")
def mock_error():
    error("Don't worry, it's just a test. :)")
    raise HTTPException(status_code=500, detail="Mock error")




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




# # Health Check Endpoints

# @app.get("/health")
# def health_check():
#     """Liveness probe - checks if the application is alive"""
#     # TODO: Add logging here in breakout 3
#     return {
#         "status": "alive",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# @app.get("/ready")
# def readiness_check():
#     """Readiness probe - checks if the application is ready to handle requests"""
#     # TODO: Add logging here in breakout 3
#     return {
#         "status": "ready",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# @app.get("/startup")
# def startup_check():
#     """Startup probe - checks if the application has finished starting up"""
#     # TODO: Add logging here in breakout 3
#     return {
#         "status": "started",
#         "timestamp": datetime.utcnow().isoformat()
#     }
