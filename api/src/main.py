from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import json
import gzip
from datetime import datetime
from typing import Optional

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
from src.mongo_client import initialize_mongo, mongo_client, search_offers, get_offer_details
from src.neo4j_client import initialize_neo4j, get_recommendations


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

@app.get("/offers")
async def search_offers(from_code: str, to_code: str, limit: int = 10):
    try:
        # 1. Vérifier le cache Redis
        cached = get_cached_offers(from_code, to_code)
        if cached:
            return JSONResponse(cached[:limit])
        
        # 2. Requête MongoDB si cache miss
        offers = search_offers(from_code, to_code, limit)
        
        # 3. Mise en cache
        cache_offers(from_code, to_code, offers)
        
        return JSONResponse(offers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reco")
async def get_recommendations(city: str, k: int = 3):
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
async def get_offer_details(offer_id: str):
    try:
        # 1. Vérifier le cache
        cached = get_cached_offer_details(offer_id)
        if cached:
            return JSONResponse(cached)
        
        # 2. Requête MongoDB
        offer = get_offer_details(offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        
        # 3. Mise en cache
        cache_offer_details(offer_id, offer)
        
        return JSONResponse(offer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))