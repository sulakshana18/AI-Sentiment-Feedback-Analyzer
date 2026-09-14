SYSTEM_PROMPT = """Analyze the customer feedback and return only JSON with these fields:
sentiment: one of positive, negative, neutral
confidence: one of low, medium, high
summary: a concise summary
themes: an array of short topic labels
"""