import streamlit as st
import sys
import subprocess
from io import StringIO
import contextlib
import traceback
import matplotlib.pyplot as plt

st.set_page_config(page_title="Jupyter-like Notebook", layout="wide")

# Initialize session state
if 'cells' not in st.session_state:
    st.session_state.cells = [{'code': '', 'output': '', 'error': ''}]
if 'namespace' not in st.session_state:
    st.session_state.namespace = {}
if 'installed_packages' not in st.session_state:
    st.session_state.installed_packages = []

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True, f"Successfully installed {package_name}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to install {package_name}: {str(e)}"

def execute_code(code, namespace):
    """Execute code and capture output, errors, and plots"""
    output = StringIO()
    error = ''
    
    # Check for pip install commands
    if code.strip().startswith('!pip install') or code.strip().startswith('pip install'):
        package = code.replace('!pip install', '').replace('pip install', '').strip()
        success, message = install_package(package)
        if success:
            st.session_state.installed_packages.append(package)
        return message, '' if success else message
    
    try:
        # Capture stdout
        with contextlib.redirect_stdout(output):
            # Try to get the result of the last expression
            try:
                # Split into statements
                code_lines = code.strip().split('\n')
                
                # Execute all but last line
                if len(code_lines) > 1:
                    exec('\n'.join(code_lines[:-1]), namespace)
                
                # Try to eval the last line for display
                last_line = code_lines[-1].strip()
                if last_line and not last_line.startswith(('print', 'plt.', 'import', 'from', 'def', 'class', 'if', 'for', 'while', '=')):
                    result = eval(last_line, namespace)
                    if result is not None:
                        print(result)
                else:
                    exec(last_line, namespace)
            except SyntaxError:
                # If eval fails, just exec everything
                exec(code, namespace)
            
        # Check if matplotlib has any figures
        if plt.get_fignums():
            st.pyplot(plt.gcf())
            plt.clf()
            
    except Exception as e:
        error = f"Error: {type(e).__name__}\n{traceback.format_exc()}"
    
    return output.getvalue(), error

# Title and description
st.title("🎯 Jupyter-like Notebook in Streamlit")
st.markdown("Execute Python code with persistent variables and install packages on the fly!")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    
    # Package installation section
    st.subheader("📦 Install Package")
    package_name = st.text_input("Package name", placeholder="e.g., requests, beautifulsoup4")
    if st.button("Install Package"):
        if package_name:
            with st.spinner(f"Installing {package_name}..."):
                success, message = install_package(package_name)
                if success:
                    st.session_state.installed_packages.append(package_name)
                    st.success(message)
                else:
                    st.error(message)
    
    if st.session_state.installed_packages:
        st.markdown("**Installed this session:**")
        for pkg in st.session_state.installed_packages:
            st.code(pkg)
    
    st.markdown("---")
    
    if st.button("➕ Add Cell"):
        st.session_state.cells.append({'code': '', 'output': '', 'error': ''})
        st.rerun()
    
    if st.button("🔄 Clear All Output"):
        for cell in st.session_state.cells:
            cell['output'] = ''
            cell['error'] = ''
        st.rerun()
    
    if st.button("🗑️ Reset Notebook"):
        st.session_state.cells = [{'code': '', 'output': '', 'error': ''}]
        st.session_state.namespace = {}
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Current Variables:**")
    if st.session_state.namespace:
        vars_to_show = {k: type(v).__name__ for k, v in st.session_state.namespace.items() 
                       if not k.startswith('__') and not callable(v)}
        for var, var_type in vars_to_show.items():
            st.code(f"{var}: {var_type}", language="python")
    else:
        st.info("No variables yet")

# Display cells
for idx, cell in enumerate(st.session_state.cells):
    col1, col2 = st.columns([20, 1])
    
    with col1:
        st.markdown(f"**Cell [{idx + 1}]**")
    
    with col2:
        if st.button("🗑️", key=f"delete_{idx}"):
            if len(st.session_state.cells) > 1:
                st.session_state.cells.pop(idx)
                st.rerun()
    
    # Code input
    code = st.text_area(
        "Code",
        value=cell['code'],
        height=150,
        key=f"code_{idx}",
        label_visibility="collapsed"
    )
    
    # Update cell code
    cell['code'] = code
    
    # Run button
    col_run, col_clear = st.columns([1, 5])
    with col_run:
        if st.button("▶️ Run", key=f"run_{idx}"):
            if code.strip():
                output, error = execute_code(code, st.session_state.namespace)
                cell['output'] = output
                cell['error'] = error
                st.rerun()
    
    with col_clear:
        if st.button("Clear Output", key=f"clear_{idx}"):
            cell['output'] = ''
            cell['error'] = ''
            st.rerun()
    
    # Display output
    if cell['error']:
        st.error(cell['error'])
    elif cell['output']:
        st.code(cell['output'], language="text")
    
    st.markdown("---")

# Quick examples
with st.expander("📚 Example Code Snippets"):
    st.markdown("""
    **Install packages directly in cells:**
    
    ```python
    # Install a package
    !pip install requests
    ```
    
    ```python
    # Use the installed package
    import requests
    response = requests.get('https://api.github.com')
    print(f"Status: {response.status_code}")
    ```
    
    **Working with data:**
    
    ```python
    # Cell 1: Import and create data
    import numpy as np
    import pandas as pd
    data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]}
    df = pd.DataFrame(data)
    df
    ```
    
    ```python
    # Cell 2: Use the data from previous cell
    print(f"Mean of y: {df['y'].mean()}")
    print(f"Sum of x: {df['x'].sum()}")
    ```
    
    ```python
    # Cell 3: Create a plot
    import matplotlib.pyplot as plt
    plt.plot(df['x'], df['y'], marker='o')
    plt.xlabel('X values')
    plt.ylabel('Y values')
    plt.title('Simple Line Plot')
    plt.grid(True)
    ```
    
    **Web scraping example:**
    ```python
    # First install: !pip install beautifulsoup4
    from bs4 import BeautifulSoup
    import requests
    
    response = requests.get('https://example.com')
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.title.text)
    ```
    """)
    
st.markdown(```mermaid
flowchart TD
    A[User Inputs Website URL] --> B[Agent Initialization]
    B --> C[Reconnaissance Phase]
    C -->|Fetches and scans| D[Web Scanner Module]
    C -->|Collects metadata, headers, endpoints| E[Data Collector]
    D --> F[Vulnerability Detection Engine]
    E --> F
    F -->|Static + Dynamic tests| G[AI Analysis Layer]
    G -->|Ranks vulnerabilities by risk| H[Risk Scoring System]
    H --> I[Recommendation Generator]
    I -->|Auto-suggests mitigation steps| J[Comprehensive Security Report]
    J --> K[Frontend Dashboard / PDF Export]

    subgraph Backend
        D
        E
        F
        G
        H
        I
    end

    subgraph Frontend
        A
        J
        K
    end
    ```)