import React, { useState, useEffect } from 'react';
import Modal from './common/Modal';
import Button from './common/Button';
import { theme } from '../styles/theme';
import { AdminQuestion, adminAPI } from '../api/admin';

interface QuestionsListModalProps {
  isOpen: boolean;
  onClose: () => void;
  lessonId: number | null;
  lessonTitle?: string;
  onQuestionClick: (question: AdminQuestion) => void;
  onAddQuestion: (lessonId: number) => void;
  onDeleteQuestion: (questionId: number) => void;
}

const QuestionsListModal: React.FC<QuestionsListModalProps> = ({
  isOpen,
  onClose,
  lessonId,
  lessonTitle,
  onQuestionClick,
  onAddQuestion,
  onDeleteQuestion
}) => {
  const [questions, setQuestions] = useState<AdminQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);

  useEffect(() => {
    if (isOpen && lessonId) {
      loadQuestions();
    }
  }, [isOpen, lessonId]);

  const loadQuestions = async () => {
    if (!lessonId) return;
    
    setLoading(true);
    try {
      const questionsData = await adminAPI.getQuestions(lessonId);
      setQuestions(questionsData);
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (questionId: number) => {
    try {
      await adminAPI.deleteQuestion(questionId);
      setQuestions(questions.filter(q => q.id !== questionId));
      setDeleteConfirmId(null);
      onDeleteQuestion(questionId);
    } catch (error) {
      console.error('Error deleting question:', error);
    }
  };

  const cardStyle = {
    background: theme.colors.surface,
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    padding: '16px',
    marginBottom: '12px',
    transition: 'all 0.2s ease',
    cursor: 'pointer'
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    paddingBottom: '12px',
    borderBottom: `1px solid ${theme.colors.border}`
  };

  if (!lessonId) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      title={`Questions - ${lessonTitle || `Lesson ${lessonId}`}`}
      size="lg"
    >
      <div>
        <div style={headerStyle}>
          <div>
            <span style={{ 
              color: theme.colors.textSecondary, 
              fontSize: '14px' 
            }}>
              {questions.length} question{questions.length !== 1 ? 's' : ''} found
            </span>
          </div>
          <Button
            variant="primary"
            onClick={() => onAddQuestion(lessonId)}
          >
            + Add Question
          </Button>
        </div>

        {loading ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px',
            color: theme.colors.textSecondary 
          }}>
            Loading questions...
          </div>
        ) : questions.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px',
            color: theme.colors.textSecondary 
          }}>
            <div style={{ marginBottom: '16px', fontSize: '18px' }}>
              📝 No questions yet
            </div>
            <p>This lesson doesn't have any questions yet. Click "Add Question" to create the first one.</p>
          </div>
        ) : (
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            {questions.map((question) => (
              <div 
                key={question.id}
                style={cardStyle}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = theme.colors.surfaceHover;
                  e.currentTarget.style.borderColor = theme.colors.primary;
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = theme.colors.surface;
                  e.currentTarget.style.borderColor = theme.colors.border;
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '12px'
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px',
                      marginBottom: '8px'
                    }}>
                      <span style={{
                        background: theme.colors.primary,
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: theme.borderRadius.sm,
                        fontSize: '11px',
                        fontWeight: '500'
                      }}>
                        {question.question_type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span style={{ 
                        fontSize: '12px', 
                        color: theme.colors.textSecondary 
                      }}>
                        ID: {question.id}
                      </span>
                    </div>
                    
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      color: theme.colors.text,
                      marginBottom: '8px',
                      lineHeight: '1.4'
                    }}>
                      {question.question_text.length > 120 
                        ? question.question_text.substring(0, 120) + '...' 
                        : question.question_text
                      }
                    </div>
                    
                    <div style={{ 
                      fontSize: '12px', 
                      color: theme.colors.textSecondary,
                      background: theme.colors.surfaceHover,
                      padding: '6px 10px',
                      borderRadius: theme.borderRadius.sm,
                      display: 'inline-block'
                    }}>
                      <strong>Answer:</strong> {question.correct_answer.length > 40 
                        ? question.correct_answer.substring(0, 40) + '...' 
                        : question.correct_answer
                      }
                    </div>
                  </div>
                  
                  <div style={{ 
                    marginLeft: '12px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px'
                  }}>
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={(e: React.MouseEvent<HTMLButtonElement>) => {
                        e.stopPropagation();
                        onQuestionClick(question);
                      }}
                      style={{ 
                        minWidth: 'auto',
                        padding: '6px 12px',
                        fontSize: '12px'
                      }}
                    >
                      ✏️ Edit
                    </Button>
                    
                    {deleteConfirmId === question.id ? (
                      <div 
                        style={{ display: 'flex', gap: '6px' }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => handleDelete(question.id)}
                          style={{ 
                            backgroundColor: theme.colors.error,
                            minWidth: 'auto',
                            padding: '6px 12px',
                            fontSize: '12px'
                          }}
                        >
                          Delete
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setDeleteConfirmId(null)}
                          style={{ 
                            minWidth: 'auto', 
                            padding: '6px 12px',
                            fontSize: '12px'
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e: React.MouseEvent<HTMLButtonElement>) => {
                          e.stopPropagation();
                          setDeleteConfirmId(question.id);
                        }}
                        style={{ 
                          color: theme.colors.error, 
                          borderColor: theme.colors.error,
                          minWidth: 'auto',
                          padding: '6px 12px',
                          fontSize: '12px'
                        }}
                      >
                        🗑️
                      </Button>
                    )}
                  </div>
                </div>
                
                {question.code_template && (
                  <div style={{
                    background: '#f8f9fa',
                    padding: '8px',
                    borderRadius: theme.borderRadius.sm,
                    fontSize: '12px',
                    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                    color: '#666',
                    marginTop: '8px',
                    borderLeft: `3px solid ${theme.colors.primary}`
                  }}>
                    <div style={{ marginBottom: '4px', fontSize: '11px', fontWeight: '500' }}>
                      Code Template:
                    </div>
                    {question.code_template.length > 100
                      ? question.code_template.substring(0, 100) + '...'
                      : question.code_template
                    }
                  </div>
                )}
                
                <div style={{
                  fontSize: '12px',
                  color: theme.colors.primary,
                  marginTop: '8px',
                  fontStyle: 'italic',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  <span>Click "Edit" to view details and modify →</span>
                </div>
              </div>
            ))}
          </div>
        )}
        
        <div style={{ 
          marginTop: '20px', 
          paddingTop: '12px',
          borderTop: `1px solid ${theme.colors.border}`,
          textAlign: 'right'
        }}>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default QuestionsListModal;