from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models import (
    User, UserAssessment, AssessmentQuestion, AssessmentResponse,
    UserSkillProfile, SkillLevel, AdaptiveDifficultyLog, Lesson, DifficultyLevel
)
from app.services.ai_service import AIQuestionGenerator
import math

class AdaptiveLearningService:
    """Service for adaptive difficulty and personalized learning"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_generator = AIQuestionGenerator()
    
    def calculate_skill_level(self, assessment: UserAssessment) -> Tuple[int, SkillLevel]:
        """Calculate user's skill level based on assessment results"""
        if not assessment.is_completed:
            return 1, SkillLevel.COMPLETE_BEGINNER
        
        accuracy = assessment.accuracy_percentage / 100.0
        responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment.id
        ).all()
        
        # Calculate level-weighted score based on question expected levels
        total_level_weight = 0
        weighted_level_score = 0
        
        topic_scores = {
            'basics': 0, 'control_flow': 0, 'functions': 0, 
            'arrays': 0, 'pointers': 0
        }
        topic_counts = {
            'basics': 0, 'control_flow': 0, 'functions': 0, 
            'arrays': 0, 'pointers': 0
        }
        
        # Calculate level-based scoring
        for response in responses:
            question = response.question
            # Use expected_level as the weight (higher level questions worth more)
            level_weight = question.expected_level * question.difficulty_weight
            total_level_weight += level_weight
            
            if response.is_correct:
                weighted_level_score += level_weight
                
            # Track topic-specific performance
            topic = self._get_topic_category(question.topic_area)
            if topic in topic_scores:
                topic_scores[topic] += 1 if response.is_correct else 0
                topic_counts[topic] += 1
        
        # Calculate realistic level based on WEAKEST areas (pedagogically sound)
        if total_level_weight == 0 or len(responses) == 0:
            calculated_level = 1
        else:
            # Step 1: Analyze topic-specific performance
            topic_mastery = {}
            for topic in topic_scores:
                if topic_counts[topic] > 0:
                    mastery_rate = topic_scores[topic] / topic_counts[topic]
                    topic_mastery[topic] = mastery_rate
                else:
                    topic_mastery[topic] = 0.0
            
            # Step 2: Map topics to prerequisite levels (progressive learning)
            topic_to_level_range = {
                'basics': (1, 3),      # Levels 1-3: Variables, I/O, syntax
                'control_flow': (4, 6), # Levels 4-6: If/else, loops
                'functions': (7, 7),    # Level 7: Functions
                'arrays': (8, 9),      # Levels 8-9: Arrays, strings
                'pointers': (10, 10)   # Level 10: Pointers, memory
            }
            
            # Step 3: Find weakest prerequisite area (foundation-based approach)
            recommended_level = 10  # Start optimistic
            weak_areas = []
            
            for topic, mastery in topic_mastery.items():
                min_level, max_level = topic_to_level_range[topic]
                
                # If mastery is poor in a foundational topic, start there
                if mastery < 0.7:  # Less than 70% mastery
                    recommended_level = min(recommended_level, min_level)
                    weak_areas.append(f"{topic} ({mastery:.1%})")
                elif mastery < 0.9:  # Less than 90% mastery
                    # Can start in this topic range but not advance beyond it
                    recommended_level = min(recommended_level, max_level)
            
            # Step 4: Check for prerequisite violations
            # Can't be good at advanced topics without mastering basics
            basics_mastery = topic_mastery.get('basics', 0)
            control_mastery = topic_mastery.get('control_flow', 0)
            
            if basics_mastery < 0.8 and recommended_level > 3:
                recommended_level = min(recommended_level, 3)
                weak_areas.append(f"basics_foundation ({basics_mastery:.1%})")
            
            if control_mastery < 0.8 and recommended_level > 6:
                recommended_level = min(recommended_level, 6)
                weak_areas.append(f"control_flow_foundation ({control_mastery:.1%})")
            
            # Step 5: AI-powered analysis for edge cases
            ai_recommendation = self._get_ai_level_recommendation(responses, topic_mastery, accuracy)
            
            # Final level: Conservative approach (choose lower of algorithmic vs AI)
            calculated_level = min(recommended_level, ai_recommendation)
            calculated_level = max(1, min(10, calculated_level))
            
            # Debug logging
            print(f"Realistic Level Calculation:")
            print(f"  Overall Accuracy: {accuracy:.1%}")
            print(f"  Topic Mastery: {topic_mastery}")
            print(f"  Weak Areas: {weak_areas}")
            print(f"  Algorithmic Level: {recommended_level}")
            print(f"  AI Recommendation: {ai_recommendation}")
            print(f"  Final Conservative Level: {calculated_level}")
            print(f"  Reasoning: Start where foundations are weakest")
        
        # Determine skill level enum
        if accuracy < 0.3:
            skill_level = SkillLevel.COMPLETE_BEGINNER
        elif accuracy < 0.5:
            skill_level = SkillLevel.BEGINNER
        elif accuracy < 0.7:
            skill_level = SkillLevel.INTERMEDIATE
        elif accuracy < 0.9:
            skill_level = SkillLevel.ADVANCED
        else:
            skill_level = SkillLevel.EXPERT
        
        # Update user skill profile
        self._update_skill_profile(assessment.user_id, topic_scores, topic_counts, 
                                 skill_level, calculated_level)
        
        return calculated_level, skill_level
    
    def _get_topic_category(self, topic_area: str) -> str:
        """Map specific topics to broader categories"""
        topic_mapping = {
            'variables': 'basics', 'data_types': 'basics', 'io': 'basics',
            'operators': 'basics', 'expressions': 'basics',
            'if_else': 'control_flow', 'loops': 'control_flow', 'switch': 'control_flow',
            'functions': 'functions', 'scope': 'functions', 'parameters': 'functions',
            'arrays': 'arrays', 'strings': 'arrays', 'multidimensional': 'arrays',
            'pointers': 'pointers', 'memory': 'pointers', 'dynamic_allocation': 'pointers'
        }
        return topic_mapping.get(topic_area, 'basics')
    
    def _update_skill_profile(self, user_id: int, topic_scores: Dict, topic_counts: Dict,
                            skill_level: SkillLevel, calculated_level: int):
        """Update user's skill profile based on assessment"""
        profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = UserSkillProfile(user_id=user_id)
            self.db.add(profile)
        
        # Update topic mastery scores (0.0 to 1.0)
        for topic, score in topic_scores.items():
            count = topic_counts[topic]
            mastery = score / count if count > 0 else 0.0
            
            if topic == 'basics':
                profile.basics_mastery = mastery
            elif topic == 'control_flow':
                profile.control_flow_mastery = mastery
            elif topic == 'functions':
                profile.functions_mastery = mastery
            elif topic == 'arrays':
                profile.arrays_mastery = mastery
            elif topic == 'pointers':
                profile.pointers_mastery = mastery
        
        profile.overall_skill_level = skill_level
        profile.adaptive_level = calculated_level
        
        self.db.commit()
    
    def get_adaptive_difficulty(self, user_id: int, lesson: Lesson) -> DifficultyLevel:
        """Determine appropriate difficulty for a lesson based on user's skill profile"""
        profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        if not profile:
            return lesson.difficulty  # Use default difficulty
        
        # Get topic-specific mastery
        topic_mastery = self._get_topic_mastery(profile, lesson)
        
        # Adjust difficulty based on mastery and preferences
        base_difficulty = lesson.difficulty
        
        if topic_mastery < 0.3:
            # User struggles with this topic, make it easier
            if base_difficulty == DifficultyLevel.ADVANCED:
                return DifficultyLevel.INTERMEDIATE
            elif base_difficulty == DifficultyLevel.INTERMEDIATE:
                return DifficultyLevel.BEGINNER
        elif topic_mastery > 0.8 and profile.prefers_challenge:
            # User masters this topic and likes challenges
            if base_difficulty == DifficultyLevel.BEGINNER:
                return DifficultyLevel.INTERMEDIATE
            elif base_difficulty == DifficultyLevel.INTERMEDIATE:
                return DifficultyLevel.ADVANCED
        
        return base_difficulty
    
    def _get_topic_mastery(self, profile: UserSkillProfile, lesson: Lesson) -> float:
        """Get user's mastery level for the lesson's topic area"""
        level_num = lesson.level.level_number if lesson.level else 1
        
        if level_num <= 2:
            return profile.basics_mastery
        elif level_num <= 4:
            return profile.basics_mastery
        elif level_num <= 6:
            return profile.control_flow_mastery
        elif level_num <= 7:
            return profile.functions_mastery
        elif level_num <= 9:
            return profile.arrays_mastery
        else:
            return profile.pointers_mastery
    
    def generate_adaptive_question(self, user_id: int, lesson: Lesson) -> Dict:
        """Generate a question with difficulty adapted to user's skill level"""
        adaptive_difficulty = self.get_adaptive_difficulty(user_id, lesson)
        
        # Use lesson title as topic for AI generation
        topic = lesson.title
        
        try:
            # Generate question with adaptive difficulty
            if lesson.lesson_type.value == "multiple_choice":
                question_data = self.ai_generator.generate_theory_question(topic, adaptive_difficulty)
            elif lesson.lesson_type.value == "coding_exercise":
                question_data = self.ai_generator.generate_coding_exercise(topic, adaptive_difficulty)
            else:
                question_data = self.ai_generator.generate_fill_in_blank(topic, adaptive_difficulty)
            
            # Log the adaptation
            self._log_difficulty_adaptation(user_id, lesson.id, lesson.difficulty, 
                                          adaptive_difficulty, "AI-generated adaptive question")
            
            return question_data
            
        except Exception as e:
            # Fallback to default difficulty if AI fails
            return {"error": f"Could not generate adaptive question: {str(e)}"}
    
    def _log_difficulty_adaptation(self, user_id: int, lesson_id: int, 
                                 original_difficulty: DifficultyLevel, 
                                 adjusted_difficulty: DifficultyLevel, reason: str):
        """Log difficulty adaptations for analysis"""
        log_entry = AdaptiveDifficultyLog(
            user_id=user_id,
            lesson_id=lesson_id,
            original_difficulty=original_difficulty.value,
            adjusted_difficulty=adjusted_difficulty.value,
            adaptation_reason=reason
        )
        self.db.add(log_entry)
        self.db.commit()
    
    def update_learning_velocity(self, user_id: int, lesson_performance: float):
        """Update user's learning velocity based on recent performance"""
        profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        if profile:
            # Adjust learning velocity (exponential moving average)
            alpha = 0.3  # Learning rate
            current_velocity = profile.learning_velocity
            new_velocity = alpha * lesson_performance + (1 - alpha) * current_velocity
            
            profile.learning_velocity = max(0.5, min(2.0, new_velocity))  # Clamp between 0.5 and 2.0
            
            # Update preferences based on performance
            if lesson_performance > 0.9:
                profile.prefers_challenge = True
            elif lesson_performance < 0.6:
                profile.needs_more_practice = True
                profile.prefers_challenge = False
            
            self.db.commit()
    
    def should_unlock_level(self, user_id: int, target_level: int) -> bool:
        """Determine if user should unlock a specific level based on adaptive assessment"""
        profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        if not profile:
            return target_level <= 1
        
        # Check if user's adaptive level meets the target
        if profile.adaptive_level >= target_level:
            return True
        
        # Check topic-specific mastery for early unlocking
        required_mastery = self._get_required_mastery_for_level(target_level)
        
        if target_level <= 2:
            return profile.basics_mastery >= required_mastery
        elif target_level <= 4:
            return profile.basics_mastery >= required_mastery
        elif target_level <= 6:
            return (profile.basics_mastery >= 0.7 and 
                   profile.control_flow_mastery >= required_mastery)
        elif target_level <= 7:
            return (profile.control_flow_mastery >= 0.7 and 
                   profile.functions_mastery >= required_mastery)
        elif target_level <= 9:
            return (profile.functions_mastery >= 0.7 and 
                   profile.arrays_mastery >= required_mastery)
        else:
            return (profile.arrays_mastery >= 0.7 and 
                   profile.pointers_mastery >= required_mastery)
    
    def _get_required_mastery_for_level(self, level: int) -> float:
        """Get required mastery percentage to unlock a level"""
        mastery_thresholds = {
            1: 0.0, 2: 0.3, 3: 0.5, 4: 0.6, 5: 0.7,
            6: 0.7, 7: 0.8, 8: 0.8, 9: 0.85, 10: 0.9
        }
        return mastery_thresholds.get(level, 0.5)
    
    def _get_ai_level_recommendation(self, responses: List, topic_mastery: Dict[str, float], accuracy: float) -> int:
        """Use AI to analyze user responses and provide level recommendation for edge cases"""
        try:
            # Prepare analysis prompt for AI
            response_analysis = []
            
            for response in responses:
                question = response.question
                response_analysis.append({
                    "topic": question.topic_area,
                    "expected_level": question.expected_level,
                    "difficulty_weight": question.difficulty_weight,
                    "user_answer": response.user_answer,
                    "correct_answer": question.correct_answer,
                    "is_correct": response.is_correct,
                    "confidence": response.confidence_level,
                    "time_taken": response.time_taken_seconds
                })
            
            # Create detailed prompt for AI analysis
            prompt = f"""
            Analyze this C programming skill assessment and recommend an appropriate starting level (1-10).
            
            ASSESSMENT RESULTS:
            - Overall Accuracy: {accuracy:.1%}
            - Topic Mastery Breakdown:
              * Basics: {topic_mastery.get('basics', 0):.1%}
              * Control Flow: {topic_mastery.get('control_flow', 0):.1%}
              * Functions: {topic_mastery.get('functions', 0):.1%}
              * Arrays: {topic_mastery.get('arrays', 0):.1%}
              * Pointers: {topic_mastery.get('pointers', 0):.1%}
            
            DETAILED RESPONSE PATTERNS:
            {self._format_response_patterns(response_analysis)}
            
            LEVEL STRUCTURE:
            - Levels 1-3: Variables, I/O, basic syntax, operators
            - Levels 4-6: Control flow (if/else, loops, switch)
            - Level 7: Functions, scope, parameters
            - Levels 8-9: Arrays, strings, multidimensional arrays
            - Level 10: Pointers, memory management, dynamic allocation
            
            ANALYSIS GUIDELINES:
            1. Foundation-first approach: Start where weakest fundamentals need work
            2. Look for knowledge gaps that indicate missing prerequisites
            3. Consider confidence patterns and response times
            4. Identify conceptual vs syntax issues
            5. Conservative recommendation (better to start easier and advance quickly)
            
            Based on this analysis, what level (1-10) should this user start at?
            Consider learning theory: it's better to reinforce weak foundations than struggle with advanced concepts.
            
            Respond with just the recommended level number (1-10) and a brief reason.
            Format: "Level X: [brief educational reasoning]"
            """
            
            # Call AI service
            ai_response = self.ai_generator.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert programming educator specializing in adaptive learning and skill assessment. Provide conservative, pedagogically sound level recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            ai_text = ai_response.choices[0].message.content.strip()
            
            # Extract level number from AI response
            import re
            level_match = re.search(r'Level (\d+)', ai_text)
            if level_match:
                ai_level = int(level_match.group(1))
                # Ensure level is within valid range
                ai_level = max(1, min(10, ai_level))
                
                print(f"  AI Analysis: {ai_text}")
                return ai_level
            else:
                # Fallback: conservative recommendation based on accuracy
                fallback_level = max(1, min(6, int(accuracy * 10)))
                print(f"  AI Parse Error: Using fallback level {fallback_level}")
                return fallback_level
                
        except Exception as e:
            # Fallback to conservative algorithmic approach if AI fails
            print(f"  AI Service Error: {e}")
            if accuracy < 0.4:
                return 1
            elif accuracy < 0.6:
                return 2
            elif accuracy < 0.8:
                return 4
            else:
                return 6  # Conservative even for high accuracy
    
    def _format_response_patterns(self, response_analysis: List[Dict]) -> str:
        """Format response patterns for AI analysis"""
        patterns = []
        
        for i, resp in enumerate(response_analysis, 1):
            confidence_desc = "Low" if resp["confidence"] < 3 else "Medium" if resp["confidence"] < 4 else "High"
            time_desc = "Quick" if resp["time_taken"] and resp["time_taken"] < 30 else "Normal" if resp["time_taken"] and resp["time_taken"] < 90 else "Slow"
            
            pattern = f"""
            Q{i}: {resp['topic']} (Level {resp['expected_level']})
            - Correct: {'✓' if resp['is_correct'] else '✗'}
            - Confidence: {confidence_desc}
            - Speed: {time_desc}
            - User answered: "{resp['user_answer'][:50]}{'...' if len(resp['user_answer']) > 50 else ''}"
            """
            patterns.append(pattern.strip())
        
        return "\n".join(patterns[:10])  # Limit to first 10 for token efficiency