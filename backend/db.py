from pymongo import MongoClient

# Replace <username>, <password>, <cluster-url> with your cluster info
MONGO_URI = "mongodb+srv://josephbwanzj_db_user:josephwan1*@mvpcluster.fgzsm9n.mongodb.net/"
client = MongoClient(MONGO_URI)

# Access database
db = client["MVPDatabase"]

# Collections
users_col = db["MVPUsers"]
files_col = db["MVPFiles"]
