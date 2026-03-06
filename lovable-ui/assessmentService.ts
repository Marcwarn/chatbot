/**
 * Assessment API Service
 * Handles all API communication with GDPR-compliant backend
 */

const API_BASE_URL = import.meta.env.VITE_ASSESSMENT_API_URL || 'http://localhost:8000';

// ============================================================================
// TYPES
// ============================================================================

export interface AssessmentType {
  id: 'big_five' | 'disc' | 'jung_mbti' | 'comprehensive';
  name: string;
  description: string;
  dimensions: number;
  recommended_questions: number;
  estimatedMinutes?: number;
  icon?: string;
}

export interface Question {
  question_id: number;
  question_text: string;
  scale_type: 'likert' | 'choice' | 'open';
  options?: string[];
  dimension: string;
}

export interface StartAssessmentRequest {
  email?: string;
  assessment_type: string;
  language?: string;
  num_questions?: number;
  consent_data_processing: boolean;
  consent_ai_analysis: boolean;
  consent_storage?: boolean;
}

export interface AssessmentQuestions {
  assessment_id: string;
  user_id: string;
  questions: Question[];
  total_questions: number;
  assessment_type: string;
  created_at: string;
  gdpr_notice: string;
}

export interface Answer {
  question_id: number;
  answer: number | string;
}

export interface PersonalityScore {
  dimension: string;
  score: number;
  percentile?: number;
  interpretation: string;
}

export interface AssessmentResult {
  assessment_id: string;
  user_id: string;
  assessment_type: string;
  scores: PersonalityScore[];
  summary: string;
  detailed_analysis: string;
  strengths: string[];
  development_areas: string[];
  recommendations: string[];
  completed_at: string;
  gdpr_notice: string;
}

export interface PrivacyInfo {
  user_id: string;
  consents: any[];
  data_summary: {
    total_assessments: number;
    completed_assessments: number;
    anonymized_assessments: number;
  };
  retention_info: {
    data_retention_days: number;
    delete_after: string;
    days_until_deletion: number;
  };
}

// ============================================================================
// API CLIENT
// ============================================================================

class AssessmentAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; gdpr_compliant: boolean }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) throw new Error('API health check failed');
    return response.json();
  }

  /**
   * Get available assessment types
   */
  async getAssessmentTypes(): Promise<{ assessment_types: AssessmentType[] }> {
    const response = await fetch(`${this.baseUrl}/api/v1/assessment/types`);
    if (!response.ok) throw new Error('Failed to fetch assessment types');
    return response.json();
  }

  /**
   * Start a new assessment
   */
  async startAssessment(
    request: StartAssessmentRequest
  ): Promise<AssessmentQuestions> {
    const response = await fetch(`${this.baseUrl}/api/v1/assessment/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start assessment');
    }

    return response.json();
  }

  /**
   * Submit assessment answers
   */
  async submitAssessment(
    assessmentId: string,
    answers: Answer[]
  ): Promise<AssessmentResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/assessment/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        assessment_id: assessmentId,
        answers: answers.map(a => ({
          assessment_id: assessmentId,
          question_id: a.question_id,
          answer: a.answer,
        })),
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit assessment');
    }

    return response.json();
  }

  /**
   * Get assessment result
   */
  async getResult(assessmentId: string): Promise<AssessmentResult> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/assessment/result/${assessmentId}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get result');
    }

    return response.json();
  }

  /**
   * Get user privacy information
   */
  async getPrivacyInfo(userId: string): Promise<PrivacyInfo> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/gdpr/privacy-info/${userId}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get privacy info');
    }

    return response.json();
  }

  /**
   * Export all user data
   */
  async exportUserData(userId: string, email?: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/gdpr/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to export data');
    }

    return response.json();
  }

  /**
   * Request data deletion
   */
  async requestDeletion(
    userId: string,
    email?: string,
    reason?: string
  ): Promise<{ verification_token: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/v1/gdpr/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, email, reason }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to request deletion');
    }

    return response.json();
  }

  /**
   * Confirm data deletion
   */
  async confirmDeletion(verificationToken: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/gdpr/delete/confirm/${verificationToken}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to confirm deletion');
    }

    return response.json();
  }

  /**
   * Get consent status
   */
  async getConsents(userId: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/gdpr/consent/${userId}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get consents');
    }

    return response.json();
  }

  /**
   * Update consent
   */
  async updateConsent(
    userId: string,
    consentType: string,
    consentGiven: boolean,
    purpose: string
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/gdpr/consent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        consent_type: consentType,
        consent_given: consentGiven,
        purpose,
        legal_basis: 'consent',
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update consent');
    }

    return response.json();
  }
}

// ============================================================================
// SINGLETON EXPORT
// ============================================================================

export const assessmentAPI = new AssessmentAPIClient();

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Download data as JSON file
 */
export function downloadJSON(data: any, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Generate a simple user ID (in real app, use auth)
 */
export function generateUserId(): string {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Save user ID to localStorage
 */
export function saveUserId(userId: string) {
  localStorage.setItem('assessment_user_id', userId);
}

/**
 * Get user ID from localStorage
 */
export function getUserId(): string | null {
  return localStorage.getItem('assessment_user_id');
}

/**
 * Clear user ID from localStorage (on deletion)
 */
export function clearUserId() {
  localStorage.removeItem('assessment_user_id');
}
