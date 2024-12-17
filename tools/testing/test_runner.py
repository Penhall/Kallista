# tools/testing/test_runner.py
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
import json

class TestRunner:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results_path = self.project_path / "TestResults"
        self.results_path.mkdir(exist_ok=True)

    def run_tests(self, 
                 test_dll: Optional[str] = None, 
                 filter: Optional[str] = None) -> Dict:
        """Executa testes usando VSTest"""
        command = ["vstest.console.exe"]
        
        if test_dll:
            command.append(str(self.project_path / test_dll))
        else:
            command.append("**/*Tests.dll")
            
        if filter:
            command.extend(["/TestCaseFilter:", filter])
            
        command.extend([
            "/Logger:trx",
            f"/ResultsDirectory:{self.results_path}"
        ])

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            return self._parse_test_results(self._get_latest_result())
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': None
            }

    def _get_latest_result(self) -> Optional[Path]:
        """Obtém o arquivo mais recente de resultados"""
        result_files = list(self.results_path.glob("*.trx"))
        if not result_files:
            return None
        return max(result_files, key=lambda p: p.stat().st_mtime)

    def _parse_test_results(self, result_file: Optional[Path]) -> Dict:
        """Analisa os resultados dos testes"""
        if not result_file:
            return {
                'success': False,
                'error': 'No test results found',
                'results': None
            }

        try:
            tree = ET.parse(result_file)
            root = tree.getroot()
            
            results = []
            for test in root.findall(".//UnitTestResult"):
                results.append({
                    'name': test.get('testName'),
                    'outcome': test.get('outcome'),
                    'duration': test.get('duration'),
                    'error_message': test.find('Output/ErrorInfo/Message').text if test.find('Output/ErrorInfo/Message') is not None else None
                })

            return {
                'success': True,
                'total_tests': len(results),
                'passed_tests': len([r for r in results if r['outcome'] == 'Passed']),
                'failed_tests': len([r for r in results if r['outcome'] == 'Failed']),
                'results': results
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error parsing test results: {str(e)}',
                'results': None
            }

    def save_results(self, results: Dict, filename: str) -> None:
        """Salva os resultados em formato JSON"""
        output_file = self.results_path / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)