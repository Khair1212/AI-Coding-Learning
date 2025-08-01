import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { learningAPI, Level, Lesson } from '../api/learning';
import { theme } from '../styles/theme';

const LessonMap: React.FC = () => {
  const [levels, setLevels] = useState<Level[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<number | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLevels();
  }, []);

  useEffect(() => {
    if (selectedLevel) {
      fetchLessons(selectedLevel);
    }
  }, [selectedLevel]);

  const fetchLevels = async () => {
    try {
      const levelsData = await learningAPI.getLevels();
      setLevels(levelsData);
      if (levelsData.length > 0) {
        setSelectedLevel(levelsData[0].id);
      }
    } catch (error) {
      console.error('Error fetching levels:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLessons = async (levelId: number) => {
    try {
      const lessonsData = await learningAPI.getLevelLessons(levelId);
      setLessons(lessonsData);
    } catch (error) {
      console.error('Error fetching lessons:', error);
    }
  };

  const handleLessonClick = (lesson: Lesson) => {
    navigate(`/lesson/${lesson.id}`);
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading lesson map...</div>
      </div>
    );
  }

  const containerStyle = {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  };

  const headerStyle = {
    textAlign: 'center' as const,
    marginBottom: '40px'
  };

  const titleStyle = {
    fontSize: '32px',
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: '8px'
  };

  const subtitleStyle = {
    fontSize: '18px',
    color: theme.colors.textSecondary
  };

  const levelsContainerStyle = {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '12px',
    justifyContent: 'center',
    marginBottom: '40px'
  };

  const levelButtonStyle = (isSelected: boolean, levelNum: number) => ({
    padding: '12px 20px',
    borderRadius: theme.borderRadius.full,
    border: isSelected ? `2px solid ${theme.colors.primary}` : '2px solid #e9ecef',
    background: isSelected ? theme.colors.primary : 'white',
    color: isSelected ? 'white' : theme.colors.text,
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.3s ease',
    position: 'relative' as const,
    minWidth: '100px'
  });

  const lessonMapStyle = {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '20px',
    maxWidth: '600px',
    margin: '0 auto'
  };

  const lessonNodeStyle = (lesson: Lesson, index: number) => {
    const isCompleted = lesson.is_completed;
    const isLocked = index > 0 && !lessons[index - 1]?.is_completed;
    
    return {
      width: '80px',
      height: '80px',
      borderRadius: '50%',
      border: `4px solid ${isCompleted ? '#28a745' : isLocked ? '#dee2e6' : theme.colors.primary}`,
      background: isCompleted ? '#28a745' : isLocked ? '#f8f9fa' : theme.colors.primary,
      color: isCompleted || !isLocked ? 'white' : '#6c757d',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: isLocked ? 'not-allowed' : 'pointer',
      fontSize: '24px',
      fontWeight: 'bold',
      position: 'relative' as const,
      transition: 'all 0.3s ease',
      boxShadow: isCompleted ? '0 4px 12px rgba(40, 167, 69, 0.3)' : 
                  isLocked ? 'none' : `0 4px 12px ${theme.colors.primary}30`
    };
  };

  const lessonInfoStyle = {
    textAlign: 'center' as const,
    marginTop: '12px'
  };

  const lessonTitleStyle = {
    fontSize: '16px',
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: '4px'
  };

  const lessonTypeStyle = {
    fontSize: '12px',
    color: theme.colors.textSecondary,
    textTransform: 'capitalize' as const
  };

  const pathLineStyle = {
    width: '4px',
    height: '40px',
    background: '#dee2e6',
    margin: '0 auto'
  };

  const getLessonIcon = (lesson: Lesson) => {
    if (lesson.is_completed) return '✓';
    if (lesson.lesson_type === 'coding_exercise') return '💻';
    if (lesson.lesson_type === 'multiple_choice') return '❓';
    if (lesson.lesson_type === 'fill_in_blank') return '📝';
    return '📚';
  };

  const selectedLevelData = levels.find(l => l.id === selectedLevel);

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h1 style={titleStyle}>Learn C Programming</h1>
        <p style={subtitleStyle}>
          Master C programming through interactive lessons and coding exercises
        </p>
      </div>

      {/* Level Selection */}
      <div style={levelsContainerStyle}>
        {levels.map((level) => (
          <button
            key={level.id}
            style={levelButtonStyle(selectedLevel === level.id, level.level_number)}
            onClick={() => setSelectedLevel(level.id)}
            onMouseEnter={(e) => {
              if (selectedLevel !== level.id) {
                e.currentTarget.style.background = '#f8f9fa';
                e.currentTarget.style.borderColor = theme.colors.primary;
              }
            }}
            onMouseLeave={(e) => {
              if (selectedLevel !== level.id) {
                e.currentTarget.style.background = 'white';
                e.currentTarget.style.borderColor = '#e9ecef';
              }
            }}
          >
            Level {level.level_number}
          </button>
        ))}
      </div>

      {/* Assessment Banner */}
      <div style={{
        background: `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
        color: 'white',
        padding: '20px',
        borderRadius: theme.borderRadius.lg,
        textAlign: 'center',
        marginBottom: '30px',
        cursor: 'pointer'
      }}
      onClick={() => navigate('/assessment')}
      >
        <h3 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>
          🎯 Not sure where to start?
        </h3>
        <p style={{ margin: '0 0 12px 0', opacity: 0.9 }}>
          Take our skill assessment to get personalized recommendations
        </p>
        <div style={{
          background: 'rgba(255, 255, 255, 0.2)',
          padding: '8px 16px',
          borderRadius: theme.borderRadius.md,
          display: 'inline-block',
          fontSize: '14px',
          fontWeight: '600'
        }}>
          Take Assessment →
        </div>
      </div>

      {/* Selected Level Info */}
      {selectedLevelData && (
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ color: theme.colors.text, marginBottom: '8px' }}>
            {selectedLevelData.title}
          </h2>
          <p style={{ color: theme.colors.textSecondary, fontSize: '16px' }}>
            {selectedLevelData.description}
          </p>
        </div>
      )}

      {/* Lesson Map */}
      <div style={lessonMapStyle}>
        {lessons.map((lesson, index) => {
          const isLocked = index > 0 && !lessons[index - 1]?.is_completed;
          
          return (
            <div key={lesson.id}>
              {index > 0 && <div style={pathLineStyle}></div>}
              <div
                style={lessonNodeStyle(lesson, index)}
                onClick={() => !isLocked && handleLessonClick(lesson)}
                onMouseEnter={(e) => {
                  if (!isLocked) {
                    e.currentTarget.style.transform = 'scale(1.1)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                {getLessonIcon(lesson)}
                {isLocked && (
                  <div style={{
                    position: 'absolute',
                    top: '-5px',
                    right: '-5px',
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    background: '#dc3545',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px'
                  }}>
                    🔒
                  </div>
                )}
              </div>
              <div style={lessonInfoStyle}>
                <div style={lessonTitleStyle}>{lesson.title}</div>
                <div style={lessonTypeStyle}>
                  {lesson.lesson_type.replace('_', ' ')} • {lesson.xp_reward} XP
                </div>
                {lesson.is_completed && (
                  <div style={{ 
                    fontSize: '12px', 
                    color: '#28a745', 
                    marginTop: '4px',
                    fontWeight: '600'
                  }}>
                    Score: {lesson.score?.toFixed(0)}%
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {lessons.length === 0 && selectedLevel && (
        <div style={{ textAlign: 'center', color: theme.colors.textSecondary }}>
          No lessons available for this level yet.
        </div>
      )}
    </div>
  );
};

export default LessonMap;