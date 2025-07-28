# AI Coding Learner 🚀

A Duolingo-style interactive platform for learning C programming with AI-powered questions and gamification.

## Features ✨

- **10 Progressive Levels** of C programming (Hello World → Pointers & Memory)
- **Interactive Learning** with multiple question types:
  - Multiple choice questions
  - Coding exercises
  - Fill-in-the-blank
- **Gamification**: XP points, streaks, achievements, level progression
- **AI-Powered Content**: Dynamic question generation using OpenAI
- **Progress Tracking**: Visual progress maps and user profiles
- **Responsive Design**: Modern React UI with TypeScript

## Tech Stack 🛠️

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL/SQLite
- OpenAI API
- JWT Authentication

**Frontend:**
- React 19 with TypeScript
- React Router
- Axios for API calls
- Custom theming system

## Quick Setup 🚀

### Prerequisites
- Python 3.11+
- Node.js 16+
- OpenAI API key (optional, for AI features)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database:**
   ```bash
   python setup_database.py
   ```

6. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   Frontend will be available at `http://localhost:3000`

## Environment Variables 🔧

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///./ai_learner.db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key-here
```

## Usage 📚

1. **Register/Login**: Create an account or log in
2. **Start Learning**: Begin with Level 1 - "Hello, C World!"
3. **Progress Through Levels**: Complete lessons to unlock new ones
4. **Earn XP & Achievements**: Build streaks and unlock badges
5. **Track Progress**: View your learning statistics in your profile

## API Documentation 📖

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Curriculum Structure 📋

1. **Level 1**: Hello, C World! (Basics, first program)
2. **Level 2**: Variables and Data Types
3. **Level 3**: Input and Output
4. **Level 4**: Operators and Expressions
5. **Level 5**: Control Flow - Conditions
6. **Level 6**: Control Flow - Loops
7. **Level 7**: Functions
8. **Level 8**: Arrays
9. **Level 9**: Strings
10. **Level 10**: Pointers and Memory

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License 📄

This project is licensed under the MIT License.

## Support 💡

If you encounter any issues:
1. Check the console logs (both frontend and backend)
2. Ensure all dependencies are installed
3. Verify environment variables are set correctly
4. Create an issue on GitHub

---

Happy Learning! 🎉