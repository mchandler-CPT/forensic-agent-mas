import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
AUTH = (USER, PASSWORD)

def generate_embeddings():
    print("🚀 Starting Semantic Feature Engineering (Embeddings)...")
    
    # 1. Load Local Model (Free & Fast)
    print("   📥 Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    with driver.session() as session:
        # 2. Fetch Cards that need embeddings
        # (We skip cards with no text or existing embeddings to allow restartability)
        print("   🔍 Fetching cards with rules text...")
        result = session.run("""
            MATCH (c:Card)
            WHERE c.text IS NOT NULL AND c.text <> "" 
            AND c.embedding IS NULL
            RETURN c.name AS name, c.text AS text
        """)
        
        cards = [{"name": r["name"], "text": r["text"]} for r in result]
        print(f"   📊 Found {len(cards)} cards to embed.")
        
        if not cards:
            print("   ✅ No new cards to process.")
            return

        # 3. Batch Process
        batch_size = 500
        total_processed = 0
        
        # Query to write embeddings back
        write_query = """
        UNWIND $batch as item
        MATCH (c:Card {name: item.name})
        SET c.embedding = item.vector
        """

        for i in range(0, len(cards), batch_size):
            batch = cards[i : i + batch_size]
            texts = [card["text"] for card in batch]
            
            # Generate Embeddings (The Magic Step)
            # This runs locally on your CPU/GPU
            vectors = model.encode(texts)
            
            # Prepare data for Neo4j
            update_data = []
            for card, vector in zip(batch, vectors):
                update_data.append({
                    "name": card["name"],
                    "vector": vector.tolist() # Convert numpy array to list
                })
            
            # Write to DB
            session.run(write_query, batch=update_data)
            
            total_processed += len(batch)
            print(f"     -> Embedded {total_processed}/{len(cards)} cards...")

    driver.close()
    print("\n✅ Semantic Embeddings Complete.")

if __name__ == "__main__":
    generate_embeddings()