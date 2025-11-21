# Football Predictor

A mobile-optimized web application for tracking NFL football picks against the spread. Users can log in with Google, submit weekly picks, view leaderboards, and compare their performance with others.

## Features

*   **Authentication**: Secure login via Google OAuth.
*   **Weekly Picks**: Submit picks against the spread for NFL games.
*   **Leaderboard**: View weekly and overall rankings based on correct picks and win rates.
*   **Comparison**: Head-to-head comparison of picks between users.
*   **Mobile-First Design**: Optimized for mobile devices with a responsive UI.

## Tech Stack

*   **Frontend**: Next.js 14+ (App Router), Tailwind CSS, TypeScript.
*   **Backend**: FastAPI (Python), SQLModel, PostgreSQL, Alembic.
*   **Database**: PostgreSQL.

## Setup Instructions

### Prerequisites

*   Node.js & npm
*   Python 3.10+
*   PostgreSQL
*   Google Cloud Console Project (for OAuth Client ID)

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, install manually: `fastapi uvicorn[standard] sqlmodel alembic psycopg2-binary python-multipart pyjwt requests google-auth google-auth-oauthlib google-auth-httplib2 httpx`)*
4.  Set up environment variables:
    Copy `.env.example` to `.env` and update the values:
    ```bash
    cp .env.example .env
    ```
    *   `DATABASE_URL`: Your PostgreSQL connection string.
    *   `SECRET_KEY`: A secure random string.
    *   `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID.
5.  Run database migrations:
    ```bash
    alembic upgrade head
    ```
6.  Seed the database (optional):
    ```bash
    python app/seed.py        # Seeds NFL teams
    python app/seed_weeks.py  # Seeds sample weeks and games
    ```
7.  Start the server:
    ```bash
    uvicorn app.main:app --reload
    ```

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Set up environment variables:
    Copy `env.example` to `.env.local` and update the values:
    ```bash
    cp env.example .env.local
    ```
    *   `NEXT_PUBLIC_API_URL`: URL of your backend (default: `http://localhost:8000`).
    *   `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: Your Google OAuth Client ID.
4.  Start the development server:
    ```bash
    npm run dev
    ```
5.  Open [http://localhost:3000](http://localhost:3000) in your browser.

## License

[MIT](LICENSE)
