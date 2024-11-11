from pymongo import MongoClient

# MongoDB client setup
MONGO_CLIENT = MongoClient("mongodb+srv://codogmjo:ciferX091@mern-trial.ytk7j.mongodb.net/PyChat?retryWrites=true&w=majority&appName=mern-trial")
MONGO_DB = MONGO_CLIENT['PyChat']