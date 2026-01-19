# api.py
import os
import pydantic_compat
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import threading
from datetime import datetime
import numpy as np
import pandas as pd
import xgboost as xgb
from sentence_transformers import SentenceTransformer

# Import our existing Neo4j connection class
from main import Neo4jConnection

# --- 1. Import LangChain & LangGraph ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain 
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.tools import Tool, StructuredTool
from langchain_core.messages import HumanMessage

# --- NEW: LangGraph Imports ---
from langgraph.prebuilt import create_react_agent

# Load environment variables (.env file)
load_dotenv()

# --- 2. LOGGING & LESSONS SETUP ---
LOG_FILE = "query_log.jsonl"
LESSONS_FILE = "lessons.txt"
MODEL_FILE = "price_predictor.json" # ML Model
log_lock = threading.Lock()

def log_episode(data: dict):
    try:
        with log_lock:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
    except Exception as e:
        print(f"--- LOGGING FAILED: {e} ---")

def load_lessons():
    if not os.path.exists(LESSONS_FILE):
        return "" 
    with open(LESSONS_FILE, "r", encoding="utf-8") as f:
        lessons = f.read()
    print(f"--- Loaded {len(lessons.splitlines())} lessons from semantic memory ---")
    return lessons

# --- 3. ML MODEL SETUP (NEW) ---
print("⏳ Loading ML Models (XGBoost + Embeddings)...")
try:
    # Load XGBoost
    price_model = xgb.XGBRegressor()
    price_model.load_model(MODEL_FILE)
    print("   ✅ Price Predictor loaded.")

    # Load Embedder
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("   ✅ Embedding Model loaded.")
    
    ML_AVAILABLE = True
except Exception as e:
    print(f"   ⚠️ ML Models failed to load: {e}")
    print("   (Prediction tool will be disabled)")
    ML_AVAILABLE = False


# --- App & Connection Setup ---

app = FastAPI(
    title="MTG Knowledge Graph API",
    description="An API for querying the MTG knowledge graph with natural language."
)

# Database connection
neo4j_conn = Neo4jConnection(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD")
)

# --- 4. Set up the Tools ---

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
loaded_lessons = load_lessons()

# -- Tool 1: Graph QA --
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Cypher query translator.
A user will ask a question about a Magic: The Gathering card database.
Respond with a Cypher query that can answer the question.
Do not add any explanation or preamble.

**Instructions:**
- **CRITICAL:** Ensure you account for ALL constraints in the user's question.
- When a user asks for "most expensive" cards, use `WHERE p.price_usd IS NOT NULL` and `ORDER BY p.price_usd DESC`.
- When a user asks for "cheap" cards, use `WHERE p.price_usd IS NOT NULL` and `ORDER BY p.price_usd ASC`.
- Card `manaCost` is a string like '{{2}}{{B}}', not a number. Use `CONTAINS`.
- "Black", "Blue", "White", "Red", "Green" are `Color` nodes.
- "Creature", "Instant", "Sorcery", "Enchantment" are `CardType` nodes.

**Learned Lessons:**
{lessons}

**Schema:**
{schema}

**Question:**
{question}

**Cypher Query:**
"""

CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question", "lessons"], 
    template=CYPHER_GENERATION_TEMPLATE
).partial(lessons=loaded_lessons)

QA_GENERATION_TEMPLATE = """
You are a helpful assistant answering questions about Magic: The Gathering cards.
Use the following context (database results) to answer the user's question.

**User Question:** {question}
**Database Context:** {context}

