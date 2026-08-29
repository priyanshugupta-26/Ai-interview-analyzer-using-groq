from __future__ import annotations
import time
import numpy as np
import streamlit as st
from ai.question_generator import generate_questions
from ai.answer_analyzer import analyze_answer
from ai.feedback_generator import generate_feedback
from audio.recorder import load_wav
from audio.voice_analysis import analyze_audio
from audio.speech_to_text import transcribe_audio, transcription_available
from config.settings import APP_NAME, DOMAINS
from dashboard.charts import gauge, radar, question_scores, emotion_chart
from interview.scoring import calculate_scores
from interview.session import init_session, reset_interview
from utils.report_generator import make_pdf
from vision.camera import camera_available
from vision.emotion_analyzer import analyze_frame
from vision.eye_contact import analyze_eye_visibility
from vision.live_capture import InterviewAudioProcessor, InterviewVideoProcessor

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
    st.caption("● Browser camera & microphone: permission required")
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
        submitted=st.form_submit_button("Start AI Interview", type="primary")
    if submitted:
        selected=custom.strip() if domain == "Other" and custom.strip() else domain
        with st.spinner("Preparing your tailored question set..."):
            qs, fallback, notice=generate_questions(selected, exp, count, difficulty, interview_type)
        st.session_state.candidate={"name": name or "Candidate", "domain":selected, "experience":exp, "difficulty":difficulty, "interview_type":interview_type}
        st.session_state.questions=qs; st.session_state.answers=[]; st.session_state.recorded_responses={}; st.session_state.mode_confirmed=False; st.session_state.current_question=0; st.session_state.final_scores=None
        st.info(notice) if fallback else st.success(notice)
        st.caption("Your questions are ready. They will be revealed one at a time during the interview.")
        go("Interview"); st.rerun()

