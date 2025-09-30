# app.py
import subprocess
import sys
import os

if __name__ == "__main__":
    # Path of your streamlit app
    streamlit_app_path = os.path.join("src", "streamlit_app.py")
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_app_path])
