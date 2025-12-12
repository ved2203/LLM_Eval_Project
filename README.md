# LLM_Eval_Project

1. Local Setup Instructions

Prerequisites
* Python 3.10+
* pip installed

Install dependencies

```bash
pip install openai python-dotenv
```
OpenAI API Key
Create a `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```
Run the evaluation script
```bash
python llm_eval_pipeline.py
```

Output:

```json
{
  "user_question": "Who is the CEO of OpenAI?",
  "llm_response": "The CEO of OpenAI is Sam Altman.",
  "relevance_score": 0.55,
  "completeness_score": 0.66,
  "hallucination_detected": false,
  "latency_ms": 134.7,
  "cost_estimate_usd": 0.00007
}
```


2. Architecture of the Evaluation Pipeline

```
┌────────────────────────┐
│  conversation.json      │
└──────────┬─────────────┘
           │
┌────────────────────────┐
│ context_vector.json     │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────────────────────────┐
│         LLM Evaluation Pipeline            │
│                                            │
│ 1. Load conversation + context             │
│ 2. Generate LLM response                   │
│ 3. Measure Latency                         │
│ 4. Estimate Cost                           │
│ 5. Evaluate using:                         │
│    - Relevance (keyword/semantic match)    │
│    - Completeness (coverage check)         │
│    - Hallucination (context comparison)    │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────┐
│   evaluation_report.json│
└────────────────────────┘
```

3. Why This Design?

->Simple + Extendable

The solution uses plain Python with very lightweight logic.
This keeps the project:
* Easy to understand
* Easy to test
* Easy to extend with embeddings, RAG, or better scoring later

->Separation of Inputs

Using two input JSON files matches how real LLM systems work:
*Conversation JSON → the actual chat
*Context JSON → retrieved from vector DB (RAG)

->Deterministic & Transparent Evaluation
Instead of vague scoring:
* Relevance → keyword / semantic match
* Completeness → coverage ratio
* Hallucination → compare LLM answer vs. context

Evaluation is predictable (important for ML Ops).

->Can scale to any LLM provider
The code uses a standard `LLMClient` wrapper.
Later, you can switch easily to:
* Groq
* Gemini
* Llama.cpp
* AWS Bedrock
* Azure OpenAI

---

4. Scalability — How Latency & Costs Stay Low
This solution follows 4 core strategies for scale (millions of daily evaluations):

A. Minimal API Calls → Latency ↓ Cost ↓
The pipeline uses:
* **One LLM call per evaluation**
* No unnecessary reranking
* No chain-of-thought decoding
* No extra embedding calls during scoring
  (scoring is done locally)

This keeps API usage extremely cheap and fast.

B. Lightweight Scoring Logic (Runs Locally)
Relevance, completeness, hallucination checks use:
* Keyword overlap OR
* Optional cosine similarity (fast, CPU-only)

This ensures:
* No GPU
* No external API calls
* No additional cloud cost

Just pure Python.

---
C. Can run fully parallel → Horizontal Scaling
This pipeline can be easily deployed with:
* Celery
* Kafka
* Redis queues
* Kubernetes autoscaling
Because each evaluation is **stateless**, millions of evaluations can run in parallel.
---

D. Caching Support (Optional)
If you add caching:
* identical user questions OR
* similar context vectors
  produce the same evaluation results

This further reduces cost by 30–50% at scale.

---