**Instructions:**
1. If the context contains a list of cards, list them out clearly.
2. Include their prices if available.
3. If the context contains duplicates, mention the card only once.
4. Do NOT say "I don't know" if there is data in the context. Use the provided data to form an answer.
"""

QA_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template=QA_GENERATION_TEMPLATE
)

cypher_qa_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
    return_intermediate_steps=True,
    cypher_prompt=CYPHER_PROMPT,
    qa_prompt=QA_PROMPT
)

class GraphToolInput(BaseModel):
    query: str = Field(description="The natural language question to answer using the database.")

def run_graph_tool(query: str):
    print(f"\n[DEBUG] Graph Tool called with input: {query}")
    try:
        q = query if isinstance(query, str) else str(query)
        result = cypher_qa_chain.invoke({"query": q})
        text_output = result.get("result", "I couldn't find an answer in the database.")
        print(f"[DEBUG] Graph Tool output: {text_output}")
        return text_output
    except Exception as e:
        return f"Error running graph query: {e}"

graph_tool = StructuredTool.from_function(
    func=run_graph_tool,
    name="mtg_database_qa",
    description="Use this tool for questions about Magic: The Gathering cards, prices, artists, etc.",
    args_schema=GraphToolInput
)

# -- Tool 2: General Chat --
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer directly."),
    ("human", "{question}")
])
chat_tool = Tool(
    name="general_knowledge_chat",
    func=(chat_prompt | llm | (lambda x: x.content)).invoke,
    description="Use this for general questions NOT about Magic: The Gathering (e.g., 'who is the king of pop?')."
)

# -- Tool 3: Price Predictor (NEW) --

class PredictPriceInput(BaseModel):
    text: str = Field(description="The rules text of the card.")
    mana_cost: str = Field(description="The mana cost (e.g., '{2}{U}').")
    rarity: str = Field(description="The rarity (common, uncommon, rare, mythic).")
    is_foil: bool = Field(default=False, description="Is the card foil?")
    is_serialized: bool = Field(default=False, description="Is the card serialized?")
    is_showcase: bool = Field(default=False, description="Is the card a showcase variant?")
    
def predict_card_price(text: str, mana_cost: str, rarity: str, is_foil: bool = False, is_serialized: bool = False, is_showcase: bool = False):
    """
    Predicts the price of a card based on its features using the trained XGBoost model.
    """
    if not ML_AVAILABLE:
        return "Prediction model is not available."
    
    print(f"\n[DEBUG] Prediction Tool called: {text[:20]}... | {rarity} | Foil: {is_foil}")

    try:
        # 1. Feature Engineering (Replicate train_model.py logic)
        
        # Embeddings
        vector = embedding_model.encode([text])[0]
        
        # Create a single-row DataFrame with the exact columns the model expects
        # Note: XGBoost is sensitive to column order. We construct a dict first.
        features = {}
        
        # Graph features (We simulate 'average' graph scores for a new card since it's not in the graph yet)
        features['pagerank'] = 1.0
        features['degree'] = 5.0
        features['betweenness'] = 100.0
        
        features['text_length'] = len(text)
        
        # Embeddings (emb_0 to emb_383)
        for i, val in enumerate(vector):
            features[f'emb_{i}'] = val
            
        # Booleans
        features['is_foil'] = int(is_foil)
        features['is_etched'] = 0
        features['is_showcase'] = int(is_showcase)
        features['is_borderless'] = 0
        features['is_extended'] = 0
        features['is_retro'] = 0
        
        # Whale Tags
        features['is_serialized'] = int(is_serialized)
        features['is_neon'] = 0
        features['is_compleat'] = 0
        features['is_halo'] = 0
        features['is_oil_slick'] = 0
        features['is_textured'] = 0
        features['is_raised'] = 0
        features['is_galaxy'] = 0
        features['is_surge'] = 0
        
        # Variant Tags
        features['is_boosterfun'] = 0
        features['is_ub'] = 0
        features['is_poster'] = 0
        features['is_scroll'] = 0
        features['is_concept'] = 0

        # Types (Default to 0 for simplicity in this demo tool)
        features['is_creature'] = 0
        features['is_instant'] = 0
        features['is_sorcery'] = 0
        features['is_planeswalker'] = 0
        features['is_legendary'] = 0
        features['is_artifact'] = 0
        features['is_battle'] = 0

        # Rarity (One-Hot)
        features['rarity_mythic'] = 1 if rarity.lower() == 'mythic' else 0
        features['rarity_rare'] = 1 if rarity.lower() == 'rare' else 0
        features['rarity_uncommon'] = 1 if rarity.lower() == 'uncommon' else 0
        
        # Mana Cost
        features['mana_cost_len'] = len(mana_cost)

        # Create DataFrame
        df = pd.DataFrame([features])
        
        # Align columns with model (XGBoost requires this)
        # We get the feature names from the loaded model
        booster = price_model.get_booster()
        model_feature_names = booster.feature_names
        
        # Ensure our DF has all columns in right order, filling missing with 0
        df_aligned = pd.DataFrame(0, index=np.arange(1), columns=model_feature_names)
        for col in df.columns:
            if col in df_aligned.columns:
                df_aligned[col] = df[col]
                
        # Predict (returns log price)
        pred_log = price_model.predict(df_aligned)[0]
        
        # --- FIX: Safety Cap (e^12 is ~$162,000) ---
        if pred_log > 12:
            result_msg = "The estimated value is over $150,000! (It broke the model)."
        else:
            pred_price = np.expm1(pred_log) # Convert log -> real dollars
            result_msg = f"The estimated value for this card is ${pred_price:.2f}."
            
        print(f"[DEBUG] Prediction result: {result_msg}")
        return result_msg

    except Exception as e:
        return f"Error calculating prediction: {e}"

prediction_tool = StructuredTool.from_function(
    func=predict_card_price,
    name="predict_new_card_price",
    description="Use this tool ONLY when the user asks to predict/estimate the price of a NEW or HYPOTHETICAL card. Do not use it for existing cards.",
    args_schema=PredictPriceInput
)


# --- 5. Create the LangGraph Agent ---

tools = [graph_tool, chat_tool, prediction_tool] # <--- Added new tool

agent_graph = create_react_agent(llm, tools)

# --- API Models ---

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    cypher_query: str | None = Field(default=None)
    db_result: str | None = Field(default=None)
    final_answer: str

# --- API Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    print(f"Received query: {request.question}")
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "question": request.question,
        "cypher_query": None,
        "db_result": None,
        "final_answer": None,
        "success": False
    }

    try:
        # --- Run the LangGraph Agent ---
        inputs = {"messages": [("user", request.question)]}
        result = agent_graph.invoke(inputs)
        
        # The final answer is the content of the last message
        final_answer = result["messages"][-1].content
        
        # Extract Graph Data (logging only)
        cypher_query = "See logs"
        db_result = "See logs"

        log_data.update({
            "final_answer": final_answer,
            "success": True
        })
        
        response = QueryResponse(
            question=request.question,
            cypher_query=cypher_query,
            db_result=db_result,
            final_answer=final_answer
        )

    except Exception as e:
        print(f"Error processing query: {e}")
        log_data.update({"final_answer": str(e), "success": False})
        response = QueryResponse(
            question=request.question,
            final_answer="An error occurred while processing your request."
        )

    threading.Thread(target=log_episode, args=(log_data,)).start()
    return response