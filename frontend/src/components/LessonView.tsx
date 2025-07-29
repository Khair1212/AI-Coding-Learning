import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { learningAPI, Question } from '../api/learning';
import { theme } from '../styles/theme';
import Button from './common/Button';

const LessonView: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (lessonId) {
      fetchQuestions(parseInt(lessonId));
    }
  }, [lessonId]);

  const fetchQuestions = async (lessonId: number) => {
    try {
      const questionsData = await learningAPI.getLessonQuestions(lessonId);
      setQuestions(questionsData);
    } catch (error) {
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!userAnswer.trim()) return;

    setSubmitting(true);
    try {
      const submission = {
        question_id: questions[currentQuestionIndex].id,
        answer: userAnswer
      };
      
      const submissionResult = await learningAPI.submitAnswer(submission);
      setResult(submissionResult);
      setShowResult(true);
    } catch (error) {
      console.error('Error submitting answer:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setUserAnswer('');
      setShowResult(false);
      setResult(null);
    } else {
      // Lesson completed
      navigate('/dashboard');
    }
  };

  const handleBackToMap = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading lesson...</div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>No questions available for this lesson.</div>
        <Button onClick={handleBackToMap} style={{ marginTop: '20px' }}>
          Back to Map
        </Button>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  const containerStyle = {
    minHeight: '100vh',
    background: theme.colors.gradient,
    padding: '20px'
  };

  const lessonCardStyle = {
    maxWidth: '800px',
    margin: '0 auto',
    background: theme.colors.surface,
    borderRadius: theme.borderRadius.xl,
    boxShadow: theme.shadows.xl,
    overflow: 'hidden' as const
  };

  const headerStyle = {
    background: theme.colors.primary,
    color: 'white',
    padding: '20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between'
  };

  const progressBarStyle = {
    width: '100%',
    height: '8px',
    background: 'rgba(255, 255, 255, 0.3)',
    borderRadius: '4px',
    overflow: 'hidden' as const,
    margin: '12px 0'
  };

  const progressFillStyle = {
    height: '100%',
    background: 'white',
    width: `${progress}%`,
    transition: 'width 0.3s ease'
  };

  const contentStyle = {
    padding: '40px'
  };

  const questionStyle = {
    fontSize: '20px',
    lineHeight: '1.6',
    color: theme.colors.text,
    marginBottom: '30px'
  };

  const codeBlockStyle = {
    background: '#f8f9fa',
    border: '1px solid #e9ecef',
    borderRadius: theme.borderRadius.md,
    padding: '20px',
    fontFamily: 'Monaco, Consolas, monospace',
    fontSize: '14px',
    lineHeight: '1.5',
    marginBottom: '20px',
    overflow: 'auto' as const
  };

  const answerInputStyle = {
    width: '100%',
    minHeight: currentQuestion.question_type === 'coding_exercise' ? '200px' : '50px',
    padding: '16px',
    border: `2px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    fontSize: '16px',
    fontFamily: currentQuestion.question_type === 'coding_exercise' ? 
                'Monaco, Consolas, monospace' : 'inherit',
    marginBottom: '20px',
    resize: 'vertical' as const
  };

  const optionsStyle = {
    display: 'grid',
    gap: '12px',
    marginBottom: '20px'
  };

  const optionButtonStyle = (isSelected: boolean) => ({
    padding: '16px',
    border: `2px solid ${isSelected ? theme.colors.primary : theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    background: isSelected ? `${theme.colors.primary}10` : 'white',
    color: theme.colors.text,
    textAlign: 'left' as const,
    cursor: 'pointer',
    transition: 'all 0.3s ease'
  });

  const resultCardStyle = (isCorrect: boolean) => ({
    background: isCorrect ? '#d4edda' : '#f8d7da',
    border: `1px solid ${isCorrect ? '#c3e6cb' : '#f5c6cb'}`,
    color: isCorrect ? '#155724' : '#721c24',
    padding: '20px',
    borderRadius: theme.borderRadius.md,
    marginBottom: '20px'
  });

  const buttonContainerStyle = {
    display: 'flex',
    gap: '16px',
    justifyContent: 'space-between'
  };

  const renderQuestionInput = () => {
    if (currentQuestion.question_type === 'multiple_choice' && currentQuestion.options) {
      const options = JSON.parse(currentQuestion.options);
      return (
        <div style={optionsStyle}>
          {options.map((option: string, index: number) => (
            <div
              key={index}
              style={optionButtonStyle(userAnswer === option)}
              onClick={() => setUserAnswer(option)}
            >
              {option}
            </div>
          ))}
        </div>
      );
    }

    if (currentQuestion.question_type === 'coding_exercise') {
      return (
        <div>
          {currentQuestion.code_template && (
            <div>
              <h4>Template:</h4>
              <pre style={codeBlockStyle}>
                {currentQuestion.code_template}
              </pre>
            </div>
          )}
          <textarea
            style={answerInputStyle}
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            placeholder="Write your C code here..."
          />
        </div>
      );
    }

    return (
      <input
        type="text"
        style={answerInputStyle}
        value={userAnswer}
        onChange={(e) => setUserAnswer(e.target.value)}
        placeholder="Type your answer..."
      />
    );
  };

  return (
    <div style={containerStyle}>
      <div style={lessonCardStyle}>
        <div style={headerStyle}>
          <div>
            <h2 style={{ margin: 0 }}>Question {currentQuestionIndex + 1} of {questions.length}</h2>
            <div style={progressBarStyle}>
              <div style={progressFillStyle}></div>
            </div>
          </div>
          <button
            onClick={handleBackToMap}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: 'none',
              color: 'white',
              padding: '8px 16px',
              borderRadius: theme.borderRadius.md,
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>

        <div style={contentStyle}>
          <div style={questionStyle}>
            {currentQuestion.question_text}
          </div>

          {!showResult && (
            <>
              {renderQuestionInput()}
              <div style={buttonContainerStyle}>
                <Button
                  variant="secondary"
                  onClick={handleBackToMap}
                >
                  Back to Map
                </Button>
                <Button
                  variant="primary"
                  onClick={handleSubmitAnswer}
                  disabled={!userAnswer.trim() || submitting}
                >
                  {submitting ? 'Checking...' : 'Submit Answer'}
                </Button>
              </div>
            </>
          )}

          {showResult && result && (
            <>
              <div style={resultCardStyle(result.correct)}>
                <h3 style={{ margin: '0 0 12px 0' }}>
                  {result.correct ? '🎉 Correct!' : '❌ Incorrect'}
                </h3>
                <p style={{ margin: '0 0 12px 0' }}>
                  {result.explanation}
                </p>
                {result.correct && result.xp_earned > 0 && (
                  <p style={{ margin: 0, fontWeight: 'bold' }}>
                    +{result.xp_earned} XP earned!
                  </p>
                )}
              </div>
              <div style={buttonContainerStyle}>
                <Button
                  variant="secondary"
                  onClick={handleBackToMap}
                >
                  Back to Map
                </Button>
                <Button
                  variant="primary"
                  onClick={handleNextQuestion}
                >
                  {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Complete Lesson'}
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default LessonView;