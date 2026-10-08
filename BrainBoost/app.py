import streamlit as st
import pandas as pd
import os
import base64

import database
from auth import show_auth_page, logout, hash_password
from test import show_test_page
from result import show_results_page
import admin
import header


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BrainBoost Test",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# BACKGROUND VIDEO
# ============================================================

def set_video_background(video_file_path):

    if not os.path.exists(video_file_path):
        st.warning(
            f"Background video not found: {video_file_path}"
        )
        return

    try:
        with open(video_file_path, "rb") as video_file:
            video_bytes = video_file.read()

        encoded_video = base64.b64encode(video_bytes).decode()

        html_code = f"""
<style>
#background-video {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    object-fit: cover;
    z-index: -100;
    pointer-events: none;
}}

.video-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(14, 17, 23, 0.75);
    z-index: -99;
    pointer-events: none;
}}

.stApp {{
    background: transparent !important;
}}

[data-testid="stAppViewContainer"] {{
    background: transparent !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}
</style>

<video
    id="background-video"
    autoplay
    loop
    muted
    playsinline
>
    <source
        src="data:video/mp4;base64,{encoded_video}"
        type="video/mp4"
    >
</video>

<div class="video-overlay"></div>
"""

        # Use st.html — NOT st.markdown
        st.html(html_code)

    except Exception as e:
        st.warning(
            f"Unable to load background video: {e}"
        )

    # Check whether the video exists
    if not os.path.exists(video_file_path):
        st.warning(
            f"Background video not found: {video_file_path}"
        )
        return

    try:
        # Read video file
        with open(video_file_path, "rb") as video_file:
            video_bytes = video_file.read()

        # Convert video to Base64
        encoded_video = base64.b64encode(video_bytes).decode()

        # HTML + CSS for background video
        html_code = f"""
        <style>

        /* =========================================
           BACKGROUND VIDEO
           ========================================= */

        #background-video {{
            position: fixed;
            top: 0;
            left: 0;

            width: 100vw;
            height: 100vh;

            object-fit: cover;

            z-index: -2;
            pointer-events: none;
        }}


        /* =========================================
           DARK OVERLAY
           ========================================= */

        .video-overlay {{
            position: fixed;
            top: 0;
            left: 0;

            width: 100vw;
            height: 100vh;

            background: rgba(14, 17, 23, 0.75);

            z-index: -1;
            pointer-events: none;
        }}


        /* =========================================
           STREAMLIT BACKGROUND
           ========================================= */

        .stApp {{
            background: transparent !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background: transparent !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}

        </style>


        <!-- Background Video -->

        <video
            autoplay
            loop
            muted
            playsinline
            id="background-video"
        >

            <source
                src="data:video/mp4;base64,{encoded_video}"
                type="video/mp4"
            >

        </video>


        <!-- Dark Overlay -->

        <div class="video-overlay"></div>
        """



    except Exception as e:
        st.warning(
            f"Unable to load background video: {e}"
        )


# ============================================================
# LOAD CSS
# ============================================================

def load_css():

    css_path = os.path.join(
        os.path.dirname(__file__),
        "style.css"
    )

    if os.path.exists(css_path):

        try:
            with open(
                css_path,
                "r",
                encoding="utf-8"
            ) as f:

                css = f.read()

            st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True
            )

        except Exception as e:

            st.warning(
                f"Unable to load style.css: {e}"
            )


# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False


# ============================================================
# PROFILE PAGE
# ============================================================

