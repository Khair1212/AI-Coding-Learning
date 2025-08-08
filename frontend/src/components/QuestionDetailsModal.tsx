import React, { useState } from 'react';
import Modal from './common/Modal';
import Button from './common/Button';
import { theme } from '../styles/theme';
import { AdminQuestion } from '../api/admin';

interface QuestionDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  question: AdminQuestion | null;
  onDelete: (questionId: number) => void;
  onEdit: (question: AdminQuestion) => void;
}

const QuestionDetailsModal: React.FC<QuestionDetailsModalProps> = ({
  isOpen,
  onClose,
  question,
  onDelete,
  onEdit
}) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (!question) return null;

  const handleDelete = () => {
    onDelete(question.id);
    setShowDeleteConfirm(false);
    onClose();
  };

  const handleEdit = () => {
    onEdit(question);
    onClose();
  };

  const cardStyle = {
    background: theme.colors.surfaceHover,
    padding: '16px',
    borderRadius: theme.borderRadius.md,
    marginBottom: '16px',
    border: `1px solid ${theme.colors.border}`
  };

  const labelStyle = {
    fontWeight: '600',
    color: theme.colors.text,
    display: 'block',
    marginBottom: '8px'
  };

  const valueStyle = {
    color: theme.colors.textSecondary,
    lineHeight: '1.5'
  };

  const codeStyle = {
    background: '#f8f9fa',
    padding: '12px',
    borderRadius: theme.borderRadius.sm,
    fontSize: '14px',
    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
    whiteSpace: 'pre-wrap' as const,
    overflow: 'auto',
    border: `1px solid ${theme.colors.border}`
  };

  const parseOptions = (optionsStr: string | undefined) => {
    if (!optionsStr) return [];
    try {
      return JSON.parse(optionsStr);
    } catch {
      return [];
    }
  };

  const options = parseOptions(question.options);

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      title={`Question Details (ID: ${question.id})`}
      size="lg"
    >
      <div>
        {/* Question Type Badge */}
        <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{
            background: theme.colors.primary,
            color: 'white',
            padding: '6px 12px',
            borderRadius: theme.borderRadius.full,
            fontSize: '14px',
            fontWeight: '500'
          }}>
            {question.question_type.replace('_', ' ').toUpperCase()}
          </span>
          <span style={{ color: theme.colors.textSecondary, fontSize: '14px' }}>
            Lesson ID: {question.lesson_id}
          </span>
        </div>

        {/* Question Text */}
        <div style={cardStyle}>
          <label style={labelStyle}>Question:</label>
          <div style={valueStyle}>{question.question_text}</div>
        </div>

        {/* Correct Answer */}
        <div style={cardStyle}>
          <label style={labelStyle}>Correct Answer:</label>
          <div style={{ 
            ...valueStyle, 
            background: '#e8f5e8', 
            padding: '8px 12px', 
            borderRadius: theme.borderRadius.sm,
            color: '#2d5016',
            fontWeight: '500'
          }}>
            {question.correct_answer}
          </div>
        </div>

        {/* Options (for multiple choice) */}
        {question.question_type === 'multiple_choice' && options.length > 0 && (
          <div style={cardStyle}>
            <label style={labelStyle}>Answer Options:</label>
            <div style={{ display: 'grid', gap: '8px' }}>
              {options.map((option: string, index: number) => (
                <div key={index} style={{
                  padding: '8px 12px',
                  background: theme.colors.surface,
                  borderRadius: theme.borderRadius.sm,
                  border: `1px solid ${theme.colors.border}`
                }}>
                  <span style={{ fontWeight: '500', marginRight: '8px' }}>
                    {String.fromCharCode(65 + index)}.
                  </span>
                  {option}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Code Template */}
        {question.code_template && (
          <div style={cardStyle}>
            <label style={labelStyle}>Code Template:</label>
            <pre style={codeStyle}>{question.code_template}</pre>
          </div>
        )}

        {/* Explanation */}
        {question.explanation && (
          <div style={cardStyle}>
            <label style={labelStyle}>Explanation:</label>
            <div style={valueStyle}>{question.explanation}</div>
          </div>
        )}

        {/* Actions */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: '24px',
          padding: '16px 0',
          borderTop: `1px solid ${theme.colors.border}`
        }}>
          <div>
            {showDeleteConfirm ? (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ color: theme.colors.error, fontSize: '14px', marginRight: '8px' }}>
                  Are you sure?
                </span>
                <Button
                  size="sm"
                  variant="primary"
                  onClick={handleDelete}
                  style={{ backgroundColor: theme.colors.error }}
                >
                  Yes, Delete
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  Cancel
                </Button>
              </div>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowDeleteConfirm(true)}
                style={{ color: theme.colors.error, borderColor: theme.colors.error }}
              >
                🗑️ Delete Question
              </Button>
            )}
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            <Button
              variant="outline"
              onClick={onClose}
            >
              Close
            </Button>
            <Button
              variant="primary"
              onClick={handleEdit}
            >
              ✏️ Edit Question
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default QuestionDetailsModal;