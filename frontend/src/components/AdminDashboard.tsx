import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { theme } from '../styles/theme';
import { adminAPI, AdminStats, AdminUser, LevelWithLessons, AdminQuestion, CreateQuestionRequest } from '../api/admin';
import Button from './common/Button';
import AddQuestionModal from './AddQuestionModal';
import QuestionDetailsModal from './QuestionDetailsModal';
import QuestionsListModal from './QuestionsListModal';

type TabType = 'overview' | 'users' | 'analytics' | 'content';

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [levels, setLevels] = useState<LevelWithLessons[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddQuestionModal, setShowAddQuestionModal] = useState(false);
  const [selectedLessonId, setSelectedLessonId] = useState<number | null>(null);
  const [selectedQuestion, setSelectedQuestion] = useState<AdminQuestion | null>(null);
  const [showQuestionDetailsModal, setShowQuestionDetailsModal] = useState(false);
  const [showQuestionsListModal, setShowQuestionsListModal] = useState(false);
  const [selectedLessonTitle, setSelectedLessonTitle] = useState<string>('');
  const [formData, setFormData] = useState<CreateQuestionRequest>({
    lesson_id: 0,
    question_text: '',
    question_type: 'multiple_choice',
    correct_answer: '',
    options: '',
    explanation: '',
    code_template: ''
  });

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    if (activeTab === 'users') {
      loadUsers();
    } else if (activeTab === 'content') {
      loadLevels();
    }
  }, [activeTab]);

  const loadStats = async () => {
    try {
      const statsData = await adminAPI.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadUsers = async () => {
    try {
      setLoading(true);
      const usersData = await adminAPI.getUsers();
      setUsers(usersData);
    } catch (error) {
      console.error('Error loading users:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadLevels = async () => {
    try {
      setLoading(true);
      const levelsData = await adminAPI.getLevelsWithLessons();
      setLevels(levelsData);
    } catch (error) {
      console.error('Error loading levels:', error);
    } finally {
      setLoading(false);
    }
  };


  const toggleUserStatus = async (userId: number, currentStatus: boolean) => {
    try {
      await adminAPI.updateUser(userId, { is_active: !currentStatus });
      loadUsers(); // Reload users
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const deleteQuestion = async (questionId: number) => {
    // Reload levels to update question counts
    loadLevels();
  };

  const handleQuestionAdded = () => {
    // Reload levels to get updated question counts
    loadLevels();
  };

  const handleViewQuestions = (lessonId: number, lessonTitle: string) => {
    setSelectedLessonId(lessonId);
    setSelectedLessonTitle(lessonTitle);
    setShowQuestionsListModal(true);
  };

  const handleQuestionClick = (question: AdminQuestion) => {
    setSelectedQuestion(question);
    setShowQuestionDetailsModal(true);
    setShowQuestionsListModal(false);
  };

  const handleQuestionEdit = (question: AdminQuestion) => {
    // Populate form data with question for editing
    setFormData({
      lesson_id: question.lesson_id,
      question_text: question.question_text,
      question_type: question.question_type as 'multiple_choice' | 'coding_exercise' | 'fill_in_blank',
      correct_answer: question.correct_answer,
      options: question.options || '',
      explanation: question.explanation || '',
      code_template: question.code_template || ''
    });
    setSelectedQuestion(question);
    setShowQuestionDetailsModal(false);
    setShowAddQuestionModal(true);
  };

  const handleAddQuestionFromList = (lessonId: number) => {
    setSelectedLessonId(lessonId);
    setShowQuestionsListModal(false);
    setShowAddQuestionModal(true);
  };

  const containerStyle = {
    minHeight: '100vh',
    background: theme.colors.background
  };

  const headerStyle = {
    background: theme.colors.surface,
    boxShadow: theme.shadows.sm,
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  };

  const titleStyle = {
    fontSize: '28px',
    fontWeight: 'bold',
    color: theme.colors.text,
    margin: 0
  };

  const tabsStyle = {
    display: 'flex',
    gap: '4px',
    background: theme.colors.surface,
    padding: '4px',
    borderRadius: theme.borderRadius.lg,
    marginBottom: '24px',
    margin: '0 20px'
  };

  const tabButtonStyle = (isActive: boolean) => ({
    padding: '12px 24px',
    border: 'none',
    background: isActive ? theme.colors.primary : 'transparent',
    color: isActive ? 'white' : theme.colors.text,
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.2s ease'
  });

  const contentStyle = {
    padding: '0 20px'
  };

  const cardStyle = {
    background: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: '24px',
    boxShadow: theme.shadows.sm,
    marginBottom: '20px'
  };

  const statsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '30px'
  };

  const statCardStyle = {
    ...cardStyle,
    textAlign: 'center' as const
  };

  const statNumberStyle = {
    fontSize: '32px',
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: '8px'
  };

  const statLabelStyle = {
    fontSize: '14px',
    color: theme.colors.textSecondary,
    fontWeight: '500'
  };

  const renderOverview = () => (
    <div>
      {stats && (
        <>
          <div style={statsGridStyle}>
            <div style={statCardStyle}>
              <div style={statNumberStyle}>{stats.total_users}</div>
              <div style={statLabelStyle}>Total Users</div>
            </div>
            <div style={statCardStyle}>
              <div style={statNumberStyle}>{stats.active_users}</div>
              <div style={statLabelStyle}>Active Users</div>
            </div>
            <div style={statCardStyle}>
              <div style={statNumberStyle}>{stats.total_lessons_completed}</div>
              <div style={statLabelStyle}>Lessons Completed</div>
            </div>
            <div style={statCardStyle}>
              <div style={statNumberStyle}>{stats.total_assessments}</div>
              <div style={statLabelStyle}>Assessments Taken</div>
            </div>
            <div style={statCardStyle}>
              <div style={statNumberStyle}>{stats.average_accuracy}%</div>
              <div style={statLabelStyle}>Average Accuracy</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={cardStyle}>
              <h3 style={{ color: theme.colors.text, marginBottom: '16px' }}>Popular Levels</h3>
              {stats.popular_levels.map((level, idx) => (
                <div key={idx} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: idx < stats.popular_levels.length - 1 ? `1px solid ${theme.colors.border}` : 'none'
                }}>
                  <span style={{ color: theme.colors.text }}>
                    Level {level.level}: {level.title}
                  </span>
                  <span style={{ 
                    color: theme.colors.primary, 
                    fontWeight: '600',
                    background: theme.colors.primaryLight,
                    padding: '4px 8px',
                    borderRadius: theme.borderRadius.sm
                  }}>
                    {level.completions}
                  </span>
                </div>
              ))}
            </div>

            <div style={cardStyle}>
              <h3 style={{ color: theme.colors.text, marginBottom: '16px' }}>Recent Registrations</h3>
              {stats.recent_registrations.slice(0, 5).map((user, idx) => (
                <div key={idx} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: idx < 4 ? `1px solid ${theme.colors.border}` : 'none'
                }}>
                  <div>
                    <div style={{ color: theme.colors.text, fontWeight: '500' }}>
                      {user.username}
                    </div>
                    <div style={{ color: theme.colors.textSecondary, fontSize: '14px' }}>
                      {user.email}
                    </div>
                  </div>
                  <div style={{ color: theme.colors.textSecondary, fontSize: '12px' }}>
                    {new Date(user.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderUsers = () => (
    <div style={cardStyle}>
      <h2 style={{ color: theme.colors.text, marginBottom: '20px' }}>User Management</h2>
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading users...</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: `2px solid ${theme.colors.border}` }}>
                <th style={{ padding: '12px', textAlign: 'left', color: theme.colors.text }}>ID</th>
                <th style={{ padding: '12px', textAlign: 'left', color: theme.colors.text }}>Username</th>
                <th style={{ padding: '12px', textAlign: 'left', color: theme.colors.text }}>Email</th>
                <th style={{ padding: '12px', textAlign: 'left', color: theme.colors.text }}>Role</th>
                <th style={{ padding: '12px', textAlign: 'left', color: theme.colors.text }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', color: theme.colors.text }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                  <td style={{ padding: '12px', color: theme.colors.text }}>{user.id}</td>
                  <td style={{ padding: '12px', color: theme.colors.text }}>{user.username}</td>
                  <td style={{ padding: '12px', color: theme.colors.text }}>{user.email}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      background: user.role === 'admin' ? theme.colors.warning : theme.colors.success,
                      color: 'white',
                      padding: '4px 8px',
                      borderRadius: theme.borderRadius.sm,
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      {user.role}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      background: user.is_active ? theme.colors.success : theme.colors.error,
                      color: 'white',
                      padding: '4px 8px',
                      borderRadius: theme.borderRadius.sm,
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <Button
                      size="sm"
                      variant={user.is_active ? 'outline' : 'secondary'}
                      onClick={() => toggleUserStatus(user.id, user.is_active)}
                    >
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderContent = () => (
    <div style={cardStyle}>
      <h2 style={{ color: theme.colors.text, marginBottom: '20px' }}>Content Management</h2>
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading content...</div>
      ) : (
        <div>
          {levels.map((level) => (
            <div key={level.id} style={{ 
              marginBottom: '24px',
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              overflow: 'hidden'
            }}>
              <div style={{ 
                background: theme.colors.primaryLight,
                padding: '16px',
                borderBottom: `1px solid ${theme.colors.border}`
              }}>
                <h3 style={{ 
                  color: theme.colors.primary,
                  margin: 0,
                  fontSize: '18px',
                  fontWeight: '600'
                }}>
                  Level {level.level_number}: {level.title}
                </h3>
                <p style={{ 
                  color: theme.colors.textSecondary,
                  margin: '4px 0 0 0',
                  fontSize: '14px'
                }}>
                  {level.description}
                </p>
              </div>
              <div style={{ padding: '16px' }}>
                <div style={{ display: 'grid', gap: '12px' }}>
                  {level.lessons.map((lesson) => (
                    <div key={lesson.id} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '12px',
                      background: theme.colors.surfaceHover,
                      borderRadius: theme.borderRadius.sm
                    }}>
                      <div>
                        <div style={{ 
                          color: theme.colors.text,
                          fontWeight: '500',
                          marginBottom: '4px'
                        }}>
                          {lesson.title}
                        </div>
                        <div style={{
                          color: theme.colors.textSecondary,
                          fontSize: '12px'
                        }}>
                          {lesson.lesson_type} • {lesson.difficulty} • {lesson.question_count} questions
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleViewQuestions(lesson.id, lesson.title)}
                        >
                          View Questions ({lesson.question_count})
                        </Button>
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => {
                            setSelectedLessonId(lesson.id);
                            setShowAddQuestionModal(true);
                          }}
                        >
                          Add Question
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
          
        </div>
      )}
    </div>
  );


  return (
    <div style={containerStyle}>
      <header style={headerStyle}>
        <h1 style={titleStyle}>Admin Dashboard</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: theme.colors.text }}>Welcome, {user?.username}!</span>
          <Button onClick={logout} style={{ backgroundColor: '#dc3545' }}>
            Logout
          </Button>
        </div>
      </header>

      <div style={tabsStyle}>
        {(['overview', 'users', 'content', 'analytics'] as TabType[]).map((tab) => (
          <button
            key={tab}
            style={tabButtonStyle(activeTab === tab)}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div style={contentStyle}>
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'users' && renderUsers()}
        {activeTab === 'content' && renderContent()}
        {activeTab === 'analytics' && (
          <div style={cardStyle}>
            <h2>Advanced Analytics</h2>
            <p>Coming soon - detailed analytics and reporting features</p>
          </div>
        )}
      </div>

      <AddQuestionModal
        isOpen={showAddQuestionModal}
        onClose={() => {
          setShowAddQuestionModal(false);
          setSelectedQuestion(null);
        }}
        onQuestionAdded={handleQuestionAdded}
        selectedLessonId={selectedLessonId}
        initialData={selectedQuestion ? {
          lesson_id: selectedQuestion.lesson_id,
          question_text: selectedQuestion.question_text,
          question_type: selectedQuestion.question_type as 'multiple_choice' | 'coding_exercise' | 'fill_in_blank',
          correct_answer: selectedQuestion.correct_answer,
          options: selectedQuestion.options || '',
          explanation: selectedQuestion.explanation || '',
          code_template: selectedQuestion.code_template || ''
        } : null}
        isEditing={!!selectedQuestion}
        questionId={selectedQuestion?.id || null}
      />
      
      <QuestionsListModal
        isOpen={showQuestionsListModal}
        onClose={() => {
          setShowQuestionsListModal(false);
          setSelectedLessonId(null);
          setSelectedLessonTitle('');
        }}
        lessonId={selectedLessonId}
        lessonTitle={selectedLessonTitle}
        onQuestionClick={handleQuestionClick}
        onAddQuestion={handleAddQuestionFromList}
        onDeleteQuestion={deleteQuestion}
      />
      
      <QuestionDetailsModal
        isOpen={showQuestionDetailsModal}
        onClose={() => {
          setShowQuestionDetailsModal(false);
          setSelectedQuestion(null);
        }}
        question={selectedQuestion}
        onDelete={deleteQuestion}
        onEdit={handleQuestionEdit}
      />
    </div>
  );
};

export default AdminDashboard;