def show_profile_page():
    header.show_brand_header()

    st.title("👤 My Profile")

    if st.session_state.is_admin:
        st.info("Profile settings are available for student accounts only.")
        return

    current_username = st.session_state.username
    user = database.get_user(current_username)

    if not user:
        st.error("Unable to load your profile. Please log in again.")
        return

    # ========================================================
    # PROFILE SUMMARY
    # ========================================================

    st.write(
        f"Welcome back, **{user[1]}**! 👋"
    )
    st.caption("Manage your BrainBoost account and view your learning progress.")

    st.write("")

    with st.container(border=True):
        st.markdown("### 👤 Personal Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Full Name**  \n{user[1]}")

        with col2:
            st.markdown(f"**Username**  \n@{user[2]}")

        st.markdown(f"**📱 Phone Number**  \n{user[3]}")

    # ========================================================
    # PERFORMANCE STATISTICS
    # ========================================================

    results = database.get_user_results(current_username)

    st.markdown("### 📊 Your Performance")

    if results:
        df = pd.DataFrame(
            results,
            columns=[
                "Category",
                "Score",
                "Total",
                "Percentage",
                "Date"
            ]
        )

        total_tests = len(df)
        best_score = df["Percentage"].max()
        avg_score = df["Percentage"].mean()
        subject_means = df.groupby("Category")["Percentage"].mean()
        best_subject = subject_means.idxmax()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            with st.container(border=True):
                st.metric("Tests Taken", total_tests)

        with col2:
            with st.container(border=True):
                st.metric("Best Score", f"{best_score:.1f}%")

        with col3:
            with st.container(border=True):
                st.metric("Average Score", f"{avg_score:.1f}%")

        with col4:
            with st.container(border=True):
                st.metric("Best Subject", best_subject)

        # Profile intentionally shows only summary statistics.
        # The subject-wise chart is displayed in My Results.
    else:
        st.info("You have not taken any tests yet. Start a test to see your performance here!")

    # ========================================================
    # EDIT PROFILE
    # ========================================================

    st.markdown("### ✏️ Edit Profile")

    with st.form("edit_profile_form"):
        new_name = st.text_input(
            "Full Name",
            value=user[1],
            max_chars=100
        )

        new_username = st.text_input(
            "Username",
            value=user[2],
            max_chars=50
        )

        new_phone = st.text_input(
            "Phone Number",
            value=user[3],
            max_chars=15
        )

        st.markdown("#### 🔐 Change Password")
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Leave blank to keep your current password",
            max_chars=128
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password"
        )

        save_profile = st.form_submit_button(
            "💾 Save Changes",
            use_container_width=True
        )

    if save_profile:
        new_name = new_name.strip()
        new_username = new_username.strip()
        new_phone = new_phone.strip()

        if not new_name or not new_username or not new_phone:
            st.warning("Full Name, Username, and Phone Number cannot be empty.")
            return

        if not new_phone.isdigit() or not 7 <= len(new_phone) <= 15:
            st.warning("Please enter a valid phone number using 7–15 digits.")
            return

        if new_password and new_password != confirm_password:
            st.error("New password and confirmation password do not match.")
            return

        if new_password and len(new_password) < 6:
            st.warning("New password must contain at least 6 characters.")
            return

        hashed_password = (
            hash_password(new_password)
            if new_password
            else None
        )

        success, message = database.update_user_profile(
            current_username,
            new_name,
            new_username,
            new_phone,
            hashed_password
        )

        if success:
            # Update session state immediately so the rest of the app uses
            # the new username/name without requiring another login.
            st.session_state.username = new_username
            st.session_state.name = new_name

            st.success("Profile updated successfully! ✅")
            st.rerun()
        else:
            st.error(message)


# ============================================================
# DASHBOARD PAGE
# ============================================================

def show_dashboard():
    header.show_brand_header()


    st.write(
        f"## Welcome back, "
        f"{st.session_state.get('name', st.session_state.username)}! 👋"
    )

    st.write(
        "Ready to challenge your brain today? "
        "Navigate to the **Test** section from the sidebar "
        "to begin."
    )

    st.write("---")

    results = database.get_user_results(
        st.session_state.username
    )

    if results:

        # Convert results into DataFrame
        df = pd.DataFrame(
            results,
            columns=[
                "Category",
                "Score",
                "Total",
                "Percentage",
                "Date"
            ]
        )

        # Statistics
        total_tests = len(df)

        best_score = df["Percentage"].max()

        avg_score = df["Percentage"].mean()

        # Strongest subject
        subject_means = (
            df.groupby("Category")["Percentage"]
            .mean()
        )

        best_subject = subject_means.idxmax()

        st.markdown(
            "### 📊 Your Performance Overview"
        )

        # ====================================================
        # KPI CARDS
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            with st.container(border=True):

                st.metric(
                    "Tests Taken",
                    total_tests
                )

        with col2:

            with st.container(border=True):

                st.metric(
                    "Average Score",
                    f"{avg_score:.1f}%"
                )

        with col3:

            with st.container(border=True):

                st.metric(
                    "Highest Score",
                    f"{best_score:.1f}%"
                )

        with col4:

            with st.container(border=True):

                st.metric(
                    "Strongest Subject",
                    best_subject
                )

        st.write("---")

        # ====================================================
        # CHART + RECENT ACTIVITY
        # ====================================================

        chart_col, activity_col = st.columns([2, 1])

        with chart_col:

            st.markdown(
                "### 📈 Average Score by Subject"
            )

            st.bar_chart(
                subject_means,
                color="#4A90E2"
            )

        with activity_col:

            st.markdown(
                "### 🕒 Recent Activity"
            )

            recent_tests = df.head(3)

            for _, row in recent_tests.iterrows():

                with st.container(border=True):

                    st.write(
                        f"**{row['Category']}**"
                    )

                    date_only = str(
                        row["Date"]
                    ).split()[0]

                    st.write(
                        f"Score: **{row['Percentage']}%** "
                        f"| 📅 {date_only}"
                    )

    else:

        st.info(
            "You haven't taken any tests yet! "
            "Go to the 'Test' tab in the sidebar to "
            "complete your first assessment and unlock "
            "your analytics dashboard."
        )


