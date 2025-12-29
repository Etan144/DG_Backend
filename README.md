# DG_Backend
FastAPI backend service for user authentication and account management using MongoDB Atlas and OTP verification.
## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account

### Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DG_Backend
   ```

2. **Create and activate virtual environment**
   
   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   **PowerShell only**
   **if cannot run script in powershell, run the following for each session**
   ```bash
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```
   
   **Windows (Command Prompt):**
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory with:
   ```env
   MONGODB_URL=your_mongodb_atlas_connection_string
   SECRET_KEY=your_secret_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```

5. **Run the server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Important: Git Workflow

⚠️ **Always activate the virtual environment before running git commands**

When contributing to this project, ensure you're inside the `venv` environment before running `git add`, `git commit`, or any git operations. This prevents accidentally committing virtual environment files or other unwanted files.

```bash
# ✅ Correct
.\venv\Scripts\Activate.ps1  # Activate venv first
git add .
git commit -m "message"

# ❌ Wrong - don't do this
git add .  # without activating venv first
git commit -m "message"
```

The `.gitignore` file protects the repo, but it's a best practice to always work within the activated environment.
