import React, { useState, useEffect } from 'react';
import Modal from './common/Modal';
import Button from './common/Button';
import { theme } from '../styles/theme';
import { adminAPI, CreateQuestionRequest, LevelWithLessons } from '../api/admin';

interface AddQuestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onQuestionAdded: () => void;
  selectedLessonId?: number | null;
  initialData?: CreateQuestionRequest | null;
  isEditing?: boolean;
  questionId?: number | null;
}

const AddQuestionModal: React.FC<AddQuestionModalProps> = ({
  isOpen,
  onClose,
  onQuestionAdded,
  selectedLessonId,
  initialData,
  isEditing = false,
  questionId
}) => {
  const [loading, setLoading] = useState(false);
  const [levels, setLevels] = useState<LevelWithLessons[]>([]);
  const [aiGenerating, setAiGenerating] = useState(false);
  
  const [formData, setFormData] = useState<CreateQuestionRequest>({
    lesson_id: selectedLessonId || 0,
    question_text: '',
    question_type: 'multiple_choice',
    correct_answer: '',
    options: '',
    explanation: '',
    code_template: ''
  });

  const [aiFormData, setAiFormData] = useState({
    difficulty: 'beginner' as 'beginner' | 'intermediate' | 'advanced',
    questionType: 'multiple_choice' as 'multiple_choice' | 'coding_exercise' | 'fill_in_blank'
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<'manual' | 'ai'>('manual');

  useEffect(() => {
    if (isOpen) {
      loadLevels();
      if (initialData && isEditing) {
        const normalizedOptions = typeof initialData.options === 'string'
          ? initialData.options
          : Array.isArray((initialData as any).options)
            ? JSON.stringify((initialData as any).options)
            : '';
        setFormData({
          lesson_id: initialData.lesson_id || selectedLessonId || 0,
          question_text: initialData.question_text || '',
          question_type: initialData.question_type || 'multiple_choice',
          correct_answer: initialData.correct_answer || '',
          options: normalizedOptions,
          explanation: initialData.explanation || '',
          code_template: initialData.code_template || ''
        });
      } else {
        setFormData(prev => ({
          ...prev,
          lesson_id: selectedLessonId || 0
        }));
      }
    }
  }, [isOpen, selectedLessonId, initialData, isEditing]);

  const loadLevels = async () => {
    try {
      const levelsData = await adminAPI.getLevelsWithLessons();
      setLevels(levelsData);
    } catch (error) {
      console.error('Error loading levels:', error);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.lesson_id || formData.lesson_id === 0) {
      newErrors.lesson_id = 'Please select a lesson';
    }
    if (!formData.question_text.trim()) {
      newErrors.question_text = 'Question text is required';
    }
    if (!formData.correct_answer.trim()) {
      newErrors.correct_answer = 'Correct answer is required';
    }
    if (formData.question_type === 'multiple_choice') {
      const optionsString = typeof formData.options === 'string'
        ? formData.options
        : Array.isArray((formData as any).options)
          ? JSON.stringify((formData as any).options)
          : '';
      if (!optionsString.trim()) {
        newErrors.options = 'Options are required for multiple choice questions';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const getErrorMessage = (error: any): string => {
    const detail = error?.response?.data?.detail ?? error?.message ?? error;
    if (Array.isArray(detail)) {
      return detail
        .map((d: any) => d?.msg || d?.message || (typeof d === 'string' ? d : JSON.stringify(d)))
        .join(', ');
    }
    if (detail && typeof detail === 'object') {
      return detail.msg || detail.message || JSON.stringify(detail);
    }
    return typeof detail === 'string' ? detail : 'An unexpected error occurred';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      if (isEditing && questionId) {
        await adminAPI.updateQuestion(questionId, formData);
        onQuestionAdded();
        handleClose();
      } else {
        await adminAPI.createQuestion(formData);
        onQuestionAdded();
        handleClose();
      }
    } catch (error: any) {
      console.error('Error saving question:', error);
      setErrors({ submit: getErrorMessage(error) });
    } finally {
      setLoading(false);
    }
  };

  const handleAIGenerate = async () => {
    if (!formData.lesson_id) {
      setErrors({ ai_generate: 'Please select a lesson first' });
      return;
    }

    setAiGenerating(true);
    setErrors({});

    try {
      // Get lesson info for topic
      const selectedLesson = levels.flatMap(l => l.lessons).find(lesson => lesson.id === formData.lesson_id);
      const topic = selectedLesson?.title || 'C Programming';

      const response = await adminAPI.generateAIQuestion(
        formData.lesson_id,
        topic,
        aiFormData.difficulty,
        aiFormData.questionType
      );

      // Populate form with generated question
      const generatedQuestion = response.generated_question;
      const normalizedOptions = typeof generatedQuestion?.options === 'string'
        ? generatedQuestion.options
        : Array.isArray(generatedQuestion?.options)
          ? JSON.stringify(generatedQuestion.options)
          : '';

      setFormData(prev => ({
        ...prev,
        question_text: generatedQuestion.question_text,
        question_type: aiFormData.questionType,
        correct_answer: generatedQuestion.correct_answer,
        options: normalizedOptions,
        explanation: generatedQuestion.explanation || '',
        code_template: generatedQuestion.code_template || ''
      }));

      // Switch to manual tab to show the generated question
      setActiveTab('manual');
      
    } catch (error: any) {
      console.error('Error generating AI question:', error);
      setErrors({ ai_generate: getErrorMessage(error) });
    } finally {
      setAiGenerating(false);
    }
  };

  const handleClose = () => {
    setFormData({
      lesson_id: selectedLessonId || 0,
      question_text: '',
      question_type: 'multiple_choice',
      correct_answer: '',
      options: '',
      explanation: '',
      code_template: ''
    });
    setAiFormData({
      difficulty: 'beginner',
      questionType: 'multiple_choice'
    });
    setErrors({});
    setActiveTab('manual');
    onClose();
  };

  const selectStyle = {
    width: '100%',
    padding: '12px',
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    fontSize: '14px',
    backgroundColor: theme.colors.surface,
    color: theme.colors.text
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    fontSize: '14px',
    backgroundColor: theme.colors.surface,
    color: theme.colors.text
  };

  const textareaStyle = {
    width: '100%',
    padding: '12px',
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    fontSize: '14px',
    backgroundColor: theme.colors.surface,
    color: theme.colors.text,
    resize: 'vertical' as const,
    minHeight: '80px'
  };

  const codeTextareaStyle = {
    ...textareaStyle,
    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
    fontSize: '12px'
  };

  const tabStyle = (isActive: boolean) => ({
    background: isActive ? theme.colors.primary : 'transparent',
    color: isActive ? 'white' : theme.colors.text,
    border: 'none',
    padding: '12px 20px',
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    marginRight: '4px'
  });

  const errorStyle = {
    color: theme.colors.error,
    fontSize: '14px',
    marginTop: '4px'
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose} 
      title={isEditing ? "Edit Question" : "Add New Question"}
      size="lg"
    >
      <div>
        {/* Tab Navigation */}
        <div style={{ marginBottom: '20px', borderBottom: `1px solid ${theme.colors.border}` }}>
          <button
            style={tabStyle(activeTab === 'manual')}
            onClick={() => setActiveTab('manual')}
          >
            Manual Entry
          </button>
          <button
            style={tabStyle(activeTab === 'ai')}
            onClick={() => setActiveTab('ai')}
          >
            AI Generate
          </button>
        </div>

        {activeTab === 'ai' && (
          <div style={{ marginBottom: '24px', padding: '20px', background: theme.colors.primaryLight, borderRadius: theme.borderRadius.md }}>
            <h4 style={{ margin: '0 0 16px 0', color: theme.colors.primary }}>
              🤖 Generate Question with AI
            </h4>
            
            {/* Show selected lesson info */}
            {formData.lesson_id > 0 && (
              <div style={{ 
                marginBottom: '16px', 
                padding: '12px', 
                background: theme.colors.surface, 
                borderRadius: theme.borderRadius.md,
                border: `1px solid ${theme.colors.border}`
              }}>
                <strong style={{ color: theme.colors.text }}>Selected Lesson:</strong> {
                  levels.flatMap(l => l.lessons).find(lesson => lesson.id === formData.lesson_id)?.title || 'Unknown'
                }
              </div>
            )}
            
            {/* Lesson Selection for AI (only if no lesson pre-selected) */}
            {!selectedLessonId && (
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Select Lesson *
                </label>
                <select
                  value={formData.lesson_id}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    lesson_id: parseInt(e.target.value)
                  }))}
                  style={selectStyle}
                >
                  <option value={0}>Choose a lesson first</option>
                  {levels.map(level => 
                    level.lessons.map(lesson => (
                      <option key={lesson.id} value={lesson.id}>
                        Level {level.level_number}: {lesson.title}
                      </option>
                    ))
                  )}
                </select>
                {errors.lesson_id && <div style={errorStyle}>{errors.lesson_id}</div>}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Difficulty
                </label>
                <select
                  value={aiFormData.difficulty}
                  onChange={(e) => setAiFormData(prev => ({ 
                    ...prev, 
                    difficulty: e.target.value as 'beginner' | 'intermediate' | 'advanced'
                  }))}
                  style={selectStyle}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Question Type
                </label>
                <select
                  value={aiFormData.questionType}
                  onChange={(e) => setAiFormData(prev => ({ 
                    ...prev, 
                    questionType: e.target.value as 'multiple_choice' | 'coding_exercise' | 'fill_in_blank'
                  }))}
                  style={selectStyle}
                >
                  <option value="multiple_choice">Multiple Choice</option>
                  <option value="coding_exercise">Coding Exercise</option>
                  <option value="fill_in_blank">Fill in the Blank</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <Button
                onClick={handleAIGenerate}
                disabled={aiGenerating || !formData.lesson_id}
                variant="primary"
                fullWidth
              >
                {aiGenerating ? '🤖 Generating Question...' : '🤖 Generate Question'}
              </Button>
              
              {!formData.lesson_id && (
                <div style={{ 
                  color: theme.colors.textSecondary, 
                  fontSize: '14px', 
                  textAlign: 'center', 
                  marginTop: '8px' 
                }}>
                  Please select a lesson first
                </div>
              )}
            </div>

            {errors.ai_generate && (
              <div style={{ ...errorStyle, marginBottom: '16px' }}>
                {errors.ai_generate}
              </div>
            )}
            
            <div style={{ 
              padding: '12px', 
              background: 'rgba(255,255,255,0.8)', 
              borderRadius: theme.borderRadius.sm,
              fontSize: '14px',
              color: theme.colors.textSecondary,
              textAlign: 'center'
            }}>
              💡 AI will generate a question based on the lesson content and your preferences
            </div>
          </div>
        )}

        {/* Only show manual form when manual tab is active */}
        {activeTab === 'manual' && (
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                Lesson *
              </label>
              <select
                value={formData.lesson_id}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  lesson_id: parseInt(e.target.value)
                }))}
                style={selectStyle}
                disabled={!!selectedLessonId}
              >
                <option value={0}>Select a lesson</option>
                {levels.map(level => 
                  level.lessons.map(lesson => (
                    <option key={lesson.id} value={lesson.id}>
                      Level {level.level_number}: {lesson.title}
                    </option>
                  ))
                )}
              </select>
              {errors.lesson_id && <div style={errorStyle}>{errors.lesson_id}</div>}
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                Question Type *
              </label>
              <select
                value={formData.question_type}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  question_type: e.target.value as CreateQuestionRequest['question_type']
                }))}
                style={selectStyle}
              >
                <option value="multiple_choice">Multiple Choice</option>
                <option value="coding_exercise">Coding Exercise</option>
                <option value="fill_in_blank">Fill in the Blank</option>
              </select>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                Question Text *
              </label>
              <textarea
                value={formData.question_text}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  question_text: e.target.value 
                }))}
                placeholder="Enter your question..."
                style={textareaStyle}
                rows={4}
              />
              {errors.question_text && <div style={errorStyle}>{errors.question_text}</div>}
            </div>

            {formData.question_type === 'multiple_choice' && (
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Options * (JSON format: ["Option A", "Option B", "Option C", "Option D"])
                </label>
                <textarea
                  value={formData.options}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    options: e.target.value 
                  }))}
                  placeholder='["Option A", "Option B", "Option C", "Option D"]'
                  style={codeTextareaStyle}
                  rows={3}
                />
                {errors.options && <div style={errorStyle}>{errors.options}</div>}
              </div>
            )}

            {formData.question_type === 'coding_exercise' && (
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Code Template
                </label>
                <textarea
                  value={formData.code_template}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    code_template: e.target.value 
                  }))}
                  placeholder="#include <stdio.h>&#10;&#10;int main() {&#10;    // TODO: Your code here&#10;    return 0;&#10;}"
                  style={codeTextareaStyle}
                  rows={6}
                />
              </div>
            )}

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                Correct Answer *
              </label>
              <input
                type="text"
                value={formData.correct_answer}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  correct_answer: e.target.value 
                }))}
                placeholder="Enter the correct answer..."
                style={inputStyle}
              />
              {errors.correct_answer && <div style={errorStyle}>{errors.correct_answer}</div>}
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                Explanation (optional)
              </label>
              <textarea
                value={formData.explanation}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  explanation: e.target.value 
                }))}
                placeholder="Explain why this is the correct answer..."
                style={textareaStyle}
                rows={3}
              />
            </div>

            {errors.submit && (
              <div style={{ ...errorStyle, marginBottom: '16px', padding: '12px', background: '#fee', borderRadius: theme.borderRadius.md }}>
                {errors.submit}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={loading}
              >
                {loading ? (isEditing ? 'Updating...' : 'Creating...') : (isEditing ? 'Update Question' : 'Create Question')}
              </Button>
            </div>
          </form>
        )}
      </div>
    </Modal>
  );
};

export default AddQuestionModal;