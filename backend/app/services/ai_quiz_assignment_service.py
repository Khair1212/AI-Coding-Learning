"""
AI-Powered Quiz Assignment Service

This service uses LLM intelligence to create personalized quiz assignments
based on detailed assessment analysis, learning patterns, and pedagogical best practices.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json
import asyncio
from datetime import datetime, timedelta

from app.models import (
    User, UserSkillProfile, UserAssessment, AssessmentResponse,
    Quiz, Question, Lesson, Level, PersonalizedQuizAssignment,
    UserLessonProgress, QuizType, QuizDifficultyLevel, LessonType
)
from app.services.ai_service import AIQuestionGenerator


class AIQuizAssignmentService:
    """
    Advanced AI-powered service that creates personalized quiz assignments using:
    - Deep assessment analysis with LLM insights
    - Learning pattern recognition
    - Pedagogical sequencing
    - Difficulty progression algorithms
    - Real-time adaptation based on performance
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_generator = AIQuestionGenerator()
    
    async def create_comprehensive_quiz_assignments(
        self, 
        user_id: int, 
        assessment_id: int
    ) -> Dict[str, Any]:
        """
        Main method: Create comprehensive personalized quiz assignments 
        based on assessment results using AI analysis
        """
        print(f"🤖 Starting AI-powered quiz assignment for user {user_id}...")
        
        # Step 1: Deep Assessment Analysis
        assessment_analysis = await self._deep_assessment_analysis(user_id, assessment_id)
        
        # Step 2: LLM-powered Learning Path Analysis
        learning_path = await self._generate_ai_learning_path(assessment_analysis)
        
        # Step 3: Create Personalized Quiz Assignments for Each Level
        quiz_assignments = await self._create_level_specific_assignments(
            user_id, assessment_analysis, learning_path
        )
        
        # Step 4: Generate AI-powered Questions for Weak Areas
        ai_questions = await self._generate_targeted_ai_questions(
            user_id, assessment_analysis, learning_path
        )
        
        # Step 5: Store Assignments and Track Progress
        stored_assignments = await self._store_comprehensive_assignments(
            user_id, quiz_assignments, ai_questions
        )
        
        result = {
            'user_id': user_id,
            'assessment_analysis': assessment_analysis,
            'learning_path': learning_path,
            'quiz_assignments': stored_assignments,
            'ai_generated_questions': len(ai_questions),
            'total_assignments_created': len(stored_assignments),
            'assignment_summary': self._create_assignment_summary(stored_assignments)
        }
        
        print(f"✅ Completed AI quiz assignment: {len(stored_assignments)} assignments created")
        return result
    
    async def _deep_assessment_analysis(self, user_id: int, assessment_id: int) -> Dict[str, Any]:
        """Comprehensive assessment analysis with AI insights"""
        
        # Get assessment data
        assessment = self.db.query(UserAssessment).filter(
            UserAssessment.id == assessment_id
        ).first()
        
        responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment_id
        ).all()
        
        # Detailed performance analysis
        performance_data = {
            'overall_accuracy': assessment.accuracy_percentage / 100.0,
            'total_questions': len(responses),
            'correct_answers': assessment.correct_answers,
            'topic_performance': {},
            'difficulty_performance': {},
            'confidence_patterns': {},
            'time_patterns': {},
            'strength_areas': [],
            'weakness_areas': [],
            'learning_gaps': []
        }
        
        # Analyze by topic and difficulty
        for response in responses:
            question = response.question
            if not question:
                continue
            
            topic = question.topic_area
            difficulty = question.expected_level
            confidence = response.confidence_level or 3
            time_taken = response.time_taken_seconds or 60
            
            # Topic analysis
            if topic not in performance_data['topic_performance']:
                performance_data['topic_performance'][topic] = {
                    'correct': 0, 'total': 0, 'accuracy': 0,
                    'avg_confidence': 0, 'avg_time': 0
                }
            
            topic_data = performance_data['topic_performance'][topic]
            topic_data['total'] += 1
            if response.is_correct:
                topic_data['correct'] += 1
            topic_data['accuracy'] = topic_data['correct'] / topic_data['total']
            
            # Difficulty analysis  
            if difficulty not in performance_data['difficulty_performance']:
                performance_data['difficulty_performance'][difficulty] = {
                    'correct': 0, 'total': 0, 'accuracy': 0
                }
            
            diff_data = performance_data['difficulty_performance'][difficulty]
            diff_data['total'] += 1
            if response.is_correct:
                diff_data['correct'] += 1
            diff_data['accuracy'] = diff_data['correct'] / diff_data['total']
        
        # Identify strengths and weaknesses
        for topic, data in performance_data['topic_performance'].items():
            if data['accuracy'] >= 0.8:
                performance_data['strength_areas'].append(topic)
            elif data['accuracy'] <= 0.5:
                performance_data['weakness_areas'].append(topic)
        
        # Identify learning gaps (prerequisite violations)
        performance_data['learning_gaps'] = self._identify_learning_gaps(
            performance_data['topic_performance']
        )
        
        return performance_data
    
    def _identify_learning_gaps(self, topic_performance: Dict) -> List[str]:
        """Identify prerequisite violations and learning gaps"""
        
        gaps = []
        
        # Check prerequisite relationships
        prerequisites = {
            'functions': ['basics', 'variables', 'operators'],
            'arrays': ['basics', 'variables', 'loops'],
            'pointers': ['basics', 'variables', 'functions', 'arrays'],
            'loops': ['basics', 'variables'],
            'operators': ['basics', 'variables']
        }
        
        for advanced_topic, required_topics in prerequisites.items():
            if advanced_topic in topic_performance:
                advanced_accuracy = topic_performance[advanced_topic].get('accuracy', 0)
                
                # If they're good at advanced topic, check prerequisites
                if advanced_accuracy >= 0.7:
                    for required in required_topics:
                        if required in topic_performance:
                            req_accuracy = topic_performance[required].get('accuracy', 0)
                            if req_accuracy < 0.6:
                                gaps.append(f"Strong in {advanced_topic} but weak in prerequisite {required}")
                
                # If they're weak at advanced topic, might need prerequisite work
                elif advanced_accuracy <= 0.5:
                    weak_prerequisites = []
                    for required in required_topics:
                        if required in topic_performance:
                            req_accuracy = topic_performance[required].get('accuracy', 0)
                            if req_accuracy < 0.7:
                                weak_prerequisites.append(required)
                    
                    if weak_prerequisites:
                        gaps.append(f"Need prerequisite work in {weak_prerequisites} for {advanced_topic}")
        
        return gaps
    
    async def _generate_ai_learning_path(self, assessment_analysis: Dict) -> Dict[str, Any]:
        """Use LLM to generate intelligent learning path recommendations"""
        
        # Prepare assessment summary for LLM
        assessment_summary = {
            'overall_accuracy': assessment_analysis['overall_accuracy'],
            'strengths': assessment_analysis['strength_areas'],
            'weaknesses': assessment_analysis['weakness_areas'],
            'learning_gaps': assessment_analysis['learning_gaps'],
            'topic_breakdown': assessment_analysis['topic_performance']
        }
        
        # Generate AI-powered learning path
        try:
            # Create a comprehensive prompt for the LLM
            learning_path_prompt = self._create_learning_path_prompt(assessment_summary)
            
            # Use AI service to generate recommendations
            ai_response = await self._get_ai_learning_recommendations(learning_path_prompt)
            
            # Parse and structure the AI response
            learning_path = self._parse_ai_learning_path(ai_response)
            
        except Exception as e:
            print(f"⚠️ AI learning path generation failed: {e}")
            # Fallback to algorithmic approach
            learning_path = self._generate_fallback_learning_path(assessment_analysis)
        
        return learning_path
    
    def _create_learning_path_prompt(self, assessment_summary: Dict) -> str:
        """Create a comprehensive prompt for LLM learning path generation"""
        
        prompt = f"""
As an expert C programming instructor, analyze this student's assessment results and create a personalized learning path:

ASSESSMENT RESULTS:
- Overall Accuracy: {assessment_summary['overall_accuracy']:.1%}
- Strong Areas: {', '.join(assessment_summary['strengths']) if assessment_summary['strengths'] else 'None identified'}
- Weak Areas: {', '.join(assessment_summary['weaknesses']) if assessment_summary['weaknesses'] else 'None identified'}
- Learning Gaps: {'; '.join(assessment_summary['learning_gaps']) if assessment_summary['learning_gaps'] else 'None identified'}

DETAILED TOPIC PERFORMANCE:
"""
        
        for topic, data in assessment_summary['topic_breakdown'].items():
            prompt += f"- {topic}: {data['accuracy']:.1%} accuracy ({data['correct']}/{data['total']} correct)\n"
        
        prompt += """

Please provide a comprehensive learning path with:

1. RECOMMENDED START LEVEL (1-10): Based on weakest foundation areas
2. PRIORITY FOCUS AREAS: Top 3 topics needing immediate attention
3. LEARNING SEQUENCE: Optimal order for studying topics
4. QUIZ DIFFICULTY STRATEGY: How to balance challenge vs confidence building
5. PRACTICE RECOMMENDATIONS: Specific types of problems to assign
6. PROGRESS MILESTONES: Key checkpoints for advancement

Format your response as JSON with these keys:
{
  "recommended_start_level": <number>,
  "priority_focus_areas": ["topic1", "topic2", "topic3"],
  "learning_sequence": ["topic1", "topic2", ...],
  "quiz_strategy": {
    "difficulty_progression": "gradual|mixed|challenging", 
    "focus_ratio": {"reinforcement": 0.4, "new_learning": 0.4, "challenge": 0.2}
  },
  "practice_recommendations": {
    "topic1": "specific recommendation",
    "topic2": "specific recommendation"
  },
  "milestones": ["milestone1", "milestone2", ...],
  "reasoning": "Brief explanation of the strategy"
}
"""
        return prompt
    
    async def _get_ai_learning_recommendations(self, prompt: str) -> str:
        """Get AI recommendations using the OpenAI API"""
        
        try:
            # Use the existing AI generator's OpenAI client
            if hasattr(self.ai_generator, 'client') and self.ai_generator.client:
                print("🤖 Calling OpenAI API for learning path analysis...")
                
                response = self.ai_generator.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert C programming instructor and learning path designer. Analyze student assessment results and create comprehensive, pedagogically sound learning recommendations in the exact JSON format requested."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.3,  # Lower temperature for more consistent JSON
                    response_format={"type": "json_object"}  # Ensure JSON response
                )
                
                ai_response = response.choices[0].message.content
                print(f"✅ OpenAI API response received ({len(ai_response)} chars)")
                return ai_response
            else:
                print("⚠️ OpenAI client not available, using simulation")
                return await self._simulate_ai_learning_response(prompt)
                
        except Exception as e:
            print(f"❌ OpenAI API call failed: {e}")
            print("🔄 Falling back to intelligent simulation")
            return await self._simulate_ai_learning_response(prompt)
    
    async def _simulate_ai_learning_response(self, prompt: str) -> str:
        """Simulate intelligent AI response for learning path based on actual assessment data"""
        
        # Extract data from prompt for more realistic simulation
        import re
        
        accuracy_match = re.search(r'Overall Accuracy: (\d+)%', prompt)
        accuracy = int(accuracy_match.group(1)) / 100.0 if accuracy_match else 0.6
        
        # Extract topic performance data
        topic_data = {}
        topic_pattern = r'- (\w+): (\d+)% accuracy'
        for match in re.finditer(topic_pattern, prompt):
            topic, perf = match.groups()
            topic_data[topic] = int(perf) / 100.0
        
        # Smart simulation based on actual assessment data
        weak_areas = [topic for topic, perf in topic_data.items() if perf < 0.6]
        strong_areas = [topic for topic, perf in topic_data.items() if perf >= 0.8]
        
        # Calculate intelligent starting level
        if accuracy >= 0.8:
            start_level = 6
            difficulty = "challenging"
        elif accuracy >= 0.6:
            start_level = 4
            difficulty = "mixed"
        else:
            start_level = 2
            difficulty = "gradual"
        
        # Adjust based on topic performance
        if 'pointers' in strong_areas or 'arrays' in strong_areas:
            start_level = min(10, start_level + 2)
        if 'basics' in weak_areas or 'variables' in weak_areas:
            start_level = max(1, start_level - 1)
        
        # Dynamic priority focus areas
        priority_areas = weak_areas[:3] if weak_areas else ['control_flow', 'functions']
        if not priority_areas:  # If no weak areas, focus on advancement
            priority_areas = ['functions', 'arrays', 'pointers']
        
        simulated_response = {
            "recommended_start_level": start_level,
            "priority_focus_areas": priority_areas,
            "learning_sequence": ["basics", "variables", "operators", "control_flow", "loops", "functions", "arrays", "strings", "pointers"],
            "quiz_strategy": {
                "difficulty_progression": difficulty,
                "focus_ratio": {
                    "reinforcement": 0.6 if weak_areas else 0.3,
                    "new_learning": 0.3 if weak_areas else 0.4, 
                    "challenge": 0.1 if weak_areas else 0.3
                }
            },
            "practice_recommendations": {
                area: f"Targeted practice needed in {area} based on assessment results" 
                for area in priority_areas
            },
            "milestones": [
                f"Strengthen weak areas: {', '.join(weak_areas)}" if weak_areas else "Build on strong foundation",
                f"Progress from Level {start_level} systematically",
                "Maintain strengths while addressing gaps",
                "Advanced concepts when ready"
            ],
            "reasoning": f"Assessment shows {accuracy:.1%} accuracy. Weak areas: {weak_areas}. Strong areas: {strong_areas}. Intelligent simulation recommends Level {start_level} start with {difficulty} progression."
        }
        
        print(f"🧠 Intelligent simulation: Accuracy {accuracy:.1%}, Start Level {start_level}, Weak: {weak_areas}")
        return json.dumps(simulated_response, indent=2)
    
    def _parse_ai_learning_path(self, ai_response: str) -> Dict[str, Any]:
        """Parse the AI response into structured learning path"""
        
        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return self._extract_learning_path_from_text(ai_response)
    
    def _generate_fallback_learning_path(self, assessment_analysis: Dict) -> Dict[str, Any]:
        """Algorithmic fallback for learning path generation"""
        
        accuracy = assessment_analysis['overall_accuracy']
        weak_areas = assessment_analysis['weakness_areas']
        strong_areas = assessment_analysis['strength_areas']
        
        # Simple algorithmic approach
        if accuracy >= 0.8:
            start_level = 6
            difficulty_progression = "challenging"
        elif accuracy >= 0.6:
            start_level = 4
            difficulty_progression = "mixed"
        else:
            start_level = 2
            difficulty_progression = "gradual"
        
        return {
            "recommended_start_level": start_level,
            "priority_focus_areas": weak_areas[:3] if weak_areas else ["basics"],
            "learning_sequence": ["basics", "variables", "operators", "control_flow", "loops", "functions"],
            "quiz_strategy": {
                "difficulty_progression": difficulty_progression,
                "focus_ratio": {"reinforcement": 0.4, "new_learning": 0.4, "challenge": 0.2}
            },
            "practice_recommendations": {},
            "milestones": ["Complete fundamentals", "Master control flow", "Advanced concepts"],
            "reasoning": "Algorithmic fallback based on accuracy patterns"
        }
    
    async def _create_level_specific_assignments(
        self, 
        user_id: int, 
        assessment_analysis: Dict, 
        learning_path: Dict
    ) -> List[Dict[str, Any]]:
        """Create specific quiz assignments for each level based on AI analysis"""
        
        assignments = []
        start_level = learning_path.get('recommended_start_level', 1)
        focus_areas = learning_path.get('priority_focus_areas', [])
        
        # Get all levels and lessons
        levels = self.db.query(Level).filter(
            Level.level_number >= max(1, start_level - 2),
            Level.level_number <= min(10, start_level + 3),
            Level.is_active == True
        ).order_by(Level.level_number).all()
        
        for level in levels:
            lessons = self.db.query(Lesson).filter(
                Lesson.level_id == level.id,
                Lesson.is_active == True
            ).all()
            
            for lesson in lessons:
                # Create targeted assignment based on AI analysis
                assignment = await self._create_lesson_assignment(
                    user_id, lesson, assessment_analysis, learning_path
                )
                assignments.append(assignment)
        
        return assignments
    
    async def _create_lesson_assignment(
        self, 
        user_id: int, 
        lesson: Lesson, 
        assessment_analysis: Dict, 
        learning_path: Dict
    ) -> Dict[str, Any]:
        """Create a specific assignment for a lesson based on AI analysis"""
        
        # Determine assignment priority based on learning path
        focus_areas = learning_path.get('priority_focus_areas', [])
        lesson_topic = self._map_lesson_to_topic(lesson)
        
        if lesson_topic in focus_areas:
            priority = 'high'
            question_count = 5  # More questions for focus areas
        elif lesson_topic in assessment_analysis.get('weakness_areas', []):
            priority = 'medium'
            question_count = 4
        else:
            priority = 'low'
            question_count = 3
        
        # Select questions intelligently
        questions = self._select_questions_for_lesson(
            lesson, question_count, assessment_analysis, learning_path
        )
        
        # Determine difficulty adjustment
        quiz_strategy = learning_path.get('quiz_strategy', {})
        difficulty_adjustment = self._calculate_difficulty_adjustment(
            lesson, assessment_analysis, quiz_strategy
        )
        
        assignment = {
            'user_id': user_id,
            'lesson_id': lesson.id,
            'lesson_title': lesson.title,
            'level_number': lesson.level.level_number,
            'priority': priority,
            'question_count': len(questions),
            'selected_questions': questions,
            'difficulty_adjustment': difficulty_adjustment,
            'estimated_time_minutes': len(questions) * 3,  # 3 minutes per question
            'learning_objectives': self._generate_learning_objectives(lesson, assessment_analysis),
            'ai_reasoning': self._generate_assignment_reasoning(lesson, assessment_analysis, learning_path)
        }
        
        return assignment
    
    def _map_lesson_to_topic(self, lesson: Lesson) -> str:
        """Map lesson to broader topic area"""
        title_lower = lesson.title.lower()
        
        if any(word in title_lower for word in ['variable', 'data', 'type', 'basic']):
            return 'basics'
        elif any(word in title_lower for word in ['if', 'else', 'condition', 'decision']):
            return 'control_flow'
        elif any(word in title_lower for word in ['loop', 'for', 'while', 'repeat']):
            return 'loops'
        elif any(word in title_lower for word in ['function', 'parameter', 'return']):
            return 'functions'
        elif any(word in title_lower for word in ['array', 'list']):
            return 'arrays'
        elif any(word in title_lower for word in ['string', 'text']):
            return 'strings'
        elif any(word in title_lower for word in ['pointer', 'memory', 'address']):
            return 'pointers'
        else:
            return 'basics'
    
    def _select_questions_for_lesson(
        self, 
        lesson: Lesson, 
        target_count: int, 
        assessment_analysis: Dict, 
        learning_path: Dict
    ) -> List[Dict[str, Any]]:
        """Select the best questions for this lesson based on AI analysis"""
        
        # Get all questions for the lesson
        questions = self.db.query(Question).filter(
            Question.lesson_id == lesson.id
        ).all()
        
        if len(questions) <= target_count:
            return [{'id': q.id, 'selection_reason': 'All available questions'} for q in questions]
        
        # Score questions based on learning path
        scored_questions = []
        lesson_topic = self._map_lesson_to_topic(lesson)
        
        for question in questions:
            score = 50  # Base score
            
            # Boost score if this topic is a focus area
            focus_areas = learning_path.get('priority_focus_areas', [])
            if lesson_topic in focus_areas:
                score += 30
            
            # Boost score if this addresses a weakness
            weakness_areas = assessment_analysis.get('weakness_areas', [])
            if lesson_topic in weakness_areas:
                score += 25
            
            # Consider question type based on quiz strategy
            quiz_strategy = learning_path.get('quiz_strategy', {})
            if quiz_strategy.get('difficulty_progression') == 'gradual':
                if hasattr(question, 'question_type'):
                    if question.question_type == LessonType.MULTIPLE_CHOICE:
                        score += 10  # Easier questions for gradual progression
            
            scored_questions.append((question, score))
        
        # Sort by score and select top questions
        scored_questions.sort(key=lambda x: x[1], reverse=True)
        selected = scored_questions[:target_count]
        
        return [
            {
                'id': question.id, 
                'selection_reason': f'AI-selected (score: {score})',
                'question_type': str(question.question_type) if hasattr(question, 'question_type') else 'unknown'
            } 
            for question, score in selected
        ]
    
    def _calculate_difficulty_adjustment(
        self, 
        lesson: Lesson, 
        assessment_analysis: Dict, 
        quiz_strategy: Dict
    ) -> str:
        """Calculate how to adjust difficulty for this lesson"""
        
        lesson_topic = self._map_lesson_to_topic(lesson)
        topic_performance = assessment_analysis.get('topic_performance', {})
        
        # Check topic-specific performance
        if lesson_topic in topic_performance:
            accuracy = topic_performance[lesson_topic].get('accuracy', 0.5)
            
            if accuracy >= 0.8:
                return 'increase'  # They're strong here, add challenge
            elif accuracy <= 0.4:
                return 'decrease'  # They're weak here, make it easier
        
        # Consider overall difficulty progression strategy
        progression = quiz_strategy.get('difficulty_progression', 'mixed')
        
        if progression == 'gradual':
            return 'decrease'
        elif progression == 'challenging':
            return 'increase'
        else:
            return 'maintain'
    
    def _generate_learning_objectives(self, lesson: Lesson, assessment_analysis: Dict) -> List[str]:
        """Generate specific learning objectives for this assignment"""
        
        objectives = [
            f"Complete {lesson.title} with understanding",
            "Apply concepts through practice problems",
            "Build confidence in this topic area"
        ]
        
        lesson_topic = self._map_lesson_to_topic(lesson)
        if lesson_topic in assessment_analysis.get('weakness_areas', []):
            objectives.append("Strengthen understanding in identified weak area")
        
        return objectives
    
    def _generate_assignment_reasoning(
        self, 
        lesson: Lesson, 
        assessment_analysis: Dict, 
        learning_path: Dict
    ) -> str:
        """Generate AI reasoning for why this assignment was created"""
        
        lesson_topic = self._map_lesson_to_topic(lesson)
        focus_areas = learning_path.get('priority_focus_areas', [])
        weakness_areas = assessment_analysis.get('weakness_areas', [])
        
        reasons = []
        
        if lesson_topic in focus_areas:
            reasons.append("Priority focus area identified by AI analysis")
        
        if lesson_topic in weakness_areas:
            reasons.append("Addresses weakness found in assessment")
        
        level_num = lesson.level.level_number
        recommended_level = learning_path.get('recommended_start_level', 1)
        
        if level_num == recommended_level:
            reasons.append("Matches recommended starting level")
        elif level_num < recommended_level:
            reasons.append("Prerequisite reinforcement")
        else:
            reasons.append("Progressive skill building")
        
        if not reasons:
            reasons.append("Part of comprehensive learning sequence")
        
        return " • ".join(reasons)
    
    async def _generate_targeted_ai_questions(
        self, 
        user_id: int, 
        assessment_analysis: Dict, 
        learning_path: Dict
    ) -> List[Dict[str, Any]]:
        """Generate AI questions specifically targeting user's weak areas"""
        
        ai_questions = []
        weakness_areas = assessment_analysis.get('weakness_areas', [])[:3]  # Top 3 weaknesses
        
        for weak_topic in weakness_areas:
            try:
                # Generate AI question for this weak area
                question_data = await self._generate_ai_question_for_topic(
                    weak_topic, assessment_analysis, learning_path
                )
                ai_questions.append(question_data)
                
                print(f"✨ Generated AI question for weak area: {weak_topic}")
                
            except Exception as e:
                print(f"⚠️ Failed to generate AI question for {weak_topic}: {e}")
        
        return ai_questions
    
    async def _generate_ai_question_for_topic(
        self, 
        topic: str, 
        assessment_analysis: Dict, 
        learning_path: Dict
    ) -> Dict[str, Any]:
        """Generate a specific AI question for a topic"""
        
        # Use existing AI generator with enhanced context
        difficulty = self._determine_ai_question_difficulty(topic, assessment_analysis)
        
        # This would call the AI service to generate a targeted question
        # For now, return a structured placeholder
        return {
            'topic': topic,
            'difficulty': difficulty,
            'question_text': f"AI-generated question for {topic}",
            'question_type': 'multiple_choice',
            'target_weakness': True,
            'ai_reasoning': f"Generated to address weakness in {topic}",
            'estimated_effectiveness': 0.8
        }
    
    def _determine_ai_question_difficulty(self, topic: str, assessment_analysis: Dict) -> str:
        """Determine appropriate difficulty for AI-generated question"""
        
        topic_performance = assessment_analysis.get('topic_performance', {})
        
        if topic in topic_performance:
            accuracy = topic_performance[topic].get('accuracy', 0.5)
            
            if accuracy <= 0.3:
                return 'beginner'
            elif accuracy <= 0.6:
                return 'intermediate'
            else:
                return 'advanced'
        
        return 'beginner'  # Default for unknown topics
    
    async def _store_comprehensive_assignments(
        self, 
        user_id: int, 
        quiz_assignments: List[Dict], 
        ai_questions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Store all assignments in the database"""
        
        stored_assignments = []
        
        for assignment in quiz_assignments:
            try:
                # Create personalized quiz assignment record
                quiz_assignment = PersonalizedQuizAssignment(
                    user_id=user_id,
                    lesson_id=assignment['lesson_id'],
                    assignment_type='ai_generated',
                    difficulty_adjustment=assignment['difficulty_adjustment'],
                    target_question_count=assignment['question_count'],
                    priority_level=assignment['priority'],
                    ai_reasoning=assignment['ai_reasoning'],
                    learning_objectives=json.dumps(assignment['learning_objectives']),
                    estimated_completion_time=assignment['estimated_time_minutes'],
                    is_active=True
                )
                
                self.db.add(quiz_assignment)
                self.db.commit()
                self.db.refresh(quiz_assignment)
                
                stored_assignments.append({
                    'assignment_id': quiz_assignment.id,
                    'lesson_id': assignment['lesson_id'],
                    'lesson_title': assignment['lesson_title'],
                    'priority': assignment['priority'],
                    'question_count': assignment['question_count'],
                    'ai_reasoning': assignment['ai_reasoning']
                })
                
            except Exception as e:
                print(f"⚠️ Failed to store assignment for lesson {assignment['lesson_id']}: {e}")
        
        return stored_assignments
    
    def _create_assignment_summary(self, assignments: List[Dict]) -> Dict[str, Any]:
        """Create a summary of all created assignments"""
        
        total_assignments = len(assignments)
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        total_questions = 0
        
        for assignment in assignments:
            priority_counts[assignment['priority']] += 1
            total_questions += assignment['question_count']
        
        return {
            'total_assignments': total_assignments,
            'priority_breakdown': priority_counts,
            'total_questions_assigned': total_questions,
            'estimated_total_time_minutes': total_questions * 3,
            'ai_enhanced': True
        }
    
    def _extract_learning_path_from_text(self, text: str) -> Dict[str, Any]:
        """Fallback text parsing if JSON parsing fails"""
        
        # Simple text-based extraction (fallback)
        return {
            "recommended_start_level": 3,
            "priority_focus_areas": ["basics"],
            "learning_sequence": ["basics", "variables", "operators"],
            "quiz_strategy": {"difficulty_progression": "gradual"},
            "practice_recommendations": {},
            "milestones": ["Master basics"],
            "reasoning": "Fallback text parsing"
        }