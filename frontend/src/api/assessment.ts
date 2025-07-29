import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/assessment`,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface AssessmentQuestion {
  id: number;
  question_text: string;
  question_type: string;
  options?: string;
  topic_area: string;
  expected_level: number;
}

export interface AssessmentAnswer {
  question_id: number;
  answer: string;
  confidence_level?: number;
  time_taken_seconds?: number;
}

export interface AssessmentSubmission {
  answers: AssessmentAnswer[];
}

export interface AssessmentResult {
  assessment_id: number;
  total_questions: number;
  correct_answers: number;
  accuracy_percentage: number;
  calculated_level: number;
  skill_level: string;
  time_taken_minutes?: number;
  topic_breakdown: Record<string, any>;
  recommendations: string[];
}

export interface UserSkillProfile {
  user_id: number;
  overall_skill_level: string;
  adaptive_level: number;
  basics_mastery: number;
  control_flow_mastery: number;
  functions_mastery: number;
  arrays_mastery: number;
  pointers_mastery: number;
  learning_velocity: number;
  prefers_challenge: boolean;
  needs_more_practice: boolean;
}

export interface AssessmentHistory {
  id: number;
  type: string;
  accuracy: number;
  level: number;
  completed_at: string;
  time_taken?: number;
}

export const assessmentAPI = {
  // Start a new assessment
  startAssessment: async (): Promise<AssessmentQuestion[]> => {
    console.log('API: Making request to /start...');
    console.log('API: Base URL:', api.defaults.baseURL);
    console.log('API: Token:', localStorage.getItem('token') ? 'Present' : 'Missing');
    
    const response = await api.get('/start');
    console.log('API: Response received:', response.status, response.data);
    return response.data;
  },

  // Submit assessment answers
  submitAssessment: async (submission: AssessmentSubmission): Promise<AssessmentResult> => {
    const response = await api.post('/submit', submission);
    return response.data;
  },

  // Get user's skill profile
  getSkillProfile: async (): Promise<UserSkillProfile> => {
    const response = await api.get('/profile');
    return response.data;
  },

  // Get assessment history
  getHistory: async (): Promise<AssessmentHistory[]> => {
    const response = await api.get('/history');
    return response.data;
  },

  // Allow retaking assessment
  allowRetake: async (): Promise<{ message: string; type: string }> => {
    const response = await api.post('/retake');
    return response.data;
  }
};