import json
import time
import re
from typing import List, Dict

# ------------------------
# SIMPLE TEXT SIMILARITY
# ------------------------

def simple_similarity(a: str, b: str) -> float:
    """A very simple token-overlap similarity for beginners."""
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0
    return len(a_words & b_words) / len(a_words | b_words)


# ------------------------
# RELEVANCE & COMPLETENESS
# ------------------------

def evaluate_relevance(response: str, context_passages: List[str]) -> float:
    """Check how similar the answer is to any provided context."""
    sims = [simple_similarity(response, ctx) for ctx in context_passages]
    return max(sims) if sims else 0.0


def evaluate_completeness(response: str, user_question: str) -> float:
    """Check if the answer covers the same keywords as the question."""
    q_words = set(user_question.lower().split())
    r_words = set(response.lower().split())

    if not q_words:
        return 1.0

    coverage = len(q_words & r_words) / len(q_words)
    return coverage


# ------------------------
# HALLUCINATION CHECK
# ------------------------

def detect_hallucination(response: str, context_passages: List[str]) -> bool:
    """
    Very simple hallucination detector:
    - If the response has low similarity to all context → possible hallucination.
    """
    relevance = evaluate_relevance(response, context_passages)
    return relevance < 0.15  # threshold


# ------------------------
# LATENCY & COST
# ------------------------

def estimate_latency(start, end):
    return round((end - start) * 1000, 2)


def estimate_cost(text: str):
    """Fake cost estimate: count tokens and multiply."""
    tokens = text.split()
    return round(len(tokens) * 0.00001, 5)  # demo cost


# ------------------------
# MAIN EVALUATION PIPELINE
# ------------------------

def evaluate(conversation, contexts):
    user_question = conversation["messages"][-2]["content"]
    llm_response = conversation["messages"][-1]["content"]

    context_texts = [c["text"] for c in contexts]

    start = time.time()

    relevance = evaluate_relevance(llm_response, context_texts)
    completeness = evaluate_completeness(llm_response, user_question)
    hallucination = detect_hallucination(llm_response, context_texts)

    end = time.time()

    latency_ms = estimate_latency(start, end)
    cost = estimate_cost(llm_response)

    report = {
        "user_question": user_question,
        "llm_response": llm_response,
        "relevance_score": relevance,
        "completeness_score": completeness,
        "hallucination_detected": hallucination,
        "latency_ms": latency_ms,
        "cost_estimate_usd": cost
    }

    return report


# ------------------------
# CLI MAIN
# ------------------------

if __name__ == "__main__":
    convo = json.load(open("conversation.json"))
    ctx = json.load(open("context_vectors.json"))

    result = evaluate(convo, ctx)

    print("\n===== LLM EVALUATION REPORT =====")
    print(json.dumps(result, indent=4))
    print("=================================\n")
