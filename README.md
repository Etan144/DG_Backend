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