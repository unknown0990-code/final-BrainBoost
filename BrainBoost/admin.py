import streamlit as st
import pandas as pd
import header
from database import (get_all_users, get_all_questions, get_all_results, 
                      add_question, update_question, delete_question, get_question_by_id)

def show_admin_panel():
    st.sidebar.header("🛠️Admin Controls")
    st.sidebar.write("---")
    menu = ["📊Admin Dashboard", "➕Add Question", "📚Question Bank", "✏️Edit Question", "🗑️Delete Question", "👥Users"]
    choice = st.sidebar.radio("Navigate", menu)
    
    if choice == "📊Admin Dashboard":
        show_admin_dashboard()
    elif choice == "➕Add Question":
        show_add_question()
    elif choice == "📚Question Bank":
        show_question_bank()
    elif choice == "✏️Edit Question":
        show_edit_question()
    elif choice == "🗑️Delete Question":
        show_delete_question()
    elif choice == "👥Users":
        show_users()

def show_admin_dashboard():
    header.show_brand_header()

    st.title("Admin Dashboard")
    users = get_all_users()
    questions = get_all_questions()
    results = get_all_results()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Registered Users", len(users))
    col2.metric("Total Questions in Bank", len(questions))
    col3.metric("Total Tests Taken", len(results))
    
    st.write("---")
    st.subheader("System Overview")
    st.write("Welcome to the BrainBoost Test Admin Panel. Use the sidebar to manage questions and view users.")

def show_add_question():
    header.show_brand_header()

    st.title("Add New Question")
    categories = ["Mathematics", "Science", "Computer", "Environment", "General Knowledge"]
    
    with st.form("add_q_form", clear_on_submit=True):
        cat = st.selectbox("Category", categories)
        q_text = st.text_area("Question")
        o1 = st.text_input("Option 1")
        o2 = st.text_input("Option 2")
        o3 = st.text_input("Option 3")
        o4 = st.text_input("Option 4")
        ans = st.text_input("Correct Answer (Must match one of the options exactly)")
        
        submitted = st.form_submit_button("Save Question")
        if submitted:
            if not (q_text and o1 and o2 and o3 and o4 and ans):
                st.error("Please fill all fields.")
            elif ans not in [o1, o2, o3, o4]:
                st.error("Correct answer must exactly match one of the options provided.")
            else:
                add_question(cat, q_text, o1, o2, o3, o4, ans)
                st.success("Question Added Successfully!")

def show_question_bank():
    header.show_brand_header()

    st.title("Question Bank")
    questions = get_all_questions()
    
    if not questions:
        st.warning("No questions found.")
        return
        
    df = pd.DataFrame(questions, columns=["ID", "Category", "Question", "Opt1", "Opt2", "Opt3", "Opt4", "Answer"])
    
    categories = ["All"] + list(df['Category'].unique())
    filter_cat = st.selectbox("Filter by Category", categories)
    
    if filter_cat != "All":
        df = df[df['Category'] == filter_cat]
        
    st.dataframe(df, use_container_width=True, hide_index=True)

def show_edit_question():
    header.show_brand_header()

    st.title("Edit Question")
    q_id = st.number_input("Enter Question ID to Edit", min_value=1, step=1)
    
    if st.button("Load Question"):
        q = get_question_by_id(q_id)
        if q:
            st.session_state.edit_q = q
        else:
            st.error("Question ID not found.")
            if 'edit_q' in st.session_state:
                del st.session_state['edit_q']
                
    if 'edit_q' in st.session_state:
        q = st.session_state.edit_q
        st.write("---")
        categories = ["Mathematics", "Science", "Computer", "Environment", "General Knowledge"]
        
        with st.form("edit_q_form"):
            cat = st.selectbox("Category", categories, index=categories.index(q[1]))
            q_text = st.text_area("Question", value=q[2])
            o1 = st.text_input("Option 1", value=q[3])
            o2 = st.text_input("Option 2", value=q[4])
            o3 = st.text_input("Option 3", value=q[5])
            o4 = st.text_input("Option 4", value=q[6])
            ans = st.text_input("Correct Answer", value=q[7])
            
            update_btn = st.form_submit_button("Update Question")
            if update_btn:
                if ans not in [o1, o2, o3, o4]:
                    st.error("Correct answer must exactly match one of the options.")
                else:
                    update_question(q[0], cat, q_text, o1, o2, o3, o4, ans)
                    st.success("Question Updated Successfully!")
                    del st.session_state['edit_q']
                    st.rerun()

