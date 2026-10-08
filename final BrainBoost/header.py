import streamlit as st


def show_brand_header():
    st.markdown(
        """
        <div class="brand-header">
            BrainBoost Test
        </div>

        <div class="tagline">
            Challenge Your Mind • Improve Your Knowledge • Track Your Progress
        </div>
        """,
        unsafe_allow_html=True
    )