elif page == "Interview":
    if not st.session_state.questions:
        st.info("Set up an interview first.")
        if st.button("Go to setup"): go("Setup Interview"); st.rerun()
    else:
        if not st.session_state.mode_confirmed:
            st.title("Choose interview mode")
            st.write("Select how you want to answer before the first question starts.")
            selected_mode = st.selectbox("Interview mode", ["Typing based interview", "Voice based interview", "Camera based interview"], key="mode_selection")
            mode_descriptions = {
                "Typing based interview": "Write each answer. Best for practicing answer structure and technical correctness.",
                "Voice based interview": "Record each answer with your microphone. The camera stays off.",
                "Camera based interview": "Use live camera and microphone for voice and visible-frame indicators.",
            }
            st.info(mode_descriptions[selected_mode])
            if st.button("Confirm mode and begin interview", type="primary"):
                st.session_state.candidate["mode"] = selected_mode
                st.session_state.mode_confirmed = True
                st.rerun()
            st.stop()
        idx=st.session_state.current_question; qs=st.session_state.questions
        if idx >= len(qs): go("Results"); st.rerun()
        q=qs[idx]
        st.progress(idx / len(qs), text=f"Question {idx+1} of {len(qs)}")
        st.markdown(f"## Question {idx + 1}: {q.question}")
        st.caption(f"{q.category} · {q.difficulty}  |  Answer this question, then the next question will appear automatically.")
        if f"started_{idx}" not in st.session_state: st.session_state[f"started_{idx}"]=None
        if st.button("Start timer"):
            st.session_state[f"started_{idx}"]=time.time(); st.rerun()
        if st.session_state[f"started_{idx}"]:
            st.info("Response timer is active. Submit when you are ready.")
        mode = st.session_state.candidate.get("mode", "Camera based interview")
        capture = None
        audio_clip = None
        if mode == "Typing based interview":
            st.info("Typing mode: write your answer, then continue to the next question.")
            answer=st.text_area("Your answer", key=f"answer_{idx}", height=180, placeholder="Explain clearly and include an example where useful.")
        elif mode == "Voice based interview":
            st.info("Voice mode: record your spoken answer using the browser microphone. Camera remains off.")
            audio_clip=st.audio_input("Record answer", key=f"voice_{idx}")
            answer=st.text_area("Transcript fallback", key=f"answer_{idx}", height=100, placeholder="Only needed when automatic transcription is unavailable.")
        else:
            try:
                from streamlit_webrtc import WebRtcMode, webrtc_streamer
                st.info("Camera mode: press START, allow camera and microphone access, answer naturally, then capture the response before stopping.")
                capture = webrtc_streamer(key=f"live_interview_{idx}", mode=WebRtcMode.SENDRECV, media_stream_constraints={"video": True, "audio": True}, video_processor_factory=InterviewVideoProcessor, audio_processor_factory=InterviewAudioProcessor, async_processing=True)
                if capture.state.playing:
                    st.success("Camera and microphone are recording this answer.")
                    if st.button("Capture this response", type="primary", key=f"capture_{idx}"):
                        audio, rate = capture.audio_processor.audio_for_analysis() if capture.audio_processor else (np.array([]), 16000)
                        frame = capture.video_processor.frame_for_analysis() if capture.video_processor else None
                        st.session_state.recorded_responses[idx] = {"audio": audio, "sample_rate": rate, "frame": frame}
                        st.success("Response snapshot saved. Now click Finish answer and show next question.")
                st.caption("Automatic transcription is used when Groq is configured. A short typed fallback is available if needed.")
            except ImportError:
                st.error("Live recording support is not installed. Run: pip install -r requirements.txt, then restart Streamlit.")
            answer=st.text_area("Transcript fallback", key=f"answer_{idx}", height=100, placeholder="Only needed if automatic transcription is unavailable.")
        if st.button("Finish answer and show next question →", type="primary"):
            with st.spinner("Analyzing your recorded response..."):
                recorded_audio = np.array([])
                audio_rate = 16000
                frame = None
                saved_capture = st.session_state.recorded_responses.get(idx, {})
                if mode == "Voice based interview" and audio_clip:
                    try:
                        recorded_audio, audio_rate = load_wav(audio_clip)
                    except RuntimeError:
                        pass
                elif saved_capture:
                    recorded_audio = saved_capture["audio"]
                    audio_rate = saved_capture["sample_rate"]
                    frame = saved_capture["frame"]
                elif capture:
                    if capture.audio_processor:
                        recorded_audio, audio_rate = capture.audio_processor.audio_for_analysis()
                    if capture.video_processor:
                        frame = capture.video_processor.frame_for_analysis()
                auto_transcript = transcribe_audio(recorded_audio, audio_rate) if transcription_available() else ""
                final_answer = auto_transcript or answer.strip()
                media_unavailable = False
                if not final_answer and st.session_state.demo_mode:
                    final_answer = "Demo answer: I would explain the concept clearly and support it with a practical example."
                if not final_answer and mode == "Typing based interview":
                    st.error("Please type an answer before continuing.")
                    st.stop()
                if not final_answer:
                    # A browser/device stream failure must never trap the candidate on a question.
                    # Preserve the interview flow and make unavailable metrics explicit in results.
                    final_answer = "Recording completed, but no transcript was available from this browser session."
                    media_unavailable = True
                    st.warning("The browser did not provide a usable media buffer, but your interview will continue. This answer will be marked as ‘media unavailable’ in the report rather than treated as a recorded transcript.")
                
                if final_answer:
                    feedback=analyze_answer(q.question, final_answer)
                    if not len(recorded_audio) and st.session_state.demo_mode:
                        recorded_audio=np.sin(np.linspace(0, 150, 16000*8))*0.05; audio_rate=16000
                    voice=analyze_audio(recorded_audio, audio_rate)
                    if media_unavailable:
                        feedback={"relevance": 5, "technical_accuracy": 5, "clarity": 5, "completeness": 5, "overall": 5, "strengths": ["Response recording was completed."], "improvements": ["Check browser microphone permission before the next attempt to enable transcript-based answer evaluation."]}
                        voice={"voice_score": 0.0, "duration_seconds": 0.0, "rms_energy": 0.0, "silence_ratio": 1.0, "level_consistency": 0.0, "status": "Media unavailable"}
                    if frame is not None:
                        try:
                            emotion=analyze_frame(frame)
                            eye_contact=analyze_eye_visibility(frame)
                        except Exception:
                            emotion={"dominant_emotion":"Not available", "distribution":{}, "available":False}
                            eye_contact={"eye_contact_score":0.0,"label":"Camera analysis unavailable"}
                    else:
                        emotion={"dominant_emotion":"Neutral (demo observation)" if st.session_state.demo_mode else "Not available", "distribution":{"neutral":65,"happy":20,"fear":15} if st.session_state.demo_mode else {}, "available":st.session_state.demo_mode}
                        eye_contact={"eye_contact_score":80.0,"label":"Both eyes visible (demo)"} if st.session_state.demo_mode else {"eye_contact_score":0.0,"label":"Media unavailable" if media_unavailable else "No camera capture"}
                    result={"question":q.question,"answer":final_answer,"answer_score":float(feedback.get("overall",0))*10,"communication_score":float(feedback.get("clarity",0))*10,"voice":voice,"emotion":emotion,"eye_contact":eye_contact,"feedback":feedback,"media_status":"Media unavailable" if media_unavailable else "Captured"}
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
            cols=st.columns(4)
            for col,(label,key) in zip(cols,[("Overall","overall"),("Answer correctness","technical"),("Communication","communication"),("Voice clarity","voice")]): col.metric(label,f"{scores[key]:.0f}/100")
            cols=st.columns(3)
            for col,(label,key) in zip(cols,[("Expression indicator","behavior"),("Eye visibility","eye_contact"),("Confidence-related indicator","confidence_indicator")]): col.metric(label,f"{scores[key]:.0f}/100")
            left,right=st.columns(2); left.plotly_chart(gauge(scores["overall"],"Overall performance"),use_container_width=True); right.plotly_chart(radar(scores),use_container_width=True)
            left,right=st.columns(2); left.plotly_chart(question_scores(st.session_state.answers),use_container_width=True); right.plotly_chart(emotion_chart(st.session_state.answers),use_container_width=True)
            st.subheader("Personalized feedback"); st.write(st.session_state.feedback["summary"])
            a,b=st.columns(2); a.write("**Strengths**"); [a.write("• "+x) for x in st.session_state.feedback.get("strengths",[])]; b.write("**Practice next**"); [b.write("• "+x) for x in st.session_state.feedback.get("improvements",[])]
            st.caption("The confidence-related value combines measured audio, expression, and eye-visibility indicators. It does not establish a person's actual confidence, emotion, personality, or job suitability.")
            st.subheader("Question-wise analysis")
            for i,r in enumerate(st.session_state.answers,1):
                with st.expander(f"Q{i}: {r['question'][:80]}"):
                    st.write(f"Answer correctness: **{r['answer_score']:.0f}/100** · Voice clarity: **{r['voice']['voice_score']:.0f}/100** · Eye visibility: **{r['eye_contact']['eye_contact_score']:.0f}/100** ({r['eye_contact']['label']}) · Detected facial expression: **{r['emotion']['dominant_emotion']}**")
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
