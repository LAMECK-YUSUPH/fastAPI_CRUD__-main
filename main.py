# Importing Union for specifying multiple possible types
from typing import Union

# Importing FastAPI and HTTPException for creating API endpoints and handling HTTP exceptions
from fastapi import FastAPI, HTTPException

# Importing BaseModel for defining data models and EmailStr for email validation
from pydantic import BaseModel, EmailStr

# Importing CryptContext for password hashing
from passlib.context import CryptContext

# Importing the function to establish a database connection from the database module
from database import get_database_connection

# Creating a FastAPI instance
app = FastAPI()

# Defining a Pydantic data model for User
class User(BaseModel):
    name: str
    email: EmailStr
    password: str

# Adding password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Endpoint to create a new user
@app.post("/users")
async def create_user(user: User):
    # Validate email domain
    if not user.email.endswith("@gmail.com"):
        raise HTTPException(status_code=400, detail="Email must be @gmail.com")

    # Connect to the database
    connection = get_database_connection()
    cursor = connection.cursor()

    # SQL query to insert user data
    query = "INSERT INTO customer (name, email, password) VALUES (%s, %s, %s)"
    values = (user.name, user.email, pwd_context.hash(user.password))

    # Execute the SQL query
    cursor.execute(query, values)
    # Commit the transaction
    connection.commit()
    # Close the database connection
    connection.close()

    return {"message": "User created successfully"}

# Endpoint to get user by user_id
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM customer WHERE id = %s"
    values = (user_id,)

    cursor.execute(query, values)
    user = cursor.fetchone()

    connection.close()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user[0], "name": user[1], "email": user[2]}

# Endpoint to get all users
@app.get("/users")
async def get_users():
    connection = get_database_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM customer"

    cursor.execute(query)
    users = cursor.fetchall()

    connection.close()

    return users

# Endpoint to update user by user_id
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = "UPDATE customer SET name = %s, email = %s, password = %s WHERE id = %s"
    values = (user.name, user.email, pwd_context.hash(user.password), user_id)

    cursor.execute(query, values)
    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User updated successfully"}

# Endpoint to delete user by user_id
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = "DELETE FROM customer WHERE id = %s"
    values = (user_id,)

    cursor.execute(query, values)
    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}