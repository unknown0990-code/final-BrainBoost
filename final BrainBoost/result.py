import streamlit as st
import pandas as pd
from database import get_user_results
import header

def show_results_page():
    header.show_brand_header()
    st.title("My Results")
    
    results = get_user_results(st.session_state.username)
    
    if not results:
        st.info("You haven't taken any tests yet. Go to the 'Test' section to start!")
        return
        
    # Calculate Summary Statistics
    total_tests = len(results)
    best_score_pct = max([r[3] for r in results])
    avg_score_pct = sum([r[3] for r in results]) / total_tests
    total_correct = sum([r[1] for r in results])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Tests Taken</div><div class="metric-value">{total_tests}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Best Score</div><div class="metric-value">{best_score_pct:.1f}%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Score</div><div class="metric-value">{avg_score_pct:.1f}%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Correct</div><div class="metric-value">{total_correct}</div></div>', unsafe_allow_html=True)
        
    # ========================================================
    # AVERAGE SCORE BY SUBJECT
    # ========================================================

    df_chart = pd.DataFrame(
        results,
        columns=["Category", "Score", "Total", "Percentage", "Date"]
    )

    subject_means = (
        df_chart.groupby("Category")["Percentage"]
        .mean()
    )

    st.write("---")
    st.markdown("### 📈 Average Score by Subject")
    st.bar_chart(
        subject_means,
        color="#4A90E2"
    )

    st.write("---")
    st.subheader("Test History")
    
    # Convert to DataFrame for nice table rendering
    df = pd.DataFrame(results, columns=["Category", "Score", "Total", "Percentage (%)", "Date"])
    # Format percentage
    df["Percentage (%)"] = df["Percentage (%)"].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(df, use_container_width=True, hide_index=True)