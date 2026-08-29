from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px

PALETTE = ["#22d3ee", "#6366f1", "#a78bfa", "#34d399"]

def gauge(value: float, title: str):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, number={"suffix": "/100"}, title={"text": title}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#22d3ee"}, "bgcolor": "#14213d"}))
    fig.update_layout(height=220, margin=dict(l=15, r=15, t=55, b=10), paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    return fig

def radar(scores: dict):
    labels = ["Technical", "Communication", "Voice", "Behavior"]
    values = [scores["technical"], scores["communication"], scores["voice"], scores["behavior"]]
    fig = go.Figure(go.Scatterpolar(r=values + [values[0]], theta=labels + [labels[0]], fill="toself", line_color="#22d3ee"))
    fig.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 100]}}, height=350, margin=dict(l=35,r=35,t=25,b=25), paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    return fig

def question_scores(results: list[dict]):
    return px.line(x=[f"Q{i+1}" for i in range(len(results))], y=[r["answer_score"] for r in results], markers=True, labels={"x": "Question", "y": "Answer score"}, color_discrete_sequence=["#22d3ee"], template="plotly_dark")

def emotion_chart(results: list[dict]):
    counts = {}
    for item in results:
        e = item.get("emotion", {}).get("dominant_emotion", "Not available")
        counts[e] = counts.get(e, 0) + 1
    return px.bar(x=list(counts), y=list(counts.values()), labels={"x": "Detected facial expression", "y": "Answers"}, color_discrete_sequence=["#a78bfa"], template="plotly_dark")
