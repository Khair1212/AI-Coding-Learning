import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export interface SubscriptionPlan {
  id: number;
  tier: 'free' | 'gold' | 'premium';
  name: string;
  price: number;
  currency: string;
  duration_days: number;
  daily_question_limit: number | null;
  max_level_access: number | null;
  ai_questions_enabled: boolean;
  detailed_analytics: boolean;
  priority_support: boolean;
  unlimited_retakes: boolean;
  personalized_tutor: boolean;
  custom_learning_paths: boolean;
  description: string;
}

export interface UserSubscription {
  id: number;
  tier: 'free' | 'gold' | 'premium';
  start_date: string;
  end_date: string | null;
  is_active: boolean;
  auto_renew: boolean;
}

export interface UserLimits {
  subscription_tier: 'free' | 'gold' | 'premium';
  current_usage: {
    questions_attempted: number;
    ai_questions_used: number;
    assessments_taken: number;
  };
  limits: {
    daily_question_limit: number | null;
    max_level_access: number | null;
    ai_questions_enabled: boolean;
    detailed_analytics: boolean;
    priority_support: boolean;
    unlimited_retakes: boolean;
    personalized_tutor: boolean;
    custom_learning_paths: boolean;
  };
  subscription_valid: boolean;
}

export interface PaymentRequest {
  subscription_tier: 'gold' | 'premium';
  success_url: string;
  fail_url: string;
  cancel_url: string;
}

export interface PaymentSession {
  status: 'success' | 'error';
  payment_url?: string;
  session_key?: string;
  transaction_id?: string;
  message?: string;
}

// Create axios instance with auth header
const createAxiosInstance = () => {
  const token = localStorage.getItem('token');
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
};

export const subscriptionAPI = {
  // Get all subscription plans
  getPlans: async (): Promise<SubscriptionPlan[]> => {
    const response = await axios.get(`${API_BASE_URL}/subscription/plans`);
    return response.data;
  },

  // Get user's current subscription
  getMySubscription: async (): Promise<UserSubscription | null> => {
    const api = createAxiosInstance();
    try {
      const response = await api.get('/subscription/my-subscription');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  // Check user's current limits
  checkLimits: async (): Promise<UserLimits> => {
    const api = createAxiosInstance();
    const response = await api.get('/subscription/check-limits');
    return response.data;
  },

  // Create payment session
  createPaymentSession: async (paymentRequest: PaymentRequest): Promise<PaymentSession> => {
    const api = createAxiosInstance();
    const response = await api.post('/subscription/create-payment', paymentRequest);
    return response.data;
  },

  // Get payment history
  getPaymentHistory: async (): Promise<any[]> => {
    const api = createAxiosInstance();
    const response = await api.get('/subscription/payment-history');
    return response.data;
  },

  // Cancel subscription auto-renewal
  cancelSubscription: async (): Promise<{ message: string }> => {
    const api = createAxiosInstance();
    const response = await api.post('/subscription/cancel-subscription');
    return response.data;
  },

  // Get usage history
  getUsage: async (days: number = 30): Promise<any[]> => {
    const api = createAxiosInstance();
    const response = await api.get(`/subscription/usage?days=${days}`);
    return response.data;
  },
};

export default subscriptionAPI;