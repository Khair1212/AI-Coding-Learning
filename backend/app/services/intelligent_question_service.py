"""
Intelligent Question Selection Service

This service uses AI and assessment data to dynamically select 
the most appropriate questions for each user in each lesson.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
import json
import random
from datetime import datetime, timedelta

from app.models import (
    User, UserSkillProfile, UserAssessment, AssessmentResponse,
    Question, Lesson, Level, UserLessonProgress, QuizType, LessonType
)
from app.services.ai_service import AIQuestionGenerator


class IntelligentQuestionSelectionService:
    """
    AI-powered service that selects optimal questions for each user based on:
    - Assessment results and skill gaps
    - Learning progress and performance patterns
    - AI analysis of question difficulty and user needs
    - Dynamic adaptation based on real-time performance
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_generator = AIQuestionGenerator()
    
    def select_personalized_questions_for_lesson(
        self, 
        user_id: int, 
        lesson_id: int, 
        target_count: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Main method: Select personalized questions for a specific lesson
        
        Args:
            user_id: User requesting the questions
            lesson_id: Lesson to select questions from
            target_count: Desired number of questions (default 4)
            
        Returns:
            List of selected questions with AI reasoning
        """
        # Get user context
        user_context = self._analyze_user_context(user_id)
        
        # Get lesson context
        lesson_context = self._analyze_lesson_context(lesson_id)
        
        # Get all available questions for this lesson
        all_questions = self.db.query(Question).filter(
            Question.lesson_id == lesson_id
        ).all()
        
        if len(all_questions) <= target_count:
            # If we have few questions, return all
            return [self._format_question_with_context(q, user_context, "insufficient_pool") 
                   for q in all_questions]
        
        # Intelligent selection process
        selected_questions = self._ai_powered_question_selection(
            all_questions, 
            user_context, 
            lesson_context, 
            target_count
        )
        
        # Log the selection for analytics
        self._log_question_selection(user_id, lesson_id, selected_questions, user_context)
        
        return selected_questions
    
    def _analyze_user_context(self, user_id: int) -> Dict[str, Any]:
        """Comprehensive analysis of user's learning state"""
        
        # Get user skill profile
        profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        # Get latest assessment
        latest_assessment = self.db.query(UserAssessment).filter(
            UserAssessment.user_id == user_id,
            UserAssessment.is_completed == True
        ).order_by(desc(UserAssessment.completed_at)).first()
        
        # Get recent performance
        recent_progress = self.db.query(UserLessonProgress).filter(
            UserLessonProgress.user_profile_id == profile.id if profile else None
        ).order_by(desc(UserLessonProgress.created_at)).limit(5).all()
        
        # Analyze assessment responses for skill gaps
        skill_gaps = {}
        strengths = {}
        
        if latest_assessment:
            responses = self.db.query(AssessmentResponse).filter(
                AssessmentResponse.assessment_id == latest_assessment.id
            ).all()
            
            # Group by topic and analyze
            topic_performance = {}
            for response in responses:
                question = response.question
                if not question:
                    continue
                    
                topic = question.topic_area
                if topic not in topic_performance:
                    topic_performance[topic] = []
                
                topic_performance[topic].append({
                    'correct': response.is_correct,
                    'confidence': response.confidence_level,
                    'time_taken': response.time_taken_seconds,
                    'difficulty': question.expected_level
                })
            
            # Identify gaps and strengths
            for topic, performances in topic_performance.items():
                accuracy = sum(1 for p in performances if p['correct']) / len(performances)
                avg_confidence = sum(p['confidence'] or 3 for p in performances) / len(performances)
                
                if accuracy < 0.6 or avg_confidence < 3:
                    skill_gaps[topic] = {
                        'accuracy': accuracy,
                        'confidence': avg_confidence,
                        'severity': 'high' if accuracy < 0.4 else 'medium'
                    }
                elif accuracy > 0.8 and avg_confidence > 4:
                    strengths[topic] = {
                        'accuracy': accuracy,
                        'confidence': avg_confidence
                    }
        
        # Recent performance trend
        performance_trend = 'stable'
        if recent_progress and len(recent_progress) >= 3:
            recent_scores = [p.score for p in recent_progress if p.score is not None]
            if recent_scores:
                if recent_scores[0] > recent_scores[-1] + 10:
                    performance_trend = 'improving'
                elif recent_scores[0] < recent_scores[-1] - 10:
                    performance_trend = 'declining'
        
        return {
            'user_id': user_id,
            'skill_profile': profile,
            'latest_assessment': latest_assessment,
            'skill_gaps': skill_gaps,
            'strengths': strengths,
            'performance_trend': performance_trend,
            'recent_progress': recent_progress,
            'learning_velocity': profile.learning_velocity if profile else 1.0,
            'prefers_challenge': profile.prefers_challenge if profile else False,
            'needs_practice': profile.needs_more_practice if profile else True
        }
    
    def _analyze_lesson_context(self, lesson_id: int) -> Dict[str, Any]:
        """Analyze lesson characteristics and requirements"""
        
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            return {}
        
        level = self.db.query(Level).filter(Level.id == lesson.level_id).first()
        
        # Get question distribution
        questions = self.db.query(Question).filter(Question.lesson_id == lesson_id).all()
        
        question_types = {}
        difficulties = []
        topics = set()
        
        for q in questions:
            # Question type distribution
            q_type = q.question_type.value if hasattr(q.question_type, 'value') else str(q.question_type)
            question_types[q_type] = question_types.get(q_type, 0) + 1
            
            # Topic areas (if available in question)
            if hasattr(q, 'topic_area') and q.topic_area:
                topics.add(q.topic_area)
        
        return {
            'lesson_id': lesson_id,
            'lesson': lesson,
            'level': level,
            'total_questions': len(questions),
            'question_types': question_types,
            'topics': list(topics),
            'lesson_type': lesson.lesson_type,
            'difficulty': lesson.difficulty
        }
    
    def _ai_powered_question_selection(
        self, 
        all_questions: List[Question], 
        user_context: Dict[str, Any], 
        lesson_context: Dict[str, Any], 
        target_count: int
    ) -> List[Dict[str, Any]]:
        """Use AI logic to select the best questions for this user"""
        
        # Score each question based on user needs
        question_scores = []
        
        for question in all_questions:
            score = self._calculate_question_relevance_score(
                question, user_context, lesson_context
            )
            question_scores.append((question, score))
        
        # Sort by relevance score
        question_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top questions with diversity
        selected = self._ensure_question_diversity(
            question_scores, target_count, user_context
        )
        
        # Format with AI reasoning
        formatted_questions = []
        for question, score in selected:
            reasoning = self._generate_selection_reasoning(question, score, user_context)
            formatted_questions.append(
                self._format_question_with_context(question, user_context, reasoning)
            )
        
        return formatted_questions
    
    def _calculate_question_relevance_score(
        self, 
        question: Question, 
        user_context: Dict[str, Any], 
        lesson_context: Dict[str, Any]
    ) -> float:
        """Calculate how relevant this question is for the user (0-100 score)"""
        
        score = 50.0  # Base score
        
        # Factor 1: Address skill gaps (highest weight)
        skill_gaps = user_context.get('skill_gaps', {})
        question_topic = getattr(question, 'topic_area', None)
        
        if question_topic and question_topic in skill_gaps:
            gap_severity = skill_gaps[question_topic].get('severity', 'medium')
            if gap_severity == 'high':
                score += 30
            elif gap_severity == 'medium':
                score += 20
            else:
                score += 10
        
        # Factor 2: Question type preference based on performance
        q_type = question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type)
        
        performance_trend = user_context.get('performance_trend', 'stable')
        if performance_trend == 'declining':
            # Prefer easier question types for struggling users
            if q_type == 'multiple_choice':
                score += 15
            elif q_type == 'fill_in_blank':
                score += 10
        elif performance_trend == 'improving':
            # Challenge improving users
            if q_type == 'coding_exercise':
                score += 20
            elif q_type == 'fill_in_blank':
                score += 15
        
        # Factor 3: User preferences
        prefers_challenge = user_context.get('prefers_challenge', False)
        if prefers_challenge and q_type == 'coding_exercise':
            score += 15
        
        needs_practice = user_context.get('needs_practice', True)
        if needs_practice and q_type == 'multiple_choice':
            score += 10
        
        # Factor 4: Learning velocity adaptation
        velocity = user_context.get('learning_velocity', 1.0)
        if velocity > 1.5:
            # Fast learners get more challenging questions
            if q_type == 'coding_exercise':
                score += 10
        elif velocity < 0.7:
            # Slower learners get more foundational questions
            if q_type == 'multiple_choice':
                score += 10
        
        # Factor 5: Avoid recently seen questions (if we track this)
        # This would require additional tracking - placeholder for now
        
        # Factor 6: Question quality indicators
        # If question has good explanation, boost score
        if hasattr(question, 'explanation') and question.explanation:
            score += 5
        
        # If question has code template for coding exercises
        if q_type == 'coding_exercise' and hasattr(question, 'code_template') and question.code_template:
            score += 5
        
        return min(100.0, max(0.0, score))
    
    def _ensure_question_diversity(
        self, 
        scored_questions: List[Tuple[Question, float]], 
        target_count: int,
        user_context: Dict[str, Any]
    ) -> List[Tuple[Question, float]]:
        """Ensure selected questions have good diversity in types and topics"""
        
        selected = []
        type_counts = {}
        topic_counts = {}
        
        # First, take the highest scored questions while maintaining diversity
        for question, score in scored_questions:
            if len(selected) >= target_count:
                break
            
            q_type = question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type)
            q_topic = getattr(question, 'topic_area', 'general')
            
            # Check if we have too many of this type/topic
            current_type_count = type_counts.get(q_type, 0)
            current_topic_count = topic_counts.get(q_topic, 0)
            
            # Allow at most 60% of questions to be the same type
            max_same_type = max(1, int(target_count * 0.6))
            max_same_topic = max(1, int(target_count * 0.7))
            
            if current_type_count < max_same_type and current_topic_count < max_same_topic:
                selected.append((question, score))
                type_counts[q_type] = current_type_count + 1
                topic_counts[q_topic] = current_topic_count + 1
        
        # If we don't have enough, fill with remaining questions
        if len(selected) < target_count:
            remaining = [q for q in scored_questions if q not in selected]
            selected.extend(remaining[:target_count - len(selected)])
        
        return selected[:target_count]
    
    def _generate_selection_reasoning(
        self, 
        question: Question, 
        score: float, 
        user_context: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for why this question was selected"""
        
        reasons = []
        
        # High score reasons
        if score >= 80:
            reasons.append("High relevance for your current learning needs")
        elif score >= 65:
            reasons.append("Good match for your skill level")
        
        # Skill gap addressing
        skill_gaps = user_context.get('skill_gaps', {})
        question_topic = getattr(question, 'topic_area', None)
        
        if question_topic and question_topic in skill_gaps:
            severity = skill_gaps[question_topic].get('severity', 'medium')
            if severity == 'high':
                reasons.append(f"Addresses your weak area in {question_topic}")
            else:
                reasons.append(f"Helps reinforce {question_topic} skills")
        
        # Question type reasoning
        q_type = question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type)
        
        performance_trend = user_context.get('performance_trend', 'stable')
        if performance_trend == 'improving' and q_type == 'coding_exercise':
            reasons.append("Challenges you with hands-on coding")
        elif performance_trend == 'declining' and q_type == 'multiple_choice':
            reasons.append("Builds confidence with structured questions")
        
        # User preference reasoning
        if user_context.get('prefers_challenge', False) and q_type == 'coding_exercise':
            reasons.append("Matches your preference for challenging problems")
        
        if not reasons:
            reasons.append("Selected for balanced learning experience")
        
        return " • ".join(reasons[:2])  # Keep it concise
    
    def _format_question_with_context(
        self, 
        question: Question, 
        user_context: Dict[str, Any], 
        reasoning: str
    ) -> Dict[str, Any]:
        """Format question with additional context for the frontend"""
        
        return {
            'id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type),
            'correct_answer': question.correct_answer,
            'options': question.options,
            'explanation': question.explanation,
            'code_template': question.code_template,
            # AI context
            'selection_reasoning': reasoning,
            'personalized': True,
            'recommended_time_minutes': self._estimate_question_time(question, user_context),
            'difficulty_for_user': self._assess_difficulty_for_user(question, user_context)
        }
    
    def _estimate_question_time(self, question: Question, user_context: Dict[str, Any]) -> int:
        """Estimate how long this question should take for this user"""
        
        base_times = {
            'multiple_choice': 2,
            'fill_in_blank': 3,
            'coding_exercise': 8
        }
        
        q_type = question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type)
        base_time = base_times.get(q_type, 5)
        
        # Adjust for user's learning velocity
        velocity = user_context.get('learning_velocity', 1.0)
        adjusted_time = base_time / velocity
        
        # Adjust for skill gaps
        question_topic = getattr(question, 'topic_area', None)
        skill_gaps = user_context.get('skill_gaps', {})
        
        if question_topic and question_topic in skill_gaps:
            adjusted_time *= 1.3  # Need more time for weak areas
        
        return max(1, int(adjusted_time))
    
    def _assess_difficulty_for_user(self, question: Question, user_context: Dict[str, Any]) -> str:
        """Assess how difficult this question will be for this specific user"""
        
        # Base difficulty from question type
        q_type = question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type)
        
        base_difficulty = {
            'multiple_choice': 'easy',
            'fill_in_blank': 'medium',  
            'coding_exercise': 'hard'
        }.get(q_type, 'medium')
        
        # Adjust for user's skill gaps
        question_topic = getattr(question, 'topic_area', None)
        skill_gaps = user_context.get('skill_gaps', {})
        strengths = user_context.get('strengths', {})
        
        if question_topic:
            if question_topic in skill_gaps:
                # Harder for weak areas
                if base_difficulty == 'easy':
                    return 'medium'
                elif base_difficulty == 'medium':
                    return 'hard'
                else:
                    return 'very_hard'
            elif question_topic in strengths:
                # Easier for strong areas
                if base_difficulty == 'hard':
                    return 'medium'
                elif base_difficulty == 'medium':
                    return 'easy'
        
        return base_difficulty
    
    def _log_question_selection(
        self, 
        user_id: int, 
        lesson_id: int, 
        selected_questions: List[Dict[str, Any]], 
        user_context: Dict[str, Any]
    ):
        """Log the selection for analytics and improvement"""
        
        # This would typically go to a logging service
        # For now, we'll just print for debugging
        print(f"🎯 Intelligent Question Selection for User {user_id}, Lesson {lesson_id}:")
        print(f"   Selected {len(selected_questions)} questions")
        print(f"   User velocity: {user_context.get('learning_velocity', 1.0):.2f}")
        print(f"   Skill gaps: {list(user_context.get('skill_gaps', {}).keys())}")
        print(f"   Strengths: {list(user_context.get('strengths', {}).keys())}")
        
        # Could store in database for future analysis
        # selection_log = QuestionSelectionLog(...)