# ============================================================
# ABOUT PAGE
# ============================================================

def show_about_page():
    header.show_brand_header()

    st.title("About / Info")

    # About BrainBoost
    with st.container(border=True):
        st.subheader("🧠 About BrainBoost")

        st.write(
            "BrainBoost Test is a web-based Multiple Choice Question (MCQ) "
            "testing and knowledge assessment system developed as a college "
            "minor project."
        )

        st.write(
            "The system allows users to create an account, take subject-based "
            "tests, view their results, and track their performance over time."
        )

    # Purpose
    with st.container(border=True):
        st.subheader("🎯 Purpose of the Project")

        st.write(
            "The main purpose of BrainBoost Test is to provide a simple and "
            "interactive platform for testing knowledge and improving learning "
            "through subject-based assessments."
        )

        st.markdown("""
        **The system helps users to:**

        - Test their knowledge through MCQ questions
        - Practice different subjects
        - View scores and percentages
        - Track previous test results
        - Identify stronger subjects
        - Monitor overall performance
        """)

    # Features
    with st.container(border=True):
        st.subheader("✨ Key Features")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **👤 User Features**

            - User Registration and Login
            - Secure Password Handling
            - Personal Profile
            - Subject-based Tests
            - Automatic Score Calculation
            - Test History
            - Performance Statistics
            """)

        with col2:
            st.markdown("""
            **🔐 Admin Features**

            - Admin Dashboard
            - Add Questions
            - Question Bank
            - Edit Questions
            - Delete Questions
            - View Registered Users
            - Monitor Test Statistics
            """)

    # Subjects
    with st.container(border=True):
        st.subheader("📚 Available Subjects")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **🔢 Mathematics**

            """)

        with col2:
            st.markdown("""
            **🔬 Science**

            """)

        with col3:
            st.markdown("""
            **💻 Computer**

            """)

        st.write("")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🌱 Environment**

            """)

        with col2:
            st.markdown("""
            **🌎 General Knowledge**

            """)

    # How it works
    with st.container(border=True):
        st.subheader("⚙️ How BrainBoost Works")

        st.markdown("""
        **1️⃣ Create an Account**  

        **2️⃣ Login**  

        **3️⃣ Choose a Subject**  

        **4️⃣ Take the Test**  

        **5️⃣ Submit the Test**  

        **6️⃣ View Results**  

        **7️⃣ Track Performance**  
        """)

    # Technologies
    with st.container(border=True):
        st.subheader("🛠️ Technologies Used")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🐍 Python**  

            **🎈 Streamlit**  

            **🗄️ SQLite**  
            """)

        with col2:
            st.markdown("""
            **🐼 Pandas**  

            **🎨 CSS**  

            **📊 Streamlit Charts**  
            """)


    # Creator
    st.markdown(
        '<div class="spark-divider"><span class="spark-icon">©️</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "<h4 style='text-align: center; color: #888;'>"
        "Created by SPARK ⚡"
        "</h4>",
        unsafe_allow_html=True
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    load_css()

    video_path = os.path.join(
        os.path.dirname(__file__),
        "assets",
        "background.mp4"
    )

    set_video_background(video_path)

    database.create_tables()
    init_session_state()

    if not st.session_state.logged_in:

        show_auth_page()

    else:

        if st.session_state.is_admin:

            admin.show_admin_panel()

            st.sidebar.write("---")

            if st.sidebar.button(
                "⏻ Logout",
                key="admin_logout",
                use_container_width=True
            ):
                logout()

        else:

            st.sidebar.title("🧠BrainBoost⚡ Menu")
            st.sidebar.write("---")


            menu = [
                "🚪Dashboard",
                "👤My Profile",
                "📑Test",
                "📊My Results",
                "ℹ️About / Info"
            ]

            choice = st.sidebar.radio(
                "Navigation",
                menu
            )

            st.sidebar.write("---")

            if st.sidebar.button(
                "⏻ Logout",
                key="user_logout",
                use_container_width=True
            ):
                logout()

            if choice == "🚪Dashboard":
                show_dashboard()

            elif choice == "👤My Profile":
                show_profile_page()

            elif choice == "📑Test":
                show_test_page()

            elif choice == "📊My Results":
                show_results_page()

            elif choice == "ℹ️About / Info":
                show_about_page()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    main()