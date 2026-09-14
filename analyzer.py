import json
import os
import re

from prompts import SYSTEM_PROMPT


POSITIVE = {"amazing", "excellent", "good", "great", "happy", "helpful", "love", "perfect", "quick", "thank", "thanks", "wonderful"}
NEGATIVE = {"awful", "bad", "broken", " delay", "difficult", "hate", "poor", "slow", "terrible", "unhappy", "worst"}


def _local_analysis(text):
    words = re.findall(r"[a-z']+", text.lower())
    positive = sum(word in POSITIVE for word in words)
    negative = sum(word in NEGATIVE or word.strip() in NEGATIVE for word in words)
    if positive > negative:
        sentiment = "positive"
    elif negative > positive:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    confidence = "high" if positive + negative >= 2 else "medium" if positive + negative else "low"
    themes = []
    for name, terms in {"service": {"support", "staff", "service"}, "speed": {"fast", "quick", "slow", "delay"}, "quality": {"quality", "broken", "product"}, "price": {"cost", "price", "expensive"}}.items():
        if any(term in words for term in terms):
            themes.append(name)
    return {"sentiment": sentiment, "confidence": confidence, "summary": text, "themes": themes}


def analyze_feedback(text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _local_analysis(text)
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
        )
        result = json.loads(response.choices[0].message.content)
        return {"sentiment": result["sentiment"], "confidence": result["confidence"], "summary": result["summary"], "themes": result.get("themes", [])}
    except Exception:
        return _local_analysis(text)


def analyze_many(feedback_items):
    return [{"feedback": text, **analyze_feedback(text)} for text in feedback_items]