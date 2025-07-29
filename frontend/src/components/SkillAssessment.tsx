import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assessmentAPI } from '../api/assessment';
import { theme } from '../styles/theme';
import Button from './common/Button';

interface AssessmentQuestion {
  id: number;
  question_text: string;
  question_type: string;
  options?: string;
  topic_area: string;
  expected_level: number;
}

interface AssessmentAnswer {
  question_id: number;
  answer: string;
  confidence_level?: number;
  time_taken_seconds?: number;
}

interface AssessmentResult {
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

const SkillAssessment: React.FC = () => {
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<AssessmentAnswer[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [confidence, setConfidence] = useState(3);
  const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [showIntro, setShowIntro] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Don't load questions until user starts assessment
  }, []);

  const startAssessment = async () => {
    console.log('Starting assessment...');
    setLoading(true);
    try {
      console.log('Calling assessmentAPI.startAssessment()...');
      const questionsData = await assessmentAPI.startAssessment();
      console.log('Received questions:', questionsData);
      setQuestions(questionsData);
      setShowIntro(false);
      setQuestionStartTime(Date.now());
    } catch (error) {
      console.error('Error starting assessment:', error);
      alert(`Error starting assessment: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = () => {
    if (!currentAnswer.trim()) return;

    const timeTaken = (Date.now() - questionStartTime) / 1000;
    const answer: AssessmentAnswer = {
      question_id: questions[currentQuestionIndex].id,
      answer: currentAnswer,
      confidence_level: confidence,
      time_taken_seconds: timeTaken
    };

    setAnswers([...answers, answer]);
    setCurrentAnswer('');
    setConfidence(3);

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setQuestionStartTime(Date.now());
    } else {
      submitAssessment([...answers, answer]);
    }
  };

  const submitAssessment = async (finalAnswers: AssessmentAnswer[]) => {
    setSubmitting(true);
    try {
      const assessmentResult = await assessmentAPI.submitAssessment({ answers: finalAnswers });
      setResult(assessmentResult);
    } catch (error) {
      console.error('Error submitting assessment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleFinishAssessment = () => {
    navigate('/dashboard');
  };

  if (showIntro) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <div style={headerStyle}>
            <h1 style={titleStyle}>🎯 Skill Assessment</h1>
            <p style={subtitleStyle}>
              Let's determine your C programming level to personalize your learning experience
            </p>
          </div>

          <div style={contentStyle}>
            <div style={infoBoxStyle}>
              <h3 style={{ margin: '0 0 16px 0', color: theme.colors.primary }}>
                What to Expect:
              </h3>
              <ul style={listStyle}>
                <li>15 questions covering C programming fundamentals to advanced topics</li>
                <li>Multiple choice questions testing your knowledge</li>
                <li>Takes about 10-15 minutes to complete</li>
                <li>Your answers help us recommend the right starting level</li>
                <li>You can retake this assessment anytime</li>
              </ul>
            </div>

            <div style={warningBoxStyle}>
              <strong>💡 Tip:</strong> Answer honestly - this helps us create the best learning path for you!
            </div>

            <div style={buttonContainerStyle}>
              <Button
                variant="secondary"
                onClick={() => navigate('/dashboard')}
              >
                Skip Assessment
              </Button>
              <Button
                variant="primary"
                size="lg"
                onClick={startAssessment}
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Start Assessment'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (result) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <div style={headerStyle}>
            <h1 style={titleStyle}>🎉 Assessment Complete!</h1>
            <p style={subtitleStyle}>Here are your personalized results</p>
          </div>

          <div style={contentStyle}>
            <div style={resultStatsStyle}>
              <div style={statBoxStyle}>
                <div style={statValueStyle}>{result.calculated_level}</div>
                <div style={statLabelStyle}>Recommended Level</div>
              </div>
              <div style={statBoxStyle}>
                <div style={statValueStyle}>{result.accuracy_percentage.toFixed(0)}%</div>
                <div style={statLabelStyle}>Accuracy</div>
              </div>
              <div style={statBoxStyle}>
                <div style={statValueStyle}>{result.correct_answers}/{result.total_questions}</div>
                <div style={statLabelStyle}>Correct Answers</div>
              </div>
            </div>

            <div style={skillLevelBoxStyle}>
              <h3 style={{ margin: '0 0 8px 0' }}>Your Skill Level: {formatSkillLevel(result.skill_level)}</h3>
              <p style={{ margin: 0, opacity: 0.8 }}>
                {getSkillLevelDescription(result.skill_level)}
              </p>
            </div>

            <div style={topicBreakdownStyle}>
              <h3 style={{ margin: '0 0 16px 0' }}>Topic Breakdown:</h3>
              <div style={topicGridStyle}>
                {Object.entries(result.topic_breakdown).map(([topic, data]: [string, any]) => (
                  <div key={topic} style={topicCardStyle}>
                    <div style={topicNameStyle}>{formatTopicName(topic)}</div>
                    <div style={topicScoreStyle}>
                      {(data.accuracy * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={recommendationsStyle}>
              <h3 style={{ margin: '0 0 16px 0' }}>Personalized Recommendations:</h3>
              <ul style={listStyle}>
                {result.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>

            <div style={buttonContainerStyle}>
              <Button
                variant="secondary"
                onClick={() => setShowIntro(true)}
              >
                Retake Assessment
              </Button>
              <Button
                variant="primary"
                size="lg"
                onClick={handleFinishAssessment}
              >
                Start Learning!
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading || submitting) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>
              {submitting ? '📊' : '⏳'}
            </div>
            <h2>{submitting ? 'Analyzing Your Responses...' : 'Loading Assessment...'}</h2>
            <p>{submitting ? 'Calculating your skill level' : 'Preparing questions for you'}</p>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <div style={headerStyle}>
          <div style={progressBarContainerStyle}>
            <div style={progressBarStyle}>
              <div style={{ ...progressFillStyle, width: `${progress}%` }}></div>
            </div>
            <span style={progressTextStyle}>
              Question {currentQuestionIndex + 1} of {questions.length}
            </span>
          </div>
        </div>

        <div style={contentStyle}>
          <div style={questionStyle}>
            <div style={topicTagStyle}>
              {formatTopicName(currentQuestion.topic_area)} • Level {currentQuestion.expected_level}
            </div>
            <h2 style={questionTextStyle}>{currentQuestion.question_text}</h2>
          </div>

          {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options ? (
            <div style={optionsContainerStyle}>
              {JSON.parse(currentQuestion.options).map((option: string, index: number) => (
                <button
                  key={index}
                  style={optionButtonStyle(currentAnswer === option)}
                  onClick={() => setCurrentAnswer(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          ) : (
            <input
              type="text"
              style={textInputStyle}
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="Type your answer..."
            />
          )}

          <div style={confidenceStyle}>
            <label style={confidenceLabelStyle}>How confident are you? (1-5)</label>
            <div style={confidenceButtonsStyle}>
              {[1, 2, 3, 4, 5].map((level) => (
                <button
                  key={level}
                  style={confidenceButtonStyle(confidence === level)}
                  onClick={() => setConfidence(level)}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div style={buttonContainerStyle}>
            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={handleAnswerSubmit}
              disabled={!currentAnswer.trim()}
            >
              {currentQuestionIndex === questions.length - 1 ? 'Finish Assessment' : 'Next Question'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions
const formatSkillLevel = (level: string) => {
  return level.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join(' ');
};

const formatTopicName = (topic: string) => {
  const topicMap: Record<string, string> = {
    'basics': 'Basics',
    'variables': 'Variables',
    'operators': 'Operators',
    'loops': 'Loops',
    'functions': 'Functions',
    'arrays': 'Arrays',
    'strings': 'Strings',
    'pointers': 'Pointers',
    'memory': 'Memory Management'
  };
  return topicMap[topic] || topic.charAt(0).toUpperCase() + topic.slice(1);
};

const getSkillLevelDescription = (level: string) => {
  const descriptions: Record<string, string> = {
    'complete_beginner': 'New to programming - perfect place to start your journey!',
    'beginner': 'You know some basics - ready to build on your foundation!',
    'intermediate': 'Good grasp of fundamentals - time for more advanced concepts!',
    'advanced': 'Strong C knowledge - ready for complex topics!',
    'expert': 'Excellent mastery - you can handle the most challenging material!'
  };
  return descriptions[level] || 'Keep learning and growing!';
};

// Styles
const containerStyle = {
  minHeight: '100vh',
  background: theme.colors.gradient,
  padding: '20px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
};

const cardStyle = {
  maxWidth: '800px',
  width: '100%',
  background: theme.colors.surface,
  borderRadius: theme.borderRadius.xl,
  boxShadow: theme.shadows.xl,
  overflow: 'hidden' as const
};

const headerStyle = {
  background: theme.colors.primary,
  color: 'white',
  padding: '30px',
  textAlign: 'center' as const
};

const titleStyle = {
  fontSize: '28px',
  fontWeight: 'bold',
  margin: '0 0 8px 0'
};

const subtitleStyle = {
  fontSize: '16px',
  margin: 0,
  opacity: 0.9
};

const contentStyle = {
  padding: '40px'
};

const infoBoxStyle = {
  background: '#f8f9fa',
  padding: '24px',
  borderRadius: theme.borderRadius.lg,
  marginBottom: '24px'
};

const warningBoxStyle = {
  background: '#fff3cd',
  color: '#856404',
  padding: '16px',
  borderRadius: theme.borderRadius.md,
  marginBottom: '24px'
};

const listStyle = {
  margin: 0,
  paddingLeft: '20px'
};

const buttonContainerStyle = {
  display: 'flex',
  gap: '16px',
  justifyContent: 'center'
};

const progressBarContainerStyle = {
  width: '100%'
};

const progressBarStyle = {
  width: '100%',
  height: '8px',
  background: 'rgba(255, 255, 255, 0.3)',
  borderRadius: '4px',
  overflow: 'hidden' as const,
  marginBottom: '12px'
};

const progressFillStyle = {
  height: '100%',
  background: 'white',
  transition: 'width 0.3s ease'
};

const progressTextStyle = {
  fontSize: '14px',
  opacity: 0.9
};

const questionStyle = {
  marginBottom: '32px'
};

const topicTagStyle = {
  display: 'inline-block',
  background: theme.colors.primaryLight,
  color: theme.colors.primary,
  padding: '4px 12px',
  borderRadius: theme.borderRadius.full,
  fontSize: '12px',
  fontWeight: '600',
  marginBottom: '16px'
};

const questionTextStyle = {
  fontSize: '20px',
  lineHeight: '1.6',
  color: theme.colors.text,
  margin: 0,
  whiteSpace: 'pre-wrap' as const
};

const optionsContainerStyle = {
  display: 'grid',
  gap: '12px',
  marginBottom: '32px'
};

const optionButtonStyle = (isSelected: boolean) => ({
  padding: '16px',
  border: `2px solid ${isSelected ? theme.colors.primary : theme.colors.border}`,
  borderRadius: theme.borderRadius.md,
  background: isSelected ? `${theme.colors.primary}10` : 'white',
  color: theme.colors.text,
  textAlign: 'left' as const,
  cursor: 'pointer',
  fontSize: '16px',
  transition: 'all 0.3s ease',
  whiteSpace: 'pre-wrap' as const
});

const textInputStyle = {
  width: '100%',
  padding: '16px',
  border: `2px solid ${theme.colors.border}`,
  borderRadius: theme.borderRadius.md,
  fontSize: '16px',
  marginBottom: '32px'
};

const confidenceStyle = {
  marginBottom: '32px'
};

const confidenceLabelStyle = {
  display: 'block',
  fontSize: '14px',
  fontWeight: '600',
  color: theme.colors.text,
  marginBottom: '12px'
};

const confidenceButtonsStyle = {
  display: 'flex',
  gap: '8px'
};

const confidenceButtonStyle = (isSelected: boolean) => ({
  width: '40px',
  height: '40px',
  border: `2px solid ${isSelected ? theme.colors.primary : theme.colors.border}`,
  borderRadius: '50%',
  background: isSelected ? theme.colors.primary : 'white',
  color: isSelected ? 'white' : theme.colors.text,
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: '600',
  transition: 'all 0.3s ease'
});

const resultStatsStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(3, 1fr)',
  gap: '20px',
  marginBottom: '32px'
};

const statBoxStyle = {
  textAlign: 'center' as const,
  padding: '20px',
  background: '#f8f9fa',
  borderRadius: theme.borderRadius.lg
};

const statValueStyle = {
  fontSize: '32px',
  fontWeight: 'bold',
  color: theme.colors.primary,
  marginBottom: '8px'
};

const statLabelStyle = {
  fontSize: '14px',
  color: theme.colors.textSecondary
};

const skillLevelBoxStyle = {
  background: theme.colors.primaryLight,
  color: theme.colors.primary,
  padding: '20px',
  borderRadius: theme.borderRadius.lg,
  textAlign: 'center' as const,
  marginBottom: '32px'
};

const topicBreakdownStyle = {
  marginBottom: '32px'
};

const topicGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
  gap: '12px'
};

const topicCardStyle = {
  background: '#f8f9fa',
  padding: '16px',
  borderRadius: theme.borderRadius.md,
  textAlign: 'center' as const
};

const topicNameStyle = {
  fontSize: '12px',
  color: theme.colors.textSecondary,
  marginBottom: '4px'
};

const topicScoreStyle = {
  fontSize: '18px',
  fontWeight: 'bold',
  color: theme.colors.primary
};

const recommendationsStyle = {
  marginBottom: '32px'
};

export default SkillAssessment;