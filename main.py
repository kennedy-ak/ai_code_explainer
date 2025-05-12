import streamlit as st
import os
from groq import Groq
import tempfile

# Set page configuration
st.set_page_config(
    page_title="Code Explainer",
    page_icon="💻",
    layout="wide"
)

# Initialize Groq client
def initialize_groq_client():
    api_key = "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"
    if not api_key:
        api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")
        if not api_key:
            st.sidebar.warning("Please enter your Groq API Key to proceed")
            return None
    return Groq(api_key=api_key)

# Function to explain code using Groq API
def explain_code(client, code, model="llama3-70b-8192", detail_level="medium"):
    # Customize the prompt based on detail level
    if detail_level == "basic":
        prompt = f"""I need a simple and brief explanation of the following code:
```
{code}
```
Please provide:
1. What the code does overall (1-2 sentences)
2. The main functions or components (brief list)
3. Any potential issues to be aware of

Keep the explanation concise and beginner-friendly."""

    elif detail_level == "medium":
        prompt = f"""Please explain the following code in a detailed but accessible way:
```
{code}
```
Include:
1. Overall purpose and functionality
2. Explanation of each major component or function
3. The flow of execution 
4. Any notable patterns or techniques used
5. Potential edge cases or limitations"""

    else:  # detailed
        prompt = f"""I need a comprehensive and in-depth analysis of this code:
```
{code}
```
Please provide:
1. Detailed purpose and context of the code
2. Line-by-line or block-by-block explanation where appropriate
3. Thorough analysis of the logic and algorithms used
4. Evaluation of error handling and edge cases
5. Potential optimization opportunities
6. Best practices followed or missed
7. Suggestions for improvement or alternative approaches"""

    # Call the Groq API
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model=model,
        temperature=0.1,
        max_tokens=4096
    )
    
    return chat_completion.choices[0].message.content

def main():
    # Sidebar for configuration
    st.sidebar.title("Configuration")
    
    # Groq model selection
    model_options = {
        "Llama 3 70B": "llama-3.3-70b-versatile",
        "Mixtral 8x7B": "llama-3.1-8b-instant",
        "Gemma 7B": "gemma2-9b-it"
    }
    selected_model = st.sidebar.selectbox(
        "Select Groq Model", 
        list(model_options.keys())
    )
    model = model_options[selected_model]
    
    # Detail level selection
    detail_level = st.sidebar.radio(
        "Explanation Detail Level",
        options=["basic", "medium", "detailed"],
        index=1
    )
    
    # Main content
    st.title("💻 Code Explainer")
    st.markdown("""
    Upload a code file or paste your code to get an AI-powered explanation.
    """)
    
    # Input methods: file upload or text input
    input_method = st.radio(
        "Choose input method:",
        ["Upload a file", "Paste code"]
    )
    
    code = ""
    if input_method == "Upload a file":
        uploaded_file = st.file_uploader("Upload your code file", type=['py', 'js', 'java', 'cpp', 'c', 'html', 'css', 'go', 'rb', 'php', 'ts', 'sh', 'sql', 'r', 'swift'])
        
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            with open(tmp_file_path, 'r') as file:
                try:
                    code = file.read()
                    st.code(code)
                except UnicodeDecodeError:
                    st.error("Unable to read the file. Please ensure it's a text-based code file.")
                    code = ""
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
    else:  # Paste code
        code = st.text_area("Paste your code here:", height=300)
    
    # Add language selection for context
    languages = ["Python", "JavaScript", "Java", "C++", "C", "HTML/CSS", "Go", "Ruby", "PHP", "TypeScript", "Shell", "SQL", "R", "Swift", "Other"]
    language = st.selectbox("Select the programming language (for context):", languages)
    
    # Process button
    if st.button("Explain Code", key=f"explain_code_button") and code:
        with st.spinner("Analyzing your code..."):
            # Initialize Groq client
            client = initialize_groq_client()
            if client:
                try:
                    explanation = explain_code(client, code, model, detail_level)
                    
                    # Display explanation
                    st.subheader("Explanation")
                    st.markdown(explanation)
                    
                    # Additional features
                    with st.expander("Want more information?"):
                        st.markdown("""
                        You can:
                        - Change the detail level in the sidebar
                        - Try different models for different perspectives
                        - Upload a different file or paste new code
                        """)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please provide a valid Groq API Key in the sidebar")
    elif not code and st.button("Explain Code"):
        st.warning("Please upload a file or paste some code first.")

if __name__ == "__main__":
    main()