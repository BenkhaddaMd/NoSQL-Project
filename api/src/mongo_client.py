from pymongo import MongoClient
import os
from bson import ObjectId

mongo_client = MongoClient(
    host=os.getenv("MONGO_HOST", "mongo"),
    port=int(os.getenv("MONGO_PORT", 27017))
)

db = mongo_client.travel_hub
offers_collection = db.offers

def search_offers(from_code, to_code, limit=10):
    return list(offers_collection.find(
        {"from": from_code, "to": to_code},
        {"_id": 1, "provider": 1, "price": 1, "currency": 1, "legs": 1}
    ).sort("price", 1).limit(limit))

def get_offer_details(offer_id):
    try:
        object_id = ObjectId(offer_id)
    except Exception:
        return None

    return offers_collection.find_one({"_id": object_id})

def initialize_mongo():
    # Création des index
    offers_collection.create_index([("from", 1), ("to", 1), ("price", 1)])
    offers_collection.create_index([("provider", "text")])
    
    # Insertion de données de test (optionnel)
    if offers_collection.count_documents({}) == 0:
        offers_collection.insert_many([
            {
                "from": "PAR",
                "to": "LON",
                "provider": "AirFrance",
                "price": 150,
                "currency": "EUR",
                "legs": [{"flightNum": "AF123"}]
            },
            {
                "from": "PAR",
                "to": "NYC",
                "provider": "Delta",
                "price": 450,
                "currency": "EUR",
                "legs": [{"flightNum": "DL456"}]
            },
            {
                "from": "LON",
                "to": "PAR",
                "provider": "British Airways",
                "price": 140,
                "currency": "EUR",
                "legs": [{"flightNum": "BA789"}]
            },
            {
                "from": "PAR",
                "to": "BER",
                "provider": "Lufthansa",
                "price": 120,
                "currency": "EUR",
                "legs": [{"flightNum": "LH101"}]
            },
            {
                "from": "BER",
                "to": "ROM",
                "provider": "Ryanair",
                "price": 60,
                "currency": "EUR",
                "legs": [{"flightNum": "FR202"}]
            },
            {
                "from": "NYC",
                "to": "LON",
                "provider": "United",
                "price": 500,
                "currency": "USD",
                "legs": [{"flightNum": "UA303"}]
            },
            {
                "from": "ROM",
                "to": "PAR",
                "provider": "Air France",
                "price": 130,
                "currency": "EUR",
                "legs": [{"flightNum": "AF404"}]
            },
            {
                "from": "LON",
                "to": "NYC",
                "provider": "Virgin Atlantic",
                "price": 470,
                "currency": "GBP",
                "legs": [{"flightNum": "VS505"}]
            }
        ])