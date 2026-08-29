from __future__ import annotations
import time
import numpy as np
import streamlit as st
from ai.question_generator import generate_questions
from ai.answer_analyzer import analyze_answer
from ai.feedback_generator import generate_feedback
from audio.recorder import load_wav
from audio.voice_analysis import analyze_audio
from config.settings import APP_NAME, DOMAINS
from dashboard.charts import gauge, radar, question_scores, emotion_chart
from interview.scoring import calculate_scores
from interview.session import init_session, reset_interview
from utils.report_generator import make_pdf
from vision.camera import camera_available
from vision.emotion_analyzer import analyze_frame

st.set_page_config(page_title=APP_NAME, page_icon="◈", layout="wide", initial_sidebar_state="expanded")
st.markdown('''<style>
 .stApp {background: radial-gradient(circle at 20% 0%, #122550 0%, #07101f 42%, #050914 100%); color:#eaf2ff}
 [data-testid="stSidebar"] {background:#091426}.block-container{max-width:1200px;padding-top:2.1rem}
 .hero{padding:3rem;border:1px solid rgba(103,232,249,.25);border-radius:24px;background:linear-gradient(135deg,rgba(28,52,94,.8),rgba(9,17,33,.65));}
 .eyebrow{color:#67e8f9;letter-spacing:.13em;text-transform:uppercase;font-weight:700}.metric-card{padding:1rem;border-radius:16px;background:rgba(15,32,59,.7);border:1px solid rgba(148,163,184,.17)}
 .stButton>button{border-radius:10px;border:0;background:linear-gradient(90deg,#0891b2,#4f46e5);color:white;font-weight:700;padding:.55rem 1rem}
 </style>''', unsafe_allow_html=True)
init_session()

def go(page: str): st.session_state.page = page

with st.sidebar:
    st.markdown("## ◈ AI Interview\n### Analyzer")
    for label in ["Home", "Setup Interview", "Interview", "Results", "Reports", "About"]:
        if st.button(label, use_container_width=True): go(label)
    st.divider(); st.caption("SYSTEM STATUS")
    st.caption("● Groq AI: configured" if __import__('config.settings', fromlist=['GROQ_API_KEY']).GROQ_API_KEY else "○ Groq AI: fallback mode")
    st.caption("● Camera: detected" if camera_available() else "○ Camera: not detected / browser fallback")
    st.caption("○ Microphone: optional local capture")
    demo = st.toggle("Demo Mode", value=st.session_state.demo_mode)
    st.session_state.demo_mode = demo

page = st.session_state.page
if st.session_state.demo_mode:
    st.warning("DEMO MODE — sample-compatible data is used when a device or AI service is unavailable.")

