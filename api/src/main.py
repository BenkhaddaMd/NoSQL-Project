from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import json
import gzip
from datetime import datetime
from typing import Optional
from bson import ObjectId

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clients (à implémenter dans les fichiers séparés)
from src.redis_client import (
    cache_offer_details,
    cache_offers,
    create_session,
    get_cached_offer_details,
    get_cached_offers,
    redis_client
)
from src.mongo_client import initialize_mongo, mongo_client, search_offers
from src.neo4j_client import initialize_neo4j, get_recommendations
from src.mongo_client import get_offer_details as mongo_get_offer_details

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
def read_root():
    return {"message": "SupDeVinci Travel Hub API"}

@app.on_event("startup")
async def startup_db_clients():
    # Initialisation des bases de données
    initialize_mongo()
    initialize_neo4j()

def serialize_offer(offer):
    offer["_id"] = str(offer["_id"])
    return offer

@app.get("/offers")
async def get_offers(from_code: str, to_code: str, limit: int = 10):
    try:
        cached = get_cached_offers(from_code, to_code)
        if cached:
            return JSONResponse(content=cached[:limit])

        offers = search_offers(from_code, to_code, limit)
        offers = [serialize_offer(offer) for offer in offers]  # conversion _id

        cache_offers(from_code, to_code, offers)

        return JSONResponse(content=offers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reco")
async def get_recommendations_route(city: str, k: int = 3):
    try:
        recommendations = get_recommendations(city, k)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(userId: str):
    try:
        session_id = create_session(userId)
        return {
            "token": session_id,
            "expires_in": 900
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/offers/{offer_id}")
async def get_offer_details_route(offer_id: str):
    try:
        cached = get_cached_offer_details(offer_id)
        if cached:
            return JSONResponse(content=cached)

        offer = mongo_get_offer_details(offer_id)  # pas de await ici
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")

        offer["_id"] = str(offer["_id"])
        cache_offer_details(offer_id, offer)

        return JSONResponse(content=offer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))