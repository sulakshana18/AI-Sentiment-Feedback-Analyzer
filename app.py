import csv
import io
import os

from flask import Flask, render_template_string, request
from dotenv import load_dotenv

from analyzer import analyze_feedback, analyze_many

load_dotenv()

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sentiment Feedback Analyzer</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; }
    body { margin: 0; background: #f4f7fb; color: #172033; }
    main { max-width: 900px; margin: 0 auto; padding: 48px 20px; }
    h1 { margin-bottom: 8px; }
    .lead { color: #566176; margin-top: 0; }
    section { background: white; padding: 24px; margin-top: 20px; border: 1px solid #dce3ee; border-radius: 12px; }
    textarea { width: 100%; box-sizing: border-box; min-height: 130px; padding: 12px; border: 1px solid #b9c4d6; border-radius: 8px; font: inherit; }
    input[type=file] { margin: 12px 0; }
    button { border: 0; border-radius: 8px; padding: 11px 16px; background: #2457d6; color: white; font-weight: 700; cursor: pointer; }
    button:hover { background: #1b45ad; }
    .result { margin-top: 18px; padding: 16px; border-left: 4px solid #2457d6; background: #f5f8ff; }
    .error { color: #a22626; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { text-align: left; padding: 10px; border-bottom: 1px solid #e3e8f0; }
    .muted { color: #69758a; font-size: .9rem; }
  </style>
</head>
<body>
<main>
  <h1>Sentiment Feedback Analyzer</h1>
  <p class="lead">Classify customer feedback and identify the themes behind it.</p>
  <section>
    <h2>Analyze one message</h2>
    <form method="post">
      <textarea name="feedback" placeholder="Paste customer feedback here...">{{ feedback }}</textarea>
      <p><button type="submit">Analyze feedback</button></p>
    </form>
    {% if result %}
      <div class="result">
        <strong>{{ result.sentiment|title }}</strong> · {{ result.confidence }} confidence
        <p>{{ result.summary }}</p>
        <p class="muted">Themes: {{ result.themes|join(', ') if result.themes else 'None detected' }}</p>
      </div>
    {% endif %}
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
  </section>
  <section>
    <h2>Analyze a CSV</h2>
    <p class="muted">The file must contain a <code>feedback</code> column.</p>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file" accept=".csv" required>
      <button type="submit">Analyze CSV</button>
    </form>
    {% if rows %}
      <table><tr><th>Feedback</th><th>Sentiment</th><th>Themes</th></tr>
      {% for row in rows %}<tr><td>{{ row.feedback }}</td><td>{{ row.sentiment|title }}</td><td>{{ row.themes|join(', ') }}</td></tr>{% endfor %}
      </table>
    {% endif %}
  </section>
</main>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    rows = None
    error = None
    feedback = ""

    if request.method == "POST" and request.form.get("feedback") is not None:
        feedback = request.form["feedback"].strip()
        if feedback:
            result = analyze_feedback(feedback)
        else:
            error = "Enter some feedback to analyze."

    uploaded = request.files.get("file")
    if request.method == "POST" and uploaded and uploaded.filename:
        try:
            records = list(csv.DictReader(io.StringIO(uploaded.read().decode("utf-8-sig"))))
            if not records or "feedback" not in records[0]:
                raise ValueError("CSV must include a feedback column.")
            rows = analyze_many([record["feedback"] for record in records if record.get("feedback", "").strip()])
        except (UnicodeDecodeError, ValueError) as exc:
            error = str(exc)

    return render_template_string(PAGE, result=result, rows=rows, error=error, feedback=feedback)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)