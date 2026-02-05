🚀 InsightFlow Support & Feedback Portal

A sleek, high-contrast Flask & React application delivering enterprise-grade support with dual-path conversations, encrypted-style ticket IDs, and instant PDF receipts.


✨ Highlights
👤 Customer Experience

Smart Routing — Dynamic branching: Feedback (FBK-XXX) or Complaint (CMP-XXX)
Instant Receipts — Download official PDF tickets via jsPDF
Live Tracking — Real-time status checks (Pending/Resolved)
Premium Design — Glassmorphism UI on pure black (#000)

🛡️ Admin Control

Secure Dashboard — Password-protected portal (default: admin123)
Visual Analytics — Chart.js satisfaction graphs
Full Transcripts — Individual .txt session logs
Quick Actions — One-click resolution & synchronized deletion


🛠️ Tech Stack
LayerTechnologyBackendPython / FlaskFrontendReact 18 + Tailwind CSSChartsChart.jsPDFsjsPDFStorageJSON + TXT files

📂 Structure
project-folder/
├── app.py              # Flask API & logic
├── history.json        # Central database
├── reports/            # Session transcripts
└── static/
    └── index.html      # React frontend

⚡ Quick Start
bash# Install dependencies
pip install flask

# Run server
python app.py

# Open browser
http://127.0.0.1:5000
The app auto-creates the reports/ folder if missing.

📖 Usage
Customers → Start session → Follow prompts → Download PDF → Track with Case ID
Admins → Enter passphrase → View analytics → Manage transcripts → Resolve tickets

🔒 Security
Change admin password in app.py:
pythonADMIN_PASSWORD = "your-secure-password"
Backup reminder: Regularly save history.json and reports/ directory.

<div align="center">
Built for seamless support experiences 🎯
</div>
