from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import json
import random

from app.models import (
    User, UserSkillProfile, Quiz, QuizType, QuizDifficultyLevel,
    PersonalizedQuizAssignment, UserQuizAttempt, Lesson, Level,
    UserAssessment, Question, UserLessonProgress
)
from app.services.ai_service import AIQuestionGenerator

class IntelligentQuizAssignmentService:
    """
    Service for intelligently assigning personalized quizzes to users based on:
    - Skill assessment results
    - Learning progress
    - Performance patterns
    - Skill gaps
    - Learning velocity
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_generator = AIQuestionGenerator()
    
    def assign_personalized_quizzes_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Main method to assign personalized quizzes to a user based on their skill profile
        """
        user_profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        if not user_profile:
            # If no profile, assign basic beginner quizzes
            return self._assign_beginner_quizzes(user_id)
        
        # Analyze user's learning context
        learning_context = self._analyze_user_learning_context(user_id, user_profile)
        
        # Get personalized quiz recommendations
        quiz_assignments = []
        
        # 1. Address skill gaps (highest priority)
        skill_gap_quizzes = self._get_skill_gap_quizzes(user_id, user_profile, learning_context)
        quiz_assignments.extend(skill_gap_quizzes)
        
        # 2. Reinforce recent learning
        reinforcement_quizzes = self._get_reinforcement_quizzes(user_id, user_profile, learning_context)
        quiz_assignments.extend(reinforcement_quizzes)
        
        # 3. Progressive advancement
        advancement_quizzes = self._get_advancement_quizzes(user_id, user_profile, learning_context)
        quiz_assignments.extend(advancement_quizzes)
        
        # 4. Challenge quizzes for high performers
        if user_profile.learning_velocity > 1.3 and user_profile.overall_skill_level.value in ['advanced', 'expert']:
            challenge_quizzes = self._get_challenge_quizzes(user_id, user_profile, learning_context)
            quiz_assignments.extend(challenge_quizzes)
        
        # Store assignments in database
        self._store_quiz_assignments(user_id, quiz_assignments)
        
        return quiz_assignments
    
    def _analyze_user_learning_context(self, user_id: int, profile: UserSkillProfile) -> Dict[str, Any]:
        """Analyze user's current learning state and patterns"""
        
        # Recent quiz attempts
        recent_attempts = self.db.query(UserQuizAttempt).filter(
            UserQuizAttempt.user_id == user_id,
            UserQuizAttempt.started_at >= datetime.now() - timedelta(days=14)
        ).all()
        
        # Recent lesson progress
        recent_progress = self.db.query(UserLessonProgress).filter(
            UserLessonProgress.user_profile_id == profile.id,
            UserLessonProgress.created_at >= datetime.now() - timedelta(days=7)
        ).all()
        
        # Skill mastery breakdown
        skill_mastery = {
            'basics': profile.basics_mastery,
            'control_flow': profile.control_flow_mastery,
            'functions': profile.functions_mastery,
            'arrays': profile.arrays_mastery,
            'pointers': profile.pointers_mastery
        }
        
        # Identify weak and strong areas
        weak_areas = [skill for skill, mastery in skill_mastery.items() if mastery < 0.6]
        strong_areas = [skill for skill, mastery in skill_mastery.items() if mastery > 0.8]
        
        # Performance trends
        if recent_attempts:
            recent_accuracy = sum(a.accuracy_percentage for a in recent_attempts) / len(recent_attempts)
            improving = len([a for a in recent_attempts[-3:] if a.accuracy_percentage > recent_accuracy]) > 1
        else:
            recent_accuracy = 0
            improving = True  # Assume positive for new users
        
        return {
            'skill_mastery': skill_mastery,
            'weak_areas': weak_areas,
            'strong_areas': strong_areas,
            'recent_accuracy': recent_accuracy,
            'improving': improving,
            'recent_attempts_count': len(recent_attempts),
            'learning_velocity': profile.learning_velocity,
            'prefers_challenge': profile.prefers_challenge,
            'needs_more_practice': profile.needs_more_practice,
            'current_level': profile.adaptive_level
        }
    
    def _get_skill_gap_quizzes(self, user_id: int, profile: UserSkillProfile, context: Dict) -> List[Dict]:
        """Get quizzes targeting user's skill gaps"""
        assignments = []
        
        for weak_area in context['weak_areas']:
            # Find quizzes targeting this skill area
            skill_area_json = json.dumps([weak_area])
            
            quizzes = self.db.query(Quiz).filter(
                Quiz.target_skill_areas.contains(weak_area),
                Quiz.min_skill_level <= context['skill_mastery'][weak_area],
                Quiz.max_skill_level >= context['skill_mastery'][weak_area],
                Quiz.is_active == True,
                Quiz.quiz_type.in_([QuizType.SKILL_REINFORCEMENT, QuizType.LESSON_PRACTICE])
            ).limit(2).all()
            
            for quiz in quizzes:
                assignments.append({
                    'quiz': quiz,
                    'priority': 1,  # High priority for skill gaps
                    'reason': f'skill_gap_{weak_area}',
                    'explanation': f'This quiz targets {weak_area} where you need improvement'
                })
        
        return assignments
    
    def _get_reinforcement_quizzes(self, user_id: int, profile: UserSkillProfile, context: Dict) -> List[Dict]:
        """Get quizzes to reinforce recently learned concepts"""
        assignments = []
        
        # Find lessons completed in last 3 days
        recent_lessons = self.db.query(UserLessonProgress).filter(
            UserLessonProgress.user_profile_id == profile.id,
            UserLessonProgress.is_completed == True,
            UserLessonProgress.completed_at >= datetime.now() - timedelta(days=3)
        ).all()
        
        for progress in recent_lessons:
            # Find reinforcement quizzes for this lesson
            quizzes = self.db.query(Quiz).filter(
                Quiz.lesson_id == progress.lesson_id,
                Quiz.quiz_type == QuizType.LESSON_PRACTICE,
                Quiz.difficulty_level.in_([
                    QuizDifficultyLevel.BEGINNER,
                    QuizDifficultyLevel.INTERMEDIATE
                ]),
                Quiz.is_active == True
            ).limit(1).all()
            
            for quiz in quizzes:
                assignments.append({
                    'quiz': quiz,
                    'priority': 2,  # Medium priority for reinforcement
                    'reason': 'reinforcement',
                    'explanation': f'Reinforce your recent learning in {quiz.lesson.title}'
                })
        
        return assignments
    
    def _get_advancement_quizzes(self, user_id: int, profile: UserSkillProfile, context: Dict) -> List[Dict]:
        """Get quizzes for progressive advancement"""
        assignments = []
        
        # Find next appropriate level based on current skill
        target_level = min(profile.adaptive_level + 1, 10)
        
        # Get lessons from target level where user might be ready
        target_lessons = self.db.query(Lesson).join(Level).filter(
            Level.level_number == target_level
        ).all()
        
        for lesson in target_lessons:
            # Check if user has prerequisite skills
            lesson_skill_area = self._map_lesson_to_skill_area(lesson)
            current_mastery = context['skill_mastery'].get(lesson_skill_area, 0)
            
            if current_mastery >= 0.7:  # Ready for advancement
                quizzes = self.db.query(Quiz).filter(
                    Quiz.lesson_id == lesson.id,
                    Quiz.quiz_type == QuizType.LESSON_PRACTICE,
                    Quiz.difficulty_level == QuizDifficultyLevel.INTERMEDIATE,
                    Quiz.is_active == True
                ).limit(1).all()
                
                for quiz in quizzes:
                    assignments.append({
                        'quiz': quiz,
                        'priority': 2,  # Medium priority for advancement
                        'reason': 'advancement',
                        'explanation': f'Ready to advance to {lesson.title}'
                    })
        
        return assignments
    
    def _get_challenge_quizzes(self, user_id: int, profile: UserSkillProfile, context: Dict) -> List[Dict]:
        """Get challenging quizzes for high performers"""
        assignments = []
        
        # Find advanced/challenge quizzes in user's strong areas
        for strong_area in context['strong_areas']:
            quizzes = self.db.query(Quiz).filter(
                Quiz.target_skill_areas.contains(strong_area),
                Quiz.quiz_type == QuizType.CHALLENGE,
                Quiz.difficulty_level.in_([
                    QuizDifficultyLevel.ADVANCED,
                    QuizDifficultyLevel.ADAPTIVE
                ]),
                Quiz.is_active == True
            ).limit(1).all()
            
            for quiz in quizzes:
                assignments.append({
                    'quiz': quiz,
                    'priority': 3,  # Lower priority for challenges
                    'reason': 'challenge',
                    'explanation': f'Challenge your {strong_area} skills'
                })
        
        return assignments
    
    def _assign_beginner_quizzes(self, user_id: int) -> List[Dict[str, Any]]:
        """Assign basic beginner quizzes for users without skill profiles"""
        assignments = []
        
        # Get first few lessons from Level 1
        beginner_lessons = self.db.query(Lesson).join(Level).filter(
            Level.level_number == 1
        ).limit(3).all()
        
        for lesson in beginner_lessons:
            quizzes = self.db.query(Quiz).filter(
                Quiz.lesson_id == lesson.id,
                Quiz.difficulty_level == QuizDifficultyLevel.BEGINNER,
                Quiz.quiz_type == QuizType.LESSON_PRACTICE,
                Quiz.is_active == True
            ).limit(1).all()
            
            for quiz in quizzes:
                assignments.append({
                    'quiz': quiz,
                    'priority': 1,
                    'reason': 'beginner_start',
                    'explanation': 'Start with basic C programming concepts'
                })
        
        return assignments
    
    def _map_lesson_to_skill_area(self, lesson: Lesson) -> str:
        """Map lesson to skill area for targeting"""
        level_num = lesson.level.level_number if lesson.level else 1
        
        if level_num <= 3:
            return 'basics'
        elif level_num <= 6:
            return 'control_flow'
        elif level_num == 7:
            return 'functions'
        elif level_num <= 9:
            return 'arrays'
        else:
            return 'pointers'
    
    def _store_quiz_assignments(self, user_id: int, assignments: List[Dict]):
        """Store quiz assignments in database"""
        # Clear existing active assignments
        self.db.query(PersonalizedQuizAssignment).filter(
            PersonalizedQuizAssignment.user_id == user_id,
            PersonalizedQuizAssignment.is_active == True
        ).update({'is_active': False})
        
        # Create new assignments
        for assignment_data in assignments:
            quiz = assignment_data['quiz']
            assignment = PersonalizedQuizAssignment(
                user_id=user_id,
                quiz_id=quiz.id,
                lesson_id=quiz.lesson_id,
                assignment_reason=assignment_data['reason'],
                priority=assignment_data['priority'],
                target_improvement_areas=json.dumps([assignment_data['reason']]),
                is_active=True
            )
            self.db.add(assignment)
        
        self.db.commit()
    
    def get_user_assigned_quizzes(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get currently assigned quizzes for a user"""
        assignments = self.db.query(PersonalizedQuizAssignment).filter(
            PersonalizedQuizAssignment.user_id == user_id,
            PersonalizedQuizAssignment.is_active == True
        ).order_by(PersonalizedQuizAssignment.priority).limit(limit).all()
        
        result = []
        for assignment in assignments:
            quiz = assignment.quiz
            
            # Check if already attempted
            attempts = self.db.query(UserQuizAttempt).filter(
                UserQuizAttempt.user_id == user_id,
                UserQuizAttempt.quiz_id == quiz.id
            ).count()
            
            result.append({
                'assignment_id': assignment.id,
                'quiz': {
                    'id': quiz.id,
                    'title': quiz.title,
                    'description': quiz.description,
                    'lesson_title': quiz.lesson.title,
                    'level_number': quiz.lesson.level.level_number,
                    'difficulty': quiz.difficulty_level.value,
                    'estimated_time': quiz.estimated_time_minutes,
                    'question_count': quiz.question_count,
                    'quiz_type': quiz.quiz_type.value
                },
                'assignment': {
                    'priority': assignment.priority,
                    'reason': assignment.assignment_reason,
                    'assigned_at': assignment.assigned_at
                },
                'attempts_made': attempts,
                'max_attempts': quiz.max_attempts,
                'can_attempt': attempts < quiz.max_attempts
            })
        
        return result
    
    def reassign_quizzes_after_assessment(self, user_id: int, assessment_id: int):
        """Reassign quizzes after user completes a skill assessment"""
        # This triggers a complete re-evaluation of the user's quiz assignments
        return self.assign_personalized_quizzes_for_user(user_id)