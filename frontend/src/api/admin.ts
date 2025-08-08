import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/admin`,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface AdminStats {
  total_users: number;
  active_users: number;
  total_lessons_completed: number;
  total_assessments: number;
  average_accuracy: number;
  popular_levels: Array<{
    level: number;
    title: string;
    completions: number;
  }>;
  recent_registrations: Array<{
    id: number;
    username: string;
    email: string;
    created_at: string;
  }>;
}

export interface AdminUser {
  id: number;
  email: string;
  username: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface AdminQuestion {
  id: number;
  lesson_id: number;
  question_text: string;
  question_type: string;
  correct_answer: string;
  options?: string;
  explanation?: string;
  code_template?: string;
}

export interface CreateQuestionRequest {
  lesson_id: number;
  question_text: string;
  question_type: 'multiple_choice' | 'coding_exercise' | 'fill_in_blank';
  correct_answer: string;
  options?: string;
  explanation?: string;
  code_template?: string;
}

export interface UpdateUserRequest {
  is_active: boolean;
  role?: 'user' | 'admin';
}

export interface LevelWithLessons {
  id: number;
  level_number: number;
  title: string;
  description: string;
  lessons: Array<{
    id: number;
    title: string;
    description: string;
    lesson_type: string;
    difficulty: string;
    question_count: number;
  }>;
}

export interface Achievement {
  id: number;
  name: string;
  description: string;
  requirement_type: string;
  requirement_value: number;
  xp_reward: number;
  times_earned: number;
}

export interface UserProgressDetail {
  user: AdminUser;
  profile: {
    current_level: number;
    total_xp: number;
    current_streak: number;
    lessons_completed: number;
    accuracy_rate: number;
  };
  lesson_progress: Array<{
    lesson_id: number;
    is_completed: boolean;
    score: number;
    attempts: number;
  }>;
  assessments: Array<{
    id: number;
    accuracy: number;
    level: number;
    skill_level: string;
    completed_at: string;
  }>;
}

export const adminAPI = {
  // Get platform statistics
  getStats: async (): Promise<AdminStats> => {
    const response = await api.get('/stats');
    return response.data;
  },

  // User management
  getUsers: async (skip = 0, limit = 100): Promise<AdminUser[]> => {
    const response = await api.get('/users', { params: { skip, limit } });
    return response.data;
  },

  updateUser: async (userId: number, updateData: UpdateUserRequest) => {
    const response = await api.put(`/users/${userId}`, updateData);
    return response.data;
  },

  getUserProgress: async (userId: number): Promise<UserProgressDetail> => {
    const response = await api.get(`/user-progress/${userId}`);
    return response.data;
  },

  // Question management
  getQuestions: async (lessonId?: number): Promise<AdminQuestion[]> => {
    const params = lessonId ? { lesson_id: lessonId } : {};
    const response = await api.get('/questions', { params });
    return response.data;
  },

  createQuestion: async (questionData: CreateQuestionRequest) => {
    const response = await api.post('/questions', questionData);
    return response.data;
  },

  updateQuestion: async (questionId: number, questionData: CreateQuestionRequest) => {
    const response = await api.put(`/questions/${questionId}`, questionData);
    return response.data;
  },

  deleteQuestion: async (questionId: number) => {
    const response = await api.delete(`/questions/${questionId}`);
    return response.data;
  },

  generateAIQuestion: async (
    lessonId: number,
    topic: string,
    difficulty: 'beginner' | 'intermediate' | 'advanced',
    questionType: 'multiple_choice' | 'coding_exercise' | 'fill_in_blank'
  ) => {
    const response = await api.post('/questions/generate-ai', null, {
      params: {
        lesson_id: lessonId,
        topic,
        difficulty,
        question_type: questionType
      }
    });
    return response.data;
  },

  // Content management
  getLevelsWithLessons: async (): Promise<LevelWithLessons[]> => {
    const response = await api.get('/levels-lessons');
    return response.data;
  },

  getAchievements: async (): Promise<Achievement[]> => {
    const response = await api.get('/achievements');
    return response.data;
  },

  getAssessmentQuestions: async () => {
    const response = await api.get('/assessment-questions');
    return response.data;
  }
};