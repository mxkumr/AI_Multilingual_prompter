import ast
import json
import re
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict


class PythonASTParser:
    """
    A comprehensive AST parser for analyzing Python code from LLM outputs.
    Extracts functions, classes, variables, imports, and provides detailed analysis.
    """
    
    def __init__(self):
        self.analysis_results = {}
    
    def parse_code(self, code: str, language_code: str) -> Dict[str, Any]:
        """
        Parse Python code and extract detailed information.
        
        Args:
            code (str): Python code to parse
            language_code (str): Language identifier (e.g., 'en', 'zh-CN')
            
        Returns:
            Dict containing parsed information
        """
        if not code or not code.strip():
            return {
                'language': language_code,
                'has_code': False,
                'error': 'No code provided',
                'statistics': {},
                'elements': {}
            }
        
        try:
            # Clean the code first
            cleaned_code = self._clean_code(code)
            
            # Parse the AST
            tree = ast.parse(cleaned_code)
            
            # Extract information
            result = {
                'language': language_code,
                'has_code': True,
                'error': None,
                'statistics': self._extract_statistics(tree),
                'elements': self._extract_elements(tree),
                'raw_code': cleaned_code
            }
            
            return result
            
        except SyntaxError as e:
            return {
                'language': language_code,
                'has_code': True,
                'error': f'Syntax error: {str(e)}',
                'statistics': {},
                'elements': {},
                'raw_code': code
            }
        except Exception as e:
            return {
                'language': language_code,
                'has_code': True,
                'error': f'Parsing error: {str(e)}',
                'statistics': {},
                'elements': {},
                'raw_code': code
            }
    
    def _clean_code(self, code: str) -> str:
        """
        Clean the code by removing comments and fixing common issues.
        """
        if not code:
            return ""
        
        # First, try to extract code blocks from markdown
        code_blocks = re.findall(r'```(?:python)?\s*\n?(.*?)\n?```', code, re.DOTALL | re.IGNORECASE)
        
        if code_blocks:
            # Use the first code block found
            code = code_blocks[0]
        
        # Remove single-line comments and clean up
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines and comment-only lines
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Remove inline comments
            if '#' in line:
                line = line[:line.index('#')].rstrip()
                if not line:
                    continue
            
            cleaned_lines.append(line)
        
        cleaned_code = '\n'.join(cleaned_lines)
        
        # Try to fix common syntax errors
        cleaned_code = self._fix_common_errors(cleaned_code)
        
        return cleaned_code
    
    def _fix_common_errors(self, code: str) -> str:
        """
        Fix common syntax errors in the code.
        """
        if not code:
            return code
        
        # Fix unmatched parentheses
        # Count opening and closing parentheses
        open_parens = code.count('(')
        close_parens = code.count(')')
        
        if close_parens > open_parens:
            # Remove extra closing parentheses
            diff = close_parens - open_parens
            for _ in range(diff):
                # Find the last closing parenthesis and remove it
                last_close = code.rfind(')')
                if last_close != -1:
                    code = code[:last_close] + code[last_close + 1:]
        
        # Fix unmatched brackets
        open_brackets = code.count('[')
        close_brackets = code.count(']')
        
        if close_brackets > open_brackets:
            diff = close_brackets - open_brackets
            for _ in range(diff):
                last_close = code.rfind(']')
                if last_close != -1:
                    code = code[:last_close] + code[last_close + 1:]
        
        # Fix unmatched braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        
        if close_braces > open_braces:
            diff = close_braces - open_braces
            for _ in range(diff):
                last_close = code.rfind('}')
                if last_close != -1:
                    code = code[:last_close] + code[last_close + 1:]
        
        # Fix common f-string issues
        # Replace problematic f-string syntax
        code = re.sub(r'f"[^"]*\{[^}]*\}[^"]*"', lambda m: m.group(0).replace('{', '{{').replace('}', '}}'), code)
        
        # Remove trailing commas in function calls
        code = re.sub(r',\s*\)', ')', code)
        
        return code.strip()
    
    def save_individual_python_files(self, llm_output_file: str = "data/llm_output.json", output_dir: str = "data/python_files"):
        """
        Save each language's code as individual Python files.
        
        Args:
            llm_output_file (str): Path to the LLM output JSON file
            output_dir (str): Directory to save Python files
        """
        try:
            with open(llm_output_file, 'r', encoding='utf-8') as f:
                llm_outputs = json.load(f)
        except FileNotFoundError:
            print(f"Error: {llm_output_file} not found")
            return
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {llm_output_file}")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        for language_code, code in llm_outputs.items():
            if not code or not code.strip():
                print(f"Skipping {language_code}: No code provided")
                continue
            
            # Clean the code
            cleaned_code = self._clean_code(code)
            
            if not cleaned_code:
                print(f"Skipping {language_code}: No valid code after cleaning")
                continue
            
            # Create filename
            filename = f"{language_code}_code.py"
            filepath = os.path.join(output_dir, filename)
            
            try:
                # Add header comment
                header = f'# Python code generated for language: {language_code}\n'
                header += f'# Original prompt: {self._get_original_prompt(language_code)}\n\n'
                
                full_code = header + cleaned_code
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(full_code)
                
                saved_files.append((language_code, filepath))
                print(f"Saved {language_code} code to: {filepath}")
                
            except Exception as e:
                print(f"Error saving {language_code}: {e}")
        
        print(f"\nSuccessfully saved {len(saved_files)} Python files to {output_dir}/")
        return saved_files
    
    def _get_original_prompt(self, language_code: str) -> str:
        """
        Get the original prompt for a language from translated_prompts.json
        """
        try:
            with open("data/translated_prompts.json", 'r', encoding='utf-8') as f:
                prompts = json.load(f)
                return prompts.get(language_code, "Unknown prompt")
        except:
            return "Unknown prompt"
    
    def _extract_statistics(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Extract statistical information from the AST.
        """
        stats = {
            'total_lines': 0,
            'function_count': 0,
            'class_count': 0,
            'import_count': 0,
            'variable_count': 0,
            'function_call_count': 0,
            'loop_count': 0,
            'conditional_count': 0,
            'string_literal_count': 0,
            'numeric_literal_count': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                stats['function_count'] += 1
            elif isinstance(node, ast.ClassDef):
                stats['class_count'] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                stats['import_count'] += 1
            elif isinstance(node, ast.Assign):
                stats['variable_count'] += len(node.targets)
            elif isinstance(node, ast.Call):
                stats['function_call_count'] += 1
            elif isinstance(node, (ast.For, ast.While)):
                stats['loop_count'] += 1
            elif isinstance(node, (ast.If, ast.IfExp)):
                stats['conditional_count'] += 1
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    stats['string_literal_count'] += 1
                elif isinstance(node.value, (int, float)):
                    stats['numeric_literal_count'] += 1
        
        return stats
    
    def _extract_elements(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Extract detailed code elements from the AST.
        """
        elements = {
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'function_calls': [],
            'loops': [],
            'conditionals': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                elements['functions'].append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                    'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node))
                })
            
            elif isinstance(node, ast.ClassDef):
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append({
                            'name': child.name,
                            'args': [arg.arg for arg in child.args.args],
                            'has_return': any(isinstance(n, ast.Return) for n in ast.walk(child))
                        })
                
                elements['classes'].append({
                    'name': node.name,
                    'bases': [self._get_name(base) for base in node.bases],
                    'methods': methods
                })
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    elements['imports'].append({
                        'module': alias.name,
                        'alias': alias.asname
                    })
            
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    elements['imports'].append({
                        'module': node.module,
                        'name': alias.name,
                        'alias': alias.asname
                    })
            
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        elements['variables'].append({
                            'name': target.id,
                            'type': self._get_value_type(node.value)
                        })
            
            elif isinstance(node, ast.Call):
                func_name = self._get_name(node.func)
                if func_name:
                    elements['function_calls'].append({
                        'name': func_name,
                        'args_count': len(node.args),
                        'keywords_count': len(node.keywords)
                    })
            
            elif isinstance(node, (ast.For, ast.While)):
                elements['loops'].append({
                    'type': 'for' if isinstance(node, ast.For) else 'while',
                    'target': self._get_name(node.target) if isinstance(node, ast.For) else None
                })
            
            elif isinstance(node, ast.If):
                elements['conditionals'].append({
                    'type': 'if',
                    'test': self._get_condition_string(node.test)
                })
        
        return elements
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_name(decorator.func)
        return str(decorator)
    
    def _get_name(self, node: ast.expr) -> Optional[str]:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return None
    
    def _get_value_type(self, node: ast.expr) -> str:
        """Get the type of a value node."""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return 'list'
        elif isinstance(node, ast.Dict):
            return 'dict'
        elif isinstance(node, ast.Tuple):
            return 'tuple'
        elif isinstance(node, ast.Call):
            return 'function_call'
        return 'unknown'
    
    def _get_condition_string(self, node: ast.expr) -> str:
        """Get a string representation of a condition."""
        if isinstance(node, ast.Compare):
            left = self._get_name(node.left) or str(node.left)
            ops = [type(op).__name__ for op in node.ops]
            comparators = [self._get_name(comp) or str(comp) for comp in node.comparators]
            return f"{left} {' '.join(ops)} {' '.join(comparators)}"
        return str(node)
    
    def parse_all_languages(self, llm_output_file: str = "data/llm_output.json") -> Dict[str, Any]:
        """
        Parse code from all languages in the LLM output file.
        
        Args:
            llm_output_file (str): Path to the LLM output JSON file
            
        Returns:
            Dict containing analysis for all languages
        """
        try:
            with open(llm_output_file, 'r', encoding='utf-8') as f:
                llm_outputs = json.load(f)
        except FileNotFoundError:
            print(f"Error: {llm_output_file} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {llm_output_file}")
            return {}
        
        results = {}
        for language_code, code in llm_outputs.items():
            print(f"Parsing code for language: {language_code}")
            results[language_code] = self.parse_code(code, language_code)
        
        return results
    
    def save_analysis(self, analysis: Dict[str, Any], output_file: str = "data/ast_analysis.json"):
        """
        Save the AST analysis results to a JSON file.
        
        Args:
            analysis (Dict): Analysis results
            output_file (str): Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"AST analysis saved to {output_file}")
    
    def generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a summary report of the AST analysis.
        
        Args:
            analysis (Dict): Analysis results
            
        Returns:
            str: Summary report
        """
        report = []
        report.append("=" * 60)
        report.append("PYTHON AST ANALYSIS SUMMARY REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overall statistics
        total_languages = len(analysis)
        languages_with_code = sum(1 for lang_data in analysis.values() if lang_data.get('has_code', False))
        languages_with_errors = sum(1 for lang_data in analysis.values() if lang_data.get('error'))
        
        report.append(f"Total languages analyzed: {total_languages}")
        report.append(f"Languages with valid code: {languages_with_code}")
        report.append(f"Languages with parsing errors: {languages_with_errors}")
        report.append("")
        
        # Per-language summary
        report.append("PER-LANGUAGE SUMMARY:")
        report.append("-" * 40)
        
        for language_code, lang_data in analysis.items():
            report.append(f"\n{language_code.upper()}:")
            
            if not lang_data.get('has_code', False):
                report.append("  No code provided")
                continue
            
            if lang_data.get('error'):
                report.append(f"  Error: {lang_data['error']}")
                continue
            
            stats = lang_data.get('statistics', {})
            elements = lang_data.get('elements', {})
            
            report.append(f"  Functions: {stats.get('function_count', 0)}")
            report.append(f"  Classes: {stats.get('class_count', 0)}")
            report.append(f"  Imports: {stats.get('import_count', 0)}")
            report.append(f"  Variables: {stats.get('variable_count', 0)}")
            report.append(f"  Function calls: {stats.get('function_call_count', 0)}")
            
            # List function names
            if elements.get('functions'):
                func_names = [f['name'] for f in elements['functions']]
                report.append(f"  Function names: {', '.join(func_names)}")
            
            # List class names
            if elements.get('classes'):
                class_names = [c['name'] for c in elements['classes']]
                report.append(f"  Class names: {', '.join(class_names)}")
        
        return '\n'.join(report)


def main():
    """
    Main function to run the AST parser on the LLM outputs.
    """
    parser = PythonASTParser()
    
    print("Starting Python AST analysis...")
    
    # Save individual Python files for each language
    print("\nSaving individual Python files...")
    saved_files = parser.save_individual_python_files()
    
    # Parse all languages
    print("\nParsing code for AST analysis...")
    analysis = parser.parse_all_languages()
    
    # Save analysis results
    parser.save_analysis(analysis)
    
    # Generate and print summary report
    report = parser.generate_summary_report(analysis)
    print(report)
    
    # Save report to file
    with open("data/ast_analysis_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\nAST analysis completed successfully!")
    print("Files generated:")
    print("- data/python_files/ (individual Python files for each language)")
    print("- data/ast_analysis.json (detailed analysis)")
    print("- data/ast_analysis_report.txt (summary report)")


if __name__ == "__main__":
    main()
