import pymongo
from pymongo import MongoClient
from replit import db

cluster = MongoClient("mongodb+srv://Yapa-Bot-Official:<zdKwyRadkUfZeqj4>@yapa-cluster.btsf9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db_mongo = cluster.test
