from pymongo import MongoClient

# Your MongoDB connection string
client = MongoClient("mongodb+srv://codogmjo:ciferX091@mern-trial.ytk7j.mongodb.net/PyChat?retryWrites=true&w=majority&appName=mern-trial")
db = client['PyChat']