def show_delete_question():
    header.show_brand_header()

    st.title("Delete Question")
    q_id = st.number_input("Enter Question ID to Delete", min_value=1, step=1)
    
    if st.button("Find Question"):
        q = get_question_by_id(q_id)
        if q:
            st.session_state.del_q = q
        else:
            st.error("Question ID not found.")
            if 'del_q' in st.session_state:
                del st.session_state['del_q']
                
    if 'del_q' in st.session_state:
        q = st.session_state.del_q
        st.warning(f"Are you sure you want to delete this question?")
        st.info(f"**Question:** {q[2]}")
        
        confirm = st.checkbox("I confirm deletion")
        if st.button("Delete"):
            if confirm:
                delete_question(q[0])
                st.success("Question Deleted!")
                del st.session_state['del_q']
                st.rerun()
            else:
                st.error("Please check the confirmation box.")

def show_users():
    header.show_brand_header()

    st.title("👥 Student Management")

    users = get_all_users()
    results = get_all_results()

    if not users:
        st.info("No users registered yet.")
        return

    # REGISTERED USERS
    st.subheader("📋 Registered Users")

    users_df = pd.DataFrame(
        users,
        columns=["ID", "Name", "Username", "Phone"]
    )

    st.dataframe(
        users_df,
        use_container_width=True,
        hide_index=True
    )

    st.write("---")

    # SELECT STUDENT
    st.subheader("📊 Student Performance")

    user_options = {
        f"{user[1]} (@{user[2]})": user[2]
        for user in users
    }

    selected_student = st.selectbox(
        "Select a student to view performance",
        options=list(user_options.keys()),
        key="admin_student_select"
    )

    username = user_options[selected_student]

    # FILTER RESULTS FOR SELECTED STUDENT
    student_results = [
        result for result in results
        if result[1] == username
    ]

    if not student_results:
        st.info(
            f"{selected_student} has not taken any tests yet."
        )
        return

    # SUMMARY STATISTICS
    total_tests = len(student_results)

    best_score = max(
        (result[5] for result in student_results)
    )

    average_score = sum(
        result[5] for result in student_results
    ) / total_tests

    total_correct = sum(
        result[3] for result in student_results
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tests Taken", total_tests)
    col2.metric("Best Score", f"{best_score:.1f}%")
    col3.metric("Avg Score", f"{average_score:.1f}%")
    col4.metric("Total Correct", total_correct)

    st.write("---")

    # AVERAGE SCORE BY SUBJECT
    st.subheader("📈 Average Score by Subject")

    history_df = pd.DataFrame(
        student_results,
        columns=[
            "ID", "Username", "Category",
            "Score", "Total", "Percentage", "Date"
        ]
    )

    subject_average = (
        history_df.groupby("Category")["Percentage"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        subject_average,
        color="#4A90E2",
        y_label="Average Percentage (%)"
    )

    st.write("---")

    # TEST HISTORY
    st.subheader("📝 Test History")

    display_df = history_df[
        ["Category", "Score", "Total", "Percentage", "Date"]
    ].copy()

    display_df["Percentage"] = display_df[
        "Percentage"
    ].apply(lambda value: f"{value:.2f}%")

    display_df.rename(
        columns={"Percentage": "Percentage (%)"},
        inplace=True
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )



