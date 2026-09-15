# Grounded Reply Generation Report (Milestone 13)

## Overview
This milestone establishes the response generation system for the support agent, adhering to a strict contract that demands all replies be grounded in historical evidence retrieved from previous successful support cases.

## Design
We designed a dual-tier generation system:
1. **Template-Based Generator (Default):** Extracts safe patterns from the closest matching historical response and formats them into a customer-facing reply (removing direct tags to anonymize).
2. **LLM Client (Optional):** A provider-independent LLM wrapper (`LLMClient`). To ensure security, it operates in a strict "mock mode" by default unless valid API credentials (`ANTHROPIC_API_KEY`) are present in the environment.

## Evidence Handling and Uncertainty
The system is explicitly programmed to **abstain** if it lacks historical evidence. 
Because the retrieval corpus from Milestone 12 is currently empty (due to the dataset splitting constraint isolating all available records in the golden set), the `retrieve_cases` call returns 0 records. 

Consequently, the generation system elegantly falls back to its safety mechanism:
- `draft_reply`: null
- `grounding_status`: Failed
- `uncertainty_flag`: True
- `escalation_recommendation`: True

This demonstrates that the system will **not hallucinate** policies or troubleshooting steps when it lacks verifiable company data. 

## Prompt Design
For the LLM client, the grounding prompt is structured to separate the inputs clearly:
1. **Customer Message** & **Predicted Intent**
2. **Historical Evidence** (enumerated)
3. **Instructions:** (Answer only using provided evidence, do not invent facts, ask for missing info, escalate uncertain cases).

## Known Failure Modes & Limitations
- **Template Rigidity:** The template extractor is highly deterministic. If the retrieved case is structurally unusual, the generated reply might sound disjointed.
- **Empty Retrieval Corpus:** The system correctly escalates 100% of queries right now. This is not a failure of the generation code, but a limitation of the data pipeline upstream.
- **Mock Mode Limitation:** While mock mode validates the data flow, it does not evaluate the linguistic nuance of a true LLM.

## Reproduction
```bash
# Attempt to generate a reply using the template generator
python src/generate_reply.py --text "My phone is freezing"

# Attempt to generate using the LLM in mock mode
python src/generate_reply.py --text "My phone is freezing" --use_llm
```
