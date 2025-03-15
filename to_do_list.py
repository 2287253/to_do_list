import streamlit as st
import json
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Simple To-Do List",
    layout="wide"
)

# File to store the to-do items
TODO_FILE = "todo_data.json"

# Load to-do items from the JSON file
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Save to-do items to the JSON file
def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=4)

# Main app header
st.title("📝 Simple To-Do List")
st.markdown("Keep track of your tasks with this simple to-do list app.")

# Sidebar for adding new tasks
with st.sidebar:
    st.header("Add New Task")
    with st.form(key="add_task_form", clear_on_submit=True):
        task_title = st.text_input("Task Title")
        task_description = st.text_area("Description (optional)")
        task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        task_due_date = st.date_input("Due Date (optional)")
        
        submit_button = st.form_submit_button(label="Add Task")
        
        if submit_button and task_title:
            todos = load_todos()
            
            # Generate a unique ID
            task_id = 1
            if todos:
                task_id = max(todo.get("id", 0) for todo in todos) + 1
            
            # Create new task
            new_task = {
                "id": task_id,
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "due_date": task_due_date.strftime("%Y-%m-%d") if task_due_date else None,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            todos.append(new_task)
            save_todos(todos)
            st.success(f"Task '{task_title}' added successfully!")

# Main content area
st.header("Your Tasks")

# Filter options
col1, col2 = st.columns(2)
with col1:
    filter_status = st.radio("Filter by Status", ["All", "Active", "Completed"])
with col2:
    filter_priority = st.radio("Filter by Priority", ["All", "High", "Medium", "Low"])

# Load and filter tasks
todos = load_todos()

if filter_status == "Active":
    todos = [todo for todo in todos if not todo.get("completed", False)]
elif filter_status == "Completed":
    todos = [todo for todo in todos if todo.get("completed", False)]

if filter_priority != "All":
    todos = [todo for todo in todos if todo.get("priority") == filter_priority]

# Sort tasks by creation date (newest first)
todos.sort(key=lambda x: x.get("created_at", ""), reverse=True)

# Display tasks
if not todos:
    st.info("No tasks found. Add some tasks using the sidebar form!")
else:
    for todo in todos:
        with st.container():
            col1, col2 = st.columns([6, 1])
            
            with col1:
                # Task title with checkbox
                completed = st.checkbox(
                    todo.get("title", "Untitled Task"),
                    value=todo.get("completed", False),
                    key=f"task_{todo.get('id', 0)}"
                )
                
                # Update completion status if changed
                if completed != todo.get("completed", False):
                    todo["completed"] = completed
                    if completed:
                        todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        todo["completed_at"] = None
                    save_todos(load_todos())
                
                # Task details
                if todo.get("description"):
                    st.markdown(f"**Description:** {todo.get('description')}")
                
                # Task metadata
                priority_color = {
                    "High": "🔴",
                    "Medium": "🟠",
                    "Low": "🟢"
                }.get(todo.get("priority"), "⚪")
                
                meta = f"{priority_color} **Priority:** {todo.get('priority', 'None')} | "
                if todo.get("due_date"):
                    meta += f"**Due:** {todo.get('due_date')} | "
                meta += f"**Created:** {todo.get('created_at', 'Unknown')}"
                st.markdown(meta)
            
            with col2:
                # Delete button
                if st.button("🗑️", key=f"delete_{todo.get('id', 0)}"):
                    todos = load_todos()
                    todos = [t for t in todos if t.get("id") != todo.get("id")]
                    save_todos(todos)
                    st.experimental_rerun()
            
            st.markdown("---")

# Footer
st.markdown("---")
st.markdown("### Task Summary")
all_todos = load_todos()
total = len(all_todos)
completed = sum(1 for todo in all_todos if todo.get("completed", False))
active = total - completed

col1, col2, col3 = st.columns(3)
col1.metric("Total Tasks", total)
col2.metric("Active Tasks", active)
col3.metric("Completed Tasks", completed)

st.markdown("---")
st.caption("Simple To-Do List App | Created with Streamlit")
