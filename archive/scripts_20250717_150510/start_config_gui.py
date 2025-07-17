#!/usr/bin/env python3
import os
import subprocess
import webbrowser
import time
import threading

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:3000/dev-gui.html")

print("🚀 Starting Configuration GUI...")
print("📱 Open: http://localhost:3000/dev-gui.html")

# Open browser
browser_thread = threading.Thread(target=open_browser)
browser_thread.daemon = True
browser_thread.start()

# Start server
os.chdir("tools")
subprocess.run(["python3", "-m", "http.server", "3000"])