if page == "Home":
    st.markdown('<div class="hero"><p class="eyebrow">Multimodal mock interview platform</p><h1>Practice. Analyze. Improve.</h1><p style="font-size:1.15rem">Domain-specific AI interviews with transparent answer, voice-feature, and facial-expression indicators.</p></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3); a.metric("AI questions", "Groq + fallback"); b.metric("Signals", "Answer · voice · expression"); c.metric("Output", "Dashboard + PDF")
    st.write("")
    if st.button("Start Interview →", type="primary"): go("Setup Interview"); st.rerun()
    with st.expander("How it works"):
        st.write("Configure an interview, review AI-generated questions, type answers (or use optional local audio capture), then inspect explainable scores and download a report. Signal indicators are supportive—not psychological diagnoses.")

elif page == "Setup Interview":
    st.title("Configure your interview")
    with st.form("setup"):
        left,right=st.columns(2)
        name=left.text_input("Candidate name", value=st.session_state.candidate.get("name", ""))
        domain=left.selectbox("Interview domain", DOMAINS, index=0)
        custom=left.text_input("Custom domain", disabled=domain != "Other")
        exp=right.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"])
        difficulty=right.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"], index=3)
        interview_type=right.selectbox("Interview type", ["Technical", "HR", "Behavioral", "Technical + HR"])
        count=st.select_slider("Number of questions", options=[5,10,15], value=5)
        submitted=st.form_submit_button("Generate AI Interview", type="primary")
    if submitted:
        selected=custom.strip() if domain == "Other" and custom.strip() else domain
        with st.spinner("Preparing your tailored question set..."):
            qs, fallback, notice=generate_questions(selected, exp, count, difficulty, interview_type)
        st.session_state.candidate={"name": name or "Candidate", "domain":selected, "experience":exp, "difficulty":difficulty, "interview_type":interview_type}
        st.session_state.questions=qs; st.session_state.answers=[]; st.session_state.current_question=0; st.session_state.final_scores=None
        st.info(notice) if fallback else st.success(notice)
        st.subheader("Question preview")
        for q in qs: st.write(f"**{q.id}.** {q.question}  ·  `{q.category}` / `{q.difficulty}`")
        if st.button("Start interview →", type="primary"): go("Interview"); st.rerun()

elif page == "Interview":
    if not st.session_state.questions:
        st.info("Set up an interview first.")
        if st.button("Go to setup"): go("Setup Interview"); st.rerun()
    else:
        idx=st.session_state.current_question; qs=st.session_state.questions
        if idx >= len(qs): go("Results"); st.rerun()
        q=qs[idx]
        st.progress(idx / len(qs), text=f"Question {idx+1} of {len(qs)}")
        st.markdown(f"## {q.question}")
        st.caption(f"{q.category} · {q.difficulty}  |  Start a response timer when ready.")
        if f"started_{idx}" not in st.session_state: st.session_state[f"started_{idx}"]=None
        if st.button("Start timer"):
            st.session_state[f"started_{idx}"]=time.time(); st.rerun()
        if st.session_state[f"started_{idx}"]:
            st.info("Response timer is active. Submit when you are ready.")
        answer=st.text_area("Your answer (typed-answer fallback is always available)", key=f"answer_{idx}", height=180, placeholder="Explain your answer clearly; include an example where useful.")
        uploaded=st.file_uploader("Optional audio sample (.wav)", type=["wav"], key=f"audio_{idx}", help="Audio feature analysis is optional. Browser/server audio capture varies by deployment.")
        face_image=st.file_uploader("Optional representative camera image (.jpg/.png)", type=["jpg", "jpeg", "png"], key=f"face_{idx}", help="If DeepFace is installed, one supplied image can be sampled for an expression observation.")
        if st.button("Analyze answer & continue", type="primary"):
            if not answer.strip(): st.error("Please provide an answer before continuing.")
            else:
                with st.spinner("Analyzing your response..."):
                    feedback=analyze_answer(q.question, answer)
                    # Browser-compatible uploads are preferred over assuming server hardware access.
                    if uploaded:
                        try:
                            signal, rate = load_wav(uploaded)
                            voice = analyze_audio(signal, rate)
                        except RuntimeError as exc:
                            st.warning(str(exc)); voice = analyze_audio(np.array([]))
                    else:
                        signal=np.sin(np.linspace(0, 150, 16000*8))*0.05 if st.session_state.demo_mode else np.array([])
                        voice=analyze_audio(signal)
                    if face_image:
                        try:
                            import cv2
                            data=np.frombuffer(face_image.getvalue(), np.uint8)
                            frame=cv2.imdecode(data, cv2.IMREAD_COLOR)
                            emotion=analyze_frame(frame)
                        except Exception:
                            emotion={"dominant_emotion":"Not available", "distribution":{}, "available":False}
                    else:
                        emotion={"dominant_emotion":"Neutral (demo observation)" if st.session_state.demo_mode else "Not available", "distribution":{"neutral":65,"happy":20,"fear":15} if st.session_state.demo_mode else {}, "available":st.session_state.demo_mode}
                    result={"question":q.question,"answer":answer,"answer_score":float(feedback.get("overall",0))*10,"communication_score":float(feedback.get("clarity",0))*10,"voice":voice,"emotion":emotion,"feedback":feedback}
                    st.session_state.answers.append(result); st.session_state.current_question += 1
                st.rerun()

elif page in ("Results", "Reports"):
    if not st.session_state.answers:
        st.info("Complete at least one interview answer to see results.")
    else:
        scores=calculate_scores(st.session_state.answers); st.session_state.final_scores=scores
        summary={**scores,"domain":st.session_state.candidate.get("domain","")}
        if not st.session_state.feedback: st.session_state.feedback=generate_feedback(summary)
        if page == "Results":
            st.title("Performance dashboard")
            cols=st.columns(5)
            for col,(label,key) in zip(cols,[("Overall","overall"),("Technical","technical"),("Communication","communication"),("Voice","voice"),("Behavior","behavior")]): col.metric(label,f"{scores[key]:.0f}/100")
            left,right=st.columns(2); left.plotly_chart(gauge(scores["overall"],"Overall performance"),use_container_width=True); right.plotly_chart(radar(scores),use_container_width=True)
            left,right=st.columns(2); left.plotly_chart(question_scores(st.session_state.answers),use_container_width=True); right.plotly_chart(emotion_chart(st.session_state.answers),use_container_width=True)
            st.subheader("Personalized feedback"); st.write(st.session_state.feedback["summary"])
            a,b=st.columns(2); a.write("**Strengths**"); [a.write("• "+x) for x in st.session_state.feedback.get("strengths",[])]; b.write("**Practice next**"); [b.write("• "+x) for x in st.session_state.feedback.get("improvements",[])]
            st.caption("Voice and facial-expression values are non-diagnostic indicators; they do not establish confidence, emotion, personality, or job suitability.")
            st.subheader("Question-wise analysis")
            for i,r in enumerate(st.session_state.answers,1):
                with st.expander(f"Q{i}: {r['question'][:80]}"):
                    st.write(f"Answer score: **{r['answer_score']:.0f}/100** · Voice indicator: **{r['voice']['voice_score']:.0f}/100** · Detected facial expression: **{r['emotion']['dominant_emotion']}**")
                    for item in r['feedback'].get('improvements',[]): st.write("• "+item)
        else:
            st.title("Download your report")
            try:
                pdf=make_pdf(st.session_state.candidate,scores,st.session_state.answers,st.session_state.feedback)
                st.download_button("Download PDF report",data=pdf,file_name="ai_interview_report.pdf",mime="application/pdf",type="primary")
                st.caption("The report is generated locally in memory and does not reveal your API key.")
            except RuntimeError as exc:
                st.warning(str(exc))

elif page == "About":
    st.title("About AI Interview Analyzer")
    st.write("An AI-assisted mock-interview performance evaluation platform built with Python, Streamlit, Groq, DeepFace/OpenCV (optional), NumPy, and Plotly.")
    st.markdown("**AI components:** Groq LLM for questions and feedback; optional DeepFace facial-expression observation; audio signal processing for measurable voice features.")
    st.info("This tool supports practice and reflection. It does not diagnose emotion, confidence, personality, or employability.")
    if st.button("Reset interview"): reset_interview(); st.rerun()
