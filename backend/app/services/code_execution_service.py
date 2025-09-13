"""
Code Execution Service for evaluating C programming exercises
Safely executes user-submitted C code and compares output with expected results
"""
import os
import subprocess
import tempfile
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TestCase:
    """Represents a test case with input and expected output"""
    input: str = ""
    expected_output: str = ""
    description: str = ""

@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: str = ""
    error: str = ""
    compilation_error: str = ""
    execution_time: float = 0.0

class CodeExecutionService:
    """Service for safely executing C code and comparing outputs"""
    
    def __init__(self):
        self.compile_timeout = 10  # seconds
        self.execution_timeout = 5  # seconds
        self.max_output_length = 10000  # characters
    
    def evaluate_code_exercise(self, user_code: str, test_cases_json: str) -> Tuple[bool, Dict]:
        """
        Evaluate a coding exercise by running the code against test cases
        
        Args:
            user_code: The user's C code submission
            test_cases_json: JSON string containing test cases
            
        Returns:
            Tuple of (is_correct, detailed_results)
        """
        try:
            # Parse test cases
            test_cases = self._parse_test_cases(test_cases_json)
            if not test_cases:
                # Fallback: create a simple test case for basic programs
                test_cases = [TestCase(input="", expected_output="", description="Basic execution test")]
            
            # Compile the code
            compilation_result = self._compile_code(user_code)
            if not compilation_result.success:
                return False, {
                    "error": "Compilation failed",
                    "compilation_error": compilation_result.compilation_error,
                    "passed_tests": 0,
                    "total_tests": len(test_cases)
                }
            
            # Run test cases
            results = []
            passed_count = 0
            
            for i, test_case in enumerate(test_cases):
                # Don't clean up executable until all tests are done
                execution_result = self._execute_code(compilation_result.output, test_case.input, cleanup=(i == len(test_cases) - 1))
                
                if execution_result.success:
                    # Compare outputs
                    is_match = self._compare_outputs(execution_result.output, test_case.expected_output)
                    if is_match:
                        passed_count += 1
                    
                    results.append({
                        "test_case": i + 1,
                        "description": test_case.description,
                        "input": test_case.input,
                        "expected_output": test_case.expected_output,
                        "actual_output": execution_result.output,
                        "passed": is_match,
                        "error": execution_result.error
                    })
                else:
                    results.append({
                        "test_case": i + 1,
                        "description": test_case.description,
                        "input": test_case.input,
                        "expected_output": test_case.expected_output,
                        "actual_output": "",
                        "passed": False,
                        "error": execution_result.error
                    })
            
            # Determine if exercise is correct (all tests must pass)
            is_correct = passed_count == len(test_cases)
            
            return is_correct, {
                "passed_tests": passed_count,
                "total_tests": len(test_cases),
                "test_results": results,
                "success_rate": passed_count / len(test_cases) if test_cases else 0
            }
            
        except Exception as e:
            return False, {
                "error": f"Evaluation error: {str(e)}",
                "passed_tests": 0,
                "total_tests": 0
            }
    
    def _parse_test_cases(self, test_cases_json: str) -> List[TestCase]:
        """Parse test cases from JSON string"""
        if not test_cases_json or test_cases_json.strip() == "":
            return []
        
        try:
            data = json.loads(test_cases_json)
            test_cases = []
            
            if isinstance(data, list):
                for case in data:
                    test_cases.append(TestCase(
                        input=case.get("input", ""),
                        expected_output=case.get("expected_output", ""),
                        description=case.get("description", f"Test case {len(test_cases) + 1}")
                    ))
            elif isinstance(data, dict):
                # Single test case
                test_cases.append(TestCase(
                    input=data.get("input", ""),
                    expected_output=data.get("expected_output", ""),
                    description=data.get("description", "Test case")
                ))
            
            return test_cases
        except json.JSONDecodeError:
            return []
    
    def _compile_code(self, code: str) -> ExecutionResult:
        """Compile C code and return compilation result"""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as source_file:
                source_file.write(code)
                source_path = source_file.name
            
            # Output executable path
            executable_path = source_path.replace('.c', '')
            
            # Compile command
            compile_cmd = [
                'gcc',
                '-o', executable_path,
                source_path,
                '-std=c99',  # Use C99 standard
                '-Wall',     # Enable warnings
                '-Wextra'    # Extra warnings
            ]
            
            # Run compilation
            try:
                result = subprocess.run(
                    compile_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.compile_timeout
                )
                
                # Clean up source file
                os.unlink(source_path)
                
                if result.returncode == 0:
                    return ExecutionResult(
                        success=True,
                        output=executable_path
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        compilation_error=result.stderr
                    )
                    
            except subprocess.TimeoutExpired:
                os.unlink(source_path)
                return ExecutionResult(
                    success=False,
                    compilation_error="Compilation timeout"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                compilation_error=f"Compilation error: {str(e)}"
            )
    
    def _execute_code(self, executable_path: str, input_data: str, cleanup: bool = True) -> ExecutionResult:
        """Execute compiled code with given input"""
        try:
            # Run the executable
            result = subprocess.run(
                [executable_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.execution_timeout
            )
            
            # Clean up executable only if requested
            if cleanup and os.path.exists(executable_path):
                os.unlink(executable_path)
            
            # Limit output length
            output = result.stdout
            if len(output) > self.max_output_length:
                output = output[:self.max_output_length] + "... (truncated)"
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=output,
                error=result.stderr if result.returncode != 0 else ""
            )
            
        except subprocess.TimeoutExpired:
            if cleanup and os.path.exists(executable_path):
                os.unlink(executable_path)
            return ExecutionResult(
                success=False,
                error="Execution timeout"
            )
        except Exception as e:
            if cleanup and os.path.exists(executable_path):
                os.unlink(executable_path)
            return ExecutionResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    def _compare_outputs(self, actual: str, expected: str) -> bool:
        """Compare actual output with expected output"""
        if not expected:  # If no expected output specified, just check if it runs
            return True
        
        # Normalize both outputs
        actual_normalized = self._normalize_output(actual)
        expected_normalized = self._normalize_output(expected)
        
        return actual_normalized == expected_normalized
    
    def _normalize_output(self, output: str) -> str:
        """Normalize output for comparison"""
        if not output:
            return ""
        
        # Remove trailing whitespace and normalize line endings
        normalized = output.strip()
        normalized = re.sub(r'\r\n|\r', '\n', normalized)
        
        # Remove extra spaces between words (but preserve intentional spacing)
        lines = normalized.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Strip trailing spaces but preserve leading spaces for formatting
            line = line.rstrip()
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def create_simple_test_case(self, expected_output: str, input_data: str = "") -> str:
        """Create a simple test case JSON for basic programs"""
        test_case = {
            "input": input_data,
            "expected_output": expected_output,
            "description": "Basic output test"
        }
        return json.dumps([test_case])
    
    def create_interactive_test_cases(self, interactions: List[Dict]) -> str:
        """
        Create test cases for interactive programs
        
        Args:
            interactions: List of {"input": "...", "expected_output": "...", "description": "..."}
        """
        return json.dumps(interactions)

# Example usage and helper functions
def create_hello_world_test_case():
    """Create test case for Hello World program"""
    service = CodeExecutionService()
    return service.create_simple_test_case("Hello, World!")

def create_addition_test_cases():
    """Create test cases for addition program"""
    test_cases = [
        {
            "input": "5\n3\n",
            "expected_output": "Enter the first number: Enter the second number: The sum of 5 and 3 is 8",
            "description": "Addition of 5 and 3"
        },
        {
            "input": "10\n20\n",
            "expected_output": "Enter the first number: Enter the second number: The sum of 10 and 20 is 30",
            "description": "Addition of 10 and 20"
        }
    ]
    return json.dumps(test_cases)
