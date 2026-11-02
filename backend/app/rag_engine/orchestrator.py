"""GenAI Orchestrator for generating grounded farmer advice."""

import json
from app.schemas import Diagnosis, ActionWindow, Advice, SafetyTier
from app.rag_engine.llm_client import get_llm_client
from app.rag_engine.knowledge_cards import hybrid_retrieve

def generate_farmer_advice(
    diagnosis: Diagnosis, 
    action_window: ActionWindow, 
    farmer_language: str = "Urdu"
) -> Advice:
    """
    Generates structured, grounded advice based on deterministic diagnosis and hydrology.
    """
    # 1. Retrieve grounded context
    top_condition = diagnosis.prediction_set[0].condition_id if diagnosis.prediction_set else "unknown"
    context_docs = hybrid_retrieve(top_condition, diagnosis.symptoms_seen, top_k=2)
    context_text = "\n\n".join([doc["text"] for doc in context_docs])

    # 2. Build the strict system prompt
    system_prompt = f"""
    You are AgroPulse Copilot, an expert agronomist AI. 
    You MUST generate advice in {farmer_language}.
    
    STRICT SAFETY RULES (DO NOT OVERRIDE):
    - Current Safety Tier: {diagnosis.tier.value}
    - Safe to Spray Today: {action_window.can_spray_today}
    - Wind Warning: {action_window.wind_warning}
    
    If the Safety Tier is RED, you MUST advise the farmer to contact a human expert immediately and DO NOT recommend any chemical treatments.
    If Safe to Spray is False, you MUST advise the farmer to wait for better weather.
    
    Use ONLY this retrieved context for chemical recommendations:
    {context_text}
    
    Output MUST be a valid JSON object matching this exact schema:
    {{
        "summary": "Short plain-language summary of the situation.",
        "confidence_statement": "Explanation of confidence level based on tier.",
        "do_today": [{{"text": "Action to take", "source_ids": ["card_001"]}}],
        "monitor": [{{"text": "Symptom to watch", "source_ids": []}}],
        "escalate_if": [{{"text": "Condition for human escalation", "source_ids": []}}],
        "chemical_options": ["Propiconazole 0.1%"],
        "action_window": {{
            "can_spray_today": {action_window.can_spray_today},
            "irrigation_due_hours": {action_window.irrigation_due_hours},
            "wind_warning": {action_window.wind_warning}
        }}
    }}
    """

    user_prompt = f"Diagnosis: {top_condition}. Symptoms: {', '.join(diagnosis.symptoms_seen)}. Generate the JSON advice."

    # 3. Call the LLM
    client = get_llm_client(provider="groq")
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        raw_json = response.choices[0].message.content
        parsed_data = json.loads(raw_json)
        
        # 4. Pydantic strictly validates the LLM's output (including the chemical guardrail)
        advice = Advice.model_validate(parsed_data)
        
        # 5. Hard override: Force the action window to match our deterministic calculation
        advice.action_window = action_window
        
        return advice

    except Exception as e:
        # Fallback for AMBER/RED tiers if LLM fails or is rate-limited
        if diagnosis.tier == SafetyTier.RED or diagnosis.tier == SafetyTier.RETAKE:
            return Advice(
                summary="⚠️ High Risk or Unclear Image Detected.",
                confidence_statement="Our system requires human verification for this condition.",
                do_today=[],
                monitor=[],
                escalate_if=[{"text": "Please take a clear photo in daylight and contact your local agricultural extension officer immediately.", "source_ids": []}],
                chemical_options=[],
                action_window=action_window
            )
        raise RuntimeError(f"Failed to generate advice: {e}")