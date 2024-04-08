from pymongo.mongo_client import MongoClient

uri = ""

# Create a new client and connect to the server
client = MongoClient(uri)
db = client['video']
data = db['watermark']

def insert_data(wm_len, watermark):
    # 获取数据库长度
    len = data.count_documents({})
    # 插入数据
    data.insert_one({
        "_id": len,
        "wm_len": wm_len,
        "watermark": watermark
    })
    return len

def get_data(id):
    # Get the data from the collection
    return data.find_one({"_id": id})

# print(insert_data(111, "123"))