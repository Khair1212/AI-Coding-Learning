#!/usr/bin/env python3

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lesson import Question, LessonType
import json
import re

def fix_all_question_options():
    db = SessionLocal()
    try:
        print('=== FIXING ALL MULTIPLE CHOICE QUESTION OPTIONS ===')
        
        # Find all multiple choice questions
        questions = db.query(Question).filter(
            Question.question_type == LessonType.MULTIPLE_CHOICE
        ).all()
        
        print(f'Found {len(questions)} multiple choice questions to fix')
        
        for q in questions:
            if not q.options:
                print(f'Q{q.id}: No options to fix')
                continue
                
            print(f'Q{q.id}: {q.question_text[:50]}...')
            print(f'  Original: {q.options}')
            
            try:
                # Check if options are in JSON array format
                if q.options.startswith('[') and q.options.endswith(']'):
                    # Parse as JSON array
                    options_array = json.loads(q.options)
                    
                    # Convert to pipe-separated format
                    # Remove letter prefixes like "A. ", "B. " etc if present
                    cleaned_options = []
                    for option in options_array:
                        # Remove "A. ", "B. ", etc. prefixes
                        if re.match(r'^[A-D]\.\s+', option):
                            cleaned = option.split('. ', 1)[1]
                        else:
                            cleaned = option
                        cleaned_options.append(cleaned)
                    
                    # Join with pipes
                    pipe_format = '|'.join(cleaned_options)
                    q.options = pipe_format
                    
                    print(f'  Updated: {pipe_format}')
                    
                elif '|' in q.options:
                    print(f'  Already in pipe format')
                    
                else:
                    print(f'  Unknown format, skipping')
                    
            except Exception as e:
                print(f'  Error parsing options: {e}')
                
            print()
        
        db.commit()
        print('✅ Fixed all question options')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_question_options()