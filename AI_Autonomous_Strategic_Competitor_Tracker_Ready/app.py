from flask import Flask, render_template, request, jsonify, send_file
from agent import analyze_business, build_pdf_report

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}

    business_idea = (data.get("idea") or "").strip()
    state = (data.get("state") or "").strip()
    provider = (data.get("provider") or "auto").strip().lower()

    if not business_idea:
        return jsonify({
            "error": "Please enter a business idea or category."
        }), 400

    if not state:
        return jsonify({
            "error": "Please enter a state."
        }), 400

    if provider not in {"auto", "gemini", "groq", "offline"}:
        return jsonify({
            "error": "Choose Auto, Gemini, Groq, or Offline analysis."
        }), 400

    try:
        result = analyze_business(
            business_idea=business_idea,
            state=state,
            provider=provider
        )

        return jsonify(result)

    except Exception as exc:
        return jsonify({
            "error": f"Analysis failed: {exc}"
        }), 500


@app.route("/api/report", methods=["POST"])
def report():
    data = request.get_json(silent=True) or {}

    try:
        pdf_buffer = build_pdf_report(data)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="AI_Strategic_Competitor_Report.pdf",
            mimetype="application/pdf"
        )

    except Exception as exc:
        return jsonify({
            "error": f"PDF generation failed: {exc}"
        }), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
