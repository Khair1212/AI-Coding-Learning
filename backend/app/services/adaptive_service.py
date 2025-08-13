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
        """Calculate user's skill level based on assessment results with improved logic"""
        if not assessment.is_completed:
            return 1, SkillLevel.COMPLETE_BEGINNER
        
        accuracy = assessment.accuracy_percentage / 100.0
        responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment.id
        ).all()
        
        if not responses:
            return 1, SkillLevel.COMPLETE_BEGINNER
        
        # Enhanced topic mapping for better granularity
        topic_scores = {}
        topic_counts = {}
        level_performance = {}  # Track performance by difficulty level
        
        # Analyze all responses
        for response in responses:
            question = response.question
            if not question:
                continue
                
            topic = question.topic_area
            level = question.expected_level
            
            # Track by topic
            if topic not in topic_scores:
                topic_scores[topic] = 0
                topic_counts[topic] = 0
            topic_counts[topic] += 1
            if response.is_correct:
                topic_scores[topic] += 1
            
            # Track by difficulty level
            if level not in level_performance:
                level_performance[level] = {'correct': 0, 'total': 0}
            level_performance[level]['total'] += 1
            if response.is_correct:
                level_performance[level]['correct'] += 1
        
        # Calculate topic mastery rates
        topic_mastery = {}
        for topic, score in topic_scores.items():
            count = topic_counts[topic]
            mastery = score / count if count > 0 else 0.0
            topic_mastery[topic] = mastery
        
        # Smart level calculation based on performance patterns
        calculated_level = self._calculate_intelligent_level(
            accuracy, topic_mastery, level_performance
        )
        
        # Determine skill level based on overall performance
        skill_level = self._determine_skill_level(accuracy, topic_mastery, calculated_level)
        
        # Debug logging
        print(f"🎯 Improved Assessment Analysis:")
        print(f"   Overall Accuracy: {accuracy:.1%}")
        print(f"   Topic Breakdown: {topic_mastery}")
        print(f"   Level Performance: {level_performance}")
        print(f"   Calculated Level: {calculated_level}")
        print(f"   Skill Level: {skill_level.value}")
        
        # Update user skill profile
        self._update_enhanced_skill_profile(
            assessment.user_id, topic_mastery, skill_level, calculated_level
        )
        
        return calculated_level, skill_level
    
    def _calculate_intelligent_level(self, accuracy: float, topic_mastery: dict, level_performance: dict) -> int:
        """Dynamic progression-based level calculation - recommends NEXT level to learn"""
        
        # Map topics to their corresponding course levels 
        topic_level_mapping = {
            'basics': 1,
            'variables': 2,
            'operators': 3,
            'loops': 4,
            'functions': 5,
            'arrays': 6,
            'strings': 7,
            'pointers': 8,
            'memory': 9,
            'memory_management': 9
        }
        
        # Find the highest level user has MASTERED (70%+ proficiency)
        mastered_levels = []
        
        print(f"🎯 Dynamic Level Assessment:")
        
        for topic, mastery_rate in topic_mastery.items():
            topic_key = topic.lower().replace(' ', '_')
            topic_level = topic_level_mapping.get(topic_key, 1)
            
            print(f"   {topic}: {mastery_rate:.1%} → Level {topic_level}")
            
            # Consider a topic mastered if 70%+ proficiency
            if mastery_rate >= 0.7:
                mastered_levels.append(topic_level)
                print(f"     ✅ MASTERED! Level {topic_level}")
            elif mastery_rate >= 0.5:
                print(f"     🟡 Partially learned (50%+)")
            else:
                print(f"     ❌ Needs work (<50%)")
        
        if mastered_levels:
            highest_mastered = max(mastered_levels)
            recommended_level = min(10, highest_mastered + 1)  # Next level after mastered
            
            print(f"   📈 Highest Mastered Level: {highest_mastered}")
            print(f"   🎯 Recommended Next Level: {recommended_level}")
            
            # If user has mastered levels 1-9, they're ready for level 10
            if highest_mastered >= 9:
                return 10
            else:
                return recommended_level
        else:
            # No topics mastered - start from level 1
            print(f"   🔄 No topics mastered yet - Start with Level 1")
            return 1
    
    def _get_performance_based_level(self, level_performance: dict) -> float:
        """Calculate level based on performance at different difficulty levels"""
        
        if not level_performance:
            return 1.0
        
        # Find the highest level where user has > 50% accuracy
        max_competent_level = 0
        total_weighted_score = 0
        total_weight = 0
        
        for level, data in level_performance.items():
            total = data['total']
            correct = data['correct']
            
            if total > 0:
                accuracy_at_level = correct / total
                # Weight by level difficulty
                weight = level * total  # Higher levels and more questions = more weight
                total_weighted_score += accuracy_at_level * weight
                total_weight += weight
                
                # Track highest level with decent performance
                if accuracy_at_level >= 0.5:  # 50% threshold
                    max_competent_level = max(max_competent_level, level)
        
        if total_weight > 0:
            weighted_avg_performance = total_weighted_score / total_weight
            # Blend max competent level with weighted average
            return (max_competent_level * 0.7 + weighted_avg_performance * 10 * 0.3)
        
        return 1.0
    
    def _get_topic_based_level(self, topic_mastery: dict) -> float:
        """Calculate level based on topic mastery patterns"""
        
        # Map topics to their corresponding course levels (case-insensitive)
        topic_level_mapping = {
            'basics': 1,
            'variables': 2, 
            'operators': 3,
            'control_flow': 4,
            'loops': 5,
            'functions': 6,
            'arrays': 7,
            'strings': 8,
            'pointers': 9,
            'memory': 10,
            'memory_management': 10,  # Alternative name
            'memory management': 10   # Spaced version
        }
        
        # Calculate level based on strongest topics
        max_mastered_level = 0
        mastery_scores = []
        
        print(f"🔍 Topic-based level calculation:")
        
        for topic, mastery in topic_mastery.items():
            # Make comparison case-insensitive and handle spaces
            topic_key = topic.lower().replace(' ', '_')
            topic_level = topic_level_mapping.get(topic_key, 1)
            
            print(f"   {topic} (key: {topic_key}) → Level {topic_level}, Mastery: {mastery:.1%}")
            
            if mastery >= 0.7:  # 70% mastery threshold
                max_mastered_level = max(max_mastered_level, topic_level)
                print(f"     ✅ Mastered! New max level: {max_mastered_level}")
            
            # Weight mastery by topic difficulty
            mastery_scores.append(mastery * topic_level)
        
        if mastery_scores:
            avg_weighted_mastery = sum(mastery_scores) / len(mastery_scores)
            # Blend max mastered level with weighted average
            final_level = max_mastered_level * 0.6 + avg_weighted_mastery * 0.4
            print(f"   📊 Max mastered level: {max_mastered_level}")
            print(f"   📊 Avg weighted mastery: {avg_weighted_mastery:.2f}")
            print(f"   📊 Final topic-based level: {final_level:.2f}")
            return final_level
        
        print(f"   ⚠️ No mastery scores found, returning 1.0")
        return 1.0
    
    def _get_accuracy_based_level(self, accuracy: float) -> float:
        """Simple accuracy to level mapping"""
        if accuracy >= 1.0:
            return 10.0  # Perfect accuracy = expert level
        elif accuracy >= 0.95:
            return 9.0   # Near perfect = advanced expert
        elif accuracy >= 0.9:
            return 8.0   # Very high accuracy = advanced
        elif accuracy >= 0.8:
            return 6.0   # High accuracy = intermediate-advanced
        elif accuracy >= 0.7:
            return 4.5   # Good accuracy = intermediate
        elif accuracy >= 0.6:
            return 3.0   # Decent accuracy = beginner-intermediate
        elif accuracy >= 0.5:
            return 2.0   # Fair accuracy = beginner
        else:
            return 1.0   # Low accuracy = complete beginner
    
    def _determine_skill_level(self, accuracy: float, topic_mastery: dict, calculated_level: int) -> SkillLevel:
        """Determine skill level based on highest mastered level (dynamic progression)"""
        
        # Map topics to levels and find highest mastered level
        topic_level_mapping = {
            'basics': 1, 'variables': 2, 'operators': 3, 'loops': 4, 'functions': 5,
            'arrays': 6, 'strings': 7, 'pointers': 8, 'memory': 9, 'memory_management': 9
        }
        
        mastered_levels = []
        for topic, mastery_rate in topic_mastery.items():
            topic_key = topic.lower().replace(' ', '_')
            topic_level = topic_level_mapping.get(topic_key, 1)
            if mastery_rate >= 0.7:  # 70%+ considered mastered
                mastered_levels.append(topic_level)
        
        highest_mastered = max(mastered_levels) if mastered_levels else 0
        
        print(f"🎯 Dynamic Skill Level Assessment:")
        print(f"   Highest Mastered Level: {highest_mastered}")
        print(f"   Recommended Next Level: {calculated_level}")
        
        # Dynamic skill level based on progression, not static accuracy
        if highest_mastered >= 8:  # Mastered advanced topics (Pointers/Memory)
            print(f"   → EXPERT: Mastered advanced concepts through Level {highest_mastered}")
            return SkillLevel.EXPERT
        elif highest_mastered >= 6:  # Mastered intermediate topics (Arrays/Strings)
            print(f"   → ADVANCED: Mastered intermediate concepts through Level {highest_mastered}")
            return SkillLevel.ADVANCED
        elif highest_mastered >= 4:  # Mastered basic programming (Loops/Functions)
            print(f"   → INTERMEDIATE: Mastered basic programming through Level {highest_mastered}")
            return SkillLevel.INTERMEDIATE
        elif highest_mastered >= 2:  # Mastered fundamentals (Variables/Operators)
            print(f"   → BEGINNER: Mastered fundamentals through Level {highest_mastered}")
            return SkillLevel.BEGINNER
        else:  # No solid mastery yet
            print(f"   → COMPLETE_BEGINNER: Still learning fundamentals")
            return SkillLevel.COMPLETE_BEGINNER
    
    def _update_enhanced_skill_profile(self, user_id: int, topic_mastery: dict, 
                                     skill_level: SkillLevel, calculated_level: int):
        """Update skill profile with enhanced topic tracking"""
        
        profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = UserSkillProfile(user_id=user_id)
            self.db.add(profile)
        
        # Update mastery scores with actual topic data
        for topic, mastery in topic_mastery.items():
            normalized_topic = self._normalize_topic_name(topic)
            
            if normalized_topic == 'basics':
                profile.basics_mastery = mastery
            elif normalized_topic == 'control_flow':
                profile.control_flow_mastery = mastery
            elif normalized_topic == 'functions':
                profile.functions_mastery = mastery
            elif normalized_topic == 'arrays':
                profile.arrays_mastery = mastery
            elif normalized_topic == 'pointers':
                profile.pointers_mastery = mastery
        
        profile.overall_skill_level = skill_level
        profile.adaptive_level = calculated_level
        
        # Update learning characteristics
        avg_mastery = sum(topic_mastery.values()) / len(topic_mastery) if topic_mastery else 0
        profile.learning_velocity = min(2.0, max(0.5, avg_mastery * 1.5))
        profile.prefers_challenge = avg_mastery > 0.8
        profile.needs_more_practice = avg_mastery < 0.6
        
        self.db.commit()
    
    def _normalize_topic_name(self, topic: str) -> str:
        """Normalize topic names to standard categories"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['basic', 'variable', 'data', 'io', 'input', 'output']):
            return 'basics'
        elif any(word in topic_lower for word in ['loop', 'for', 'while', 'control', 'if', 'else']):
            return 'control_flow'  
        elif any(word in topic_lower for word in ['function', 'parameter', 'return']):
            return 'functions'
        elif any(word in topic_lower for word in ['array', 'string']):
            return 'arrays'
        elif any(word in topic_lower for word in ['pointer', 'memory', 'malloc']):
            return 'pointers'
        else:
            return 'basics'  # Default fallback
    
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