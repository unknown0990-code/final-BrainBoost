import streamlit as st
from database import get_questions_by_category, save_result
import header

def reset_test_state():
    st.session_state.test_started = False
    st.session_state.current_q_index = 0
    st.session_state.test_questions = []
    st.session_state.user_answers = {}
    st.session_state.test_submitted = False
    st.session_state.selected_category = None

def show_test_page():
    header.show_brand_header()
    
    if 'test_started' not in st.session_state:
        reset_test_state()
        
    if st.session_state.test_submitted:
        show_test_result()
        return

    if not st.session_state.test_started:
        st.subheader("Select a Subject to Begin")
        categories = ["Mathematics", "Science", "Computer", "Environment", "General Knowledge"]
        selected_cat = st.selectbox("Choose Category", categories)
        
        if st.button("Start Test", use_container_width=True):
            questions = get_questions_by_category(selected_cat)
            if not questions:
                st.error("No questions available for this category yet.")
            else:
                st.session_state.test_started = True
                st.session_state.test_questions = questions
                st.session_state.selected_category = selected_cat
                st.session_state.current_q_index = 0
                st.session_state.user_answers = {}
                st.rerun()
    else:
        run_test_interface()

def run_test_interface():
    questions = st.session_state.test_questions
    q_index = st.session_state.current_q_index
    q = questions[q_index]
    
    # Progress
    st.markdown(f"**Question {q_index + 1} of {len(questions)}**")
    st.progress((q_index) / len(questions))
    
    st.markdown(f"### {q[2]}")
    
    options = [q[3], q[4], q[5], q[6]]
    
    # Check if previously answered
    saved_answer = st.session_state.user_answers.get(q[0], None)
    idx = options.index(saved_answer) if saved_answer in options else 0
    
    selected_option = st.radio("Select your answer:", options, index=idx, key=f"q_{q[0]}")
    st.session_state.user_answers[q[0]] = selected_option
    
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if q_index > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_q_index -= 1
                st.rerun()
                
    with col3:
        if q_index < len(questions) - 1:
            if st.button("Next ➡️"):
                st.session_state.current_q_index += 1
                st.rerun()
        else:
            if st.button("✅ Submit Test", type="primary"):
                evaluate_test()

def evaluate_test():
    questions = st.session_state.test_questions
    answers = st.session_state.user_answers
    
    score = 0
    total = len(questions)
    
    for q in questions:
        q_id = q[0]
        correct_ans = q[7]
        user_ans = answers.get(q_id, None)
        if user_ans == correct_ans:
            score += 1
            
    percentage = (score / total) * 100
    
    # Save to DB
    save_result(st.session_state.username, st.session_state.selected_category, score, total, percentage)
    
    st.session_state.test_score = score
    st.session_state.test_total = total
    st.session_state.test_percentage = percentage
    st.session_state.test_submitted = True
    st.rerun()

def show_test_result():
    st.title("Test Results")
    
    score = st.session_state.test_score
    total = st.session_state.test_total
    percentage = st.session_state.test_percentage
    
    if percentage >= 80:
        st.markdown(f'<div class="result-success">Excellent Job!</div>', unsafe_allow_html=True)
        st.balloons()
    elif percentage >= 50:
        st.markdown(f'<div class="result-success" style="color:#F5A623;">Good Effort!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="result-fail">Keep Practicing!</div>', unsafe_allow_html=True)
        
    st.metric(label="Your Score", value=f"{score} / {total}")
    st.metric(label="Percentage", value=f"{percentage:.2f}%")
    
    if st.button("Take Another Test"):
        reset_test_state()
        st.rerun()