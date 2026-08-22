from fastapi import FastAPI,HTTPException

app = FastAPI()

text_posts = {
    1:{"title":"Introduction to Python","content":"Python is a simple and powerful programming language used for web development, automation, data science, and artificial intelligence."},
    2:{"title":"What is FastAPI?","content":"FastAPI is a modern Python framework used to build fast and scalable REST APIs with automatic documentation and type validation."},
    3:{"title":"Benefits of Learning Java","content":"Java is a popular programming language used for enterprise applications, backend development, Android applications, and large-scale systems."},
    4:{"title":"What is REST API?","content":"A REST API allows different applications to communicate with each other using HTTP methods such as GET, POST, PUT, and DELETE."},
    5:{"title":"Understanding Git","content":"Git is a version control system that helps developers track code changes, create branches, and collaborate with other developers."},
    6:{"title":"What is SQL?","content":"SQL is a language used to store, retrieve, update, and manage data in relational databases such as MySQL and PostgreSQL."},
    7:{"title":"Introduction to Docker","content":"Docker allows developers to package applications and their dependencies into containers so they can run consistently across different environments."},
    8:{"title":"Why Learn Data Structures?","content":"Data structures help developers organize and manage data efficiently. Arrays, linked lists, stacks, queues, and trees are common examples."},
    9:{"title":"What is Spring Boot?","content":"Spring Boot is a Java framework that makes it easier to create production-ready backend applications and REST APIs with minimal configuration."},
    10:{"title":"Importance of APIs","content":"APIs provide a way for different software systems to communicate and exchange data. They are an important part of modern web applications."},
    11:{"title":"What is Machine Learning?","content":"Machine learning is a branch of artificial intelligence that allows computers to learn patterns from data and make predictions or decisions."},
    12:{"title":"Frontend vs Backend","content":"Frontend development focuses on the user interface, while backend development handles business logic, databases, authentication, and APIs."},
    13:{"title":"Why Use MySQL?","content":"MySQL is a popular relational database management system used to store structured data and efficiently perform database operations."},
    14:{"title":"What is Cloud Computing?","content":"Cloud computing provides computing resources such as servers, storage, and databases over the internet without requiring users to manage physical infrastructure."},
    15:{"title":"Importance of Clean Code","content":"Clean code is easy to read, understand, test, and maintain. Writing simple and organized code makes collaboration and future development easier."}
}

@app.get("/post")
def get_all_post():
    return text_posts

@app.get("/post/{id}")
def get_int_post(id:int):
    if id not in text_posts:
        raise HTTPException(status_code=404,detail="Post Not Found")
    return text_posts.get(id)
