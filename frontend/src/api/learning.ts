import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/learning`,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Level {
  id: number;
  level_number: number;
  title: string;
  description: string;
  required_xp: number;
  is_active: boolean;
}

export interface Lesson {
  id: number;
  level_id: number;
  lesson_number: number;
  title: string;
  description: string;
  lesson_type: 'theory' | 'coding_exercise' | 'multiple_choice' | 'fill_in_blank';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  xp_reward: number;
  is_completed?: boolean;
  score?: number;
}

export interface Question {
  id: number;
  lesson_id: number;
  question_text: string;
  question_type: 'theory' | 'coding_exercise' | 'multiple_choice' | 'fill_in_blank';
  options?: string;
  code_template?: string;
}

export interface UserProfile {
  id: number;
  user_id: number;
  current_level: number;
  total_xp: number;
  current_streak: number;
  longest_streak: number;
  lessons_completed: number;
  accuracy_rate: number;
  last_activity_date?: string;
}

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  requirement_type: string;
  requirement_value: number;
  xp_reward: number;
  earned_at?: string;
}

export interface QuestionSubmission {
  question_id: number;
  answer: string;
}

export interface SubmissionResult {
  correct: boolean;
  explanation: string;
  xp_earned: number;
}

export const learningAPI = {
  // Get user profile
  getProfile: async (): Promise<UserProfile> => {
    const response = await api.get('/profile');
    return response.data;
  },

  // Get all levels
  getLevels: async (): Promise<Level[]> => {
    const response = await api.get('/levels');
    return response.data;
  },

  // Get lessons for a level
  getLevelLessons: async (levelId: number): Promise<Lesson[]> => {
    const response = await api.get(`/levels/${levelId}/lessons`);
    return response.data;
  },

  // Get questions for a lesson
  getLessonQuestions: async (lessonId: number): Promise<Question[]> => {
    const response = await api.get(`/lessons/${lessonId}/questions`);
    return response.data;
  },

  // Submit answer
  submitAnswer: async (submission: QuestionSubmission): Promise<SubmissionResult> => {
    const response = await api.post('/questions/submit', submission);
    return response.data;
  },

  // Get achievements
  getAchievements: async (): Promise<Achievement[]> => {
    const response = await api.get('/achievements');
    return response.data;
  },

  // Get progress stats
  getProgressStats: async () => {
    const response = await api.get('/progress/stats');
    return response.data;
  },

  // Generate AI question (admin)
  generateQuestion: async (topic: string, difficulty: string, questionType: string) => {
    const response = await api.post('/questions/generate', {
      topic,
      difficulty,
      question_type: questionType
    });
    return response.data;
  }
};