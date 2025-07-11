from neo4j import GraphDatabase
import os

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), 
          os.getenv("NEO4J_PASSWORD", "Test1234@"))
)

def get_recommendations(city_code, k=3):
    query = """
    MATCH (c:City {code:$city})-[:NEAR]->(n:City)
    RETURN n.code AS city, n.name AS name, n.weight AS score 
    ORDER BY score DESC LIMIT $k
    """
    with driver.session() as session:
        result = session.run(query, city=city_code, k=k)
        return [dict(record) for record in result]

def initialize_neo4j():
    query = """
    MERGE (paris:City {code: 'PAR', name: 'Paris', country: 'FR'})
    MERGE (london:City {code: 'LON', name: 'London', country: 'UK'})
    MERGE (nyc:City {code: 'NYC', name: 'New York', country: 'US'})
    
    MERGE (paris)-[:NEAR {weight: 0.8}]->(london)
    MERGE (london)-[:NEAR {weight: 0.8}]->(paris)
    MERGE (paris)-[:NEAR {weight: 0.5}]->(nyc)
    """
    with driver.session() as session:
        session.run(query)