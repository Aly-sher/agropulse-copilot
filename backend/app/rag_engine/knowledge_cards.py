"""Mock Knowledge Base simulating Hybrid RAG retrieval for MVP."""

from typing import List, Dict, Any

# Simulated agronomic knowledge cards with image references
KNOWLEDGE_CARDS = [
    {
        "id": "card_001",
        "condition": "wheat_yellow_rust",
        "text": "Wheat yellow rust (stripe rust) thrives in cool, moist conditions (10-15°C, high humidity). "
                "Control: Apply fungicides containing Propiconazole or Tebuconazole at 0.1% concentration. "
                "Pre-Harvest Interval (PHI): 21 days. Wear gloves and a mask (PPE).",
        "keywords": ["rust", "yellow", "pustules", "fungicide", "propiconazole", "tebuconazole"],
        # Image URLs for the Frontend UI to display to the farmer
        "disease_image_url": "https://example.com/images/wheat_yellow_rust.jpg",
        "chemical_image_url": "https://example.com/images/propiconazole_bottle.jpg"
    },
    {
        "id": "card_002",
        "condition": "nitrogen_deficiency",
        "text": "Nitrogen deficiency causes yellowing of older leaves (chlorosis). "
                "Control: Apply Urea (46% N) at 50 kg/ha or Diammonium Phosphate (DAP) if phosphorus is also low. "
                "Irrigate immediately after application.",
        "keywords": ["nitrogen", "yellowing", "urea", "dap", "chlorosis"],
        "disease_image_url": "https://example.com/images/nitrogen_deficiency.jpg",
        "chemical_image_url": "https://example.com/images/urea_bag.jpg"
    }
]

def hybrid_retrieve(query_condition: str, symptoms: List[str], top_k: int = 2) -> List[Dict[str, Any]]:
    """
    Simulates Hybrid Search (Dense Semantic + Sparse Keyword BM25).
    """
    query_lower = query_condition.lower()
    symptom_lower = [s.lower() for s in symptoms]
    
    scored_cards = []
    for card in KNOWLEDGE_CARDS:
        score = 0.0
        # Sparse (Keyword) Match Scoring
        if query_lower in card["condition"] or query_lower in card["text"].lower():
            score += 2.0
        for symptom in symptom_lower:
            if any(symptom in kw for kw in card["keywords"]):
                score += 1.5
                
        # Dense (Semantic) Mock Scoring
        if card["condition"] == query_lower:
            score += 3.0
            
        scored_cards.append((score, card))
        
    scored_cards.sort(key=lambda x: x[0], reverse=True)
    
    return [card for score, card in scored_cards[:top_k]]