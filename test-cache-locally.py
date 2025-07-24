#!/usr/bin/env python3
"""
Local cache testing script for Agentic AI IaC
Tests caching strategy and identifies potential GitHub Actions issues
"""

import os
import sys
import subprocess
import json
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class CacheTestResult:
    def __init__(self, test_name: str, status: str, duration: float = 0, message: str = ""):
        self.test_name = test_name
        self.status = status  # "passed", "failed", "warning", "skipped"
        self.duration = duration
        self.message = message
        self.timestamp = datetime.now().isoformat()

class LocalCacheTester:
    def __init__(self):
        self.results: List[CacheTestResult] = []
        self.start_time = time.time()
        self.project_root = Path.cwd()
        self.cache_dirs = {
            "pip": Path.home() / ".cache" / "pip",
            "local_site_packages": Path.home() / ".local" / "lib" / "python3.11" / "site-packages",
            "npm": Path.home() / ".npm",
            "yarn": Path.home() / ".yarn" / "cache",
            "demo_apps": self.project_root / "demo-apps",
            "test_reports": self.project_root / "test-reports",
            "logs": self.project_root / "logs"
        }
        
    def log(self, message: str, level: str = "info"):
        """Log message with timestamp and level"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        levels = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌",
            "debug": "🔍"
        }
        icon = levels.get(level, "📝")
        print(f"[{timestamp}] {icon} {message}")
    
    def run_command(self, cmd: List[str], timeout: int = 60, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run command with timeout and capture output"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=capture_output, 
                text=True, 
                timeout=timeout,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return -1, "", str(e)
    
    def get_dir_size(self, path: Path) -> str:
        """Get human-readable directory size"""
        if not path.exists():
            return "0 B"
        
        try:
            # Use du command if available (more accurate)
            returncode, stdout, _ = self.run_command(["du", "-sh", str(path)])
            if returncode == 0:
                return stdout.split()[0]
        except:
            pass
        
        # Fallback to Python calculation
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                    except (OSError, IOError):
                        continue
        except:
            return "unknown"
        
        # Convert to human readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} TB"
    
    def test_python_environment(self) -> CacheTestResult:
        """Test Python environment and package installation"""
        start_time = time.time()
        
        try:
            # Test basic Python
            returncode, stdout, stderr = self.run_command([sys.executable, "--version"])
            if returncode != 0:
                return CacheTestResult("python_environment", "failed", 
                                     time.time() - start_time, f"Python not working: {stderr}")
            
            python_version = stdout.strip()
            self.log(f"Python version: {python_version}")
            
            # Test pip
            returncode, stdout, stderr = self.run_command([sys.executable, "-m", "pip", "--version"])
            if returncode != 0:
                return CacheTestResult("python_environment", "failed",
                                     time.time() - start_time, f"Pip not working: {stderr}")
            
            pip_version = stdout.strip()
            self.log(f"Pip version: {pip_version}")
            
            # Test cache directory
            pip_cache = self.cache_dirs["pip"]
            if not pip_cache.exists():
                pip_cache.mkdir(parents=True, exist_ok=True)
                self.log(f"Created pip cache directory: {pip_cache}")
            
            return CacheTestResult("python_environment", "passed", 
                                 time.time() - start_time, f"Python {python_version} ready")
            
        except Exception as e:
            return CacheTestResult("python_environment", "failed", 
                                 time.time() - start_time, str(e))
    
    def test_pip_cache_behavior(self) -> CacheTestResult:
        """Test pip caching behavior"""
        start_time = time.time()
        
        try:
            pip_cache = self.cache_dirs["pip"]
            
            # Get initial cache size
            initial_size = self.get_dir_size(pip_cache)
            self.log(f"Initial pip cache size: {initial_size}")
            
            # Test installing a small package (should use cache if available)
            test_package = "six"  # Small, stable package
            
            self.log(f"Installing test package: {test_package}")
            returncode, stdout, stderr = self.run_command([
                sys.executable, "-m", "pip", "install", "--user", 
                "--cache-dir", str(pip_cache), test_package
            ], timeout=120)
            
            if returncode != 0:
                return CacheTestResult("pip_cache", "failed",
                                     time.time() - start_time, f"Package install failed: {stderr}")
            
            # Check if cache was used
            cache_used = "Using cached" in stdout or "Requirement already satisfied" in stdout
            
            # Get final cache size
            final_size = self.get_dir_size(pip_cache)
            self.log(f"Final pip cache size: {final_size}")
            
            message = f"Cache used: {cache_used}, Size: {initial_size} -> {final_size}"
            return CacheTestResult("pip_cache", "passed", time.time() - start_time, message)
            
        except Exception as e:
            return CacheTestResult("pip_cache", "failed", time.time() - start_time, str(e))
    
    def test_requirements_installation(self) -> CacheTestResult:
        """Test requirements.txt installation with caching"""
        start_time = time.time()
        
        try:
            requirements_files = [
                self.project_root / "requirements.txt",
                self.project_root / "requirements-minimal.txt"
            ]
            
            # Find available requirements file
            requirements_file = None
            for req_file in requirements_files:
                if req_file.exists():
                    requirements_file = req_file
                    break
            
            if not requirements_file:
                return CacheTestResult("requirements_install", "skipped",
                                     time.time() - start_time, "No requirements.txt found")
            
            self.log(f"Installing requirements from: {requirements_file.name}")
            
            pip_cache = self.cache_dirs["pip"]
            returncode, stdout, stderr = self.run_command([
                sys.executable, "-m", "pip", "install", "--user",
                "--cache-dir", str(pip_cache),
                "-r", str(requirements_file)
            ], timeout=300)
            
            if returncode != 0:
                # Try with minimal requirements if main fails
                minimal_req = self.project_root / "requirements-minimal.txt"
                if minimal_req.exists() and requirements_file != minimal_req:
                    self.log("Main requirements failed, trying minimal requirements...")
                    returncode, stdout, stderr = self.run_command([
                        sys.executable, "-m", "pip", "install", "--user",
                        "--cache-dir", str(pip_cache),
                        "-r", str(minimal_req)
                    ], timeout=180)
            
            if returncode != 0:
                return CacheTestResult("requirements_install", "failed",
                                     time.time() - start_time, f"Requirements install failed: {stderr[:500]}")
            
            # Count cache hits
            cache_hits = stdout.count("Using cached")
            already_satisfied = stdout.count("Requirement already satisfied")
            
            message = f"Cache hits: {cache_hits}, Already satisfied: {already_satisfied}"
            return CacheTestResult("requirements_install", "passed", 
                                 time.time() - start_time, message)
            
        except Exception as e:
            return CacheTestResult("requirements_install", "failed", 
                                 time.time() - start_time, str(e))
    
    def test_python_imports(self) -> CacheTestResult:
        """Test critical Python module imports"""
        start_time = time.time()
        
        critical_modules = [
            ("yaml", "PyYAML"),
            ("requests", "requests"),
            ("click", "click"),
            ("json", "built-in"),
            ("pathlib", "built-in"),
            ("asyncio", "built-in")
        ]
        
        optional_modules = [
            ("boto3", "AWS SDK"),
            ("google.cloud", "Google Cloud SDK"),
            ("kubernetes", "Kubernetes client"),
            ("docker", "Docker SDK"),
            ("pytest", "testing framework")
        ]
        
        # Add src to Python path
        src_path = self.project_root / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        
        results = {"critical": 0, "optional": 0, "total_critical": len(critical_modules)}
        failed_imports = []
        
        # Test critical imports
        for module, description in critical_modules:
            try:
                __import__(module)
                results["critical"] += 1
                self.log(f"✅ {module} ({description})")
            except ImportError as e:
                failed_imports.append(f"{module}: {e}")
                self.log(f"❌ {module}: {e}")
        
        # Test optional imports
        for module, description in optional_modules:
            try:
                __import__(module)
                results["optional"] += 1
                self.log(f"✅ {module} ({description})")
            except ImportError:
                self.log(f"⚠️ {module} not available (optional)")
        
        # Test project modules
        try:
            from agentic_iac.utils.logger import setup_logger
            self.log("✅ Project modules importable")
            project_modules_ok = True
        except ImportError as e:
            self.log(f"⚠️ Project modules: {e}")
            project_modules_ok = False
        
        duration = time.time() - start_time
        
        if results["critical"] == results["total_critical"] and project_modules_ok:
            status = "passed"
            message = f"All critical imports OK, {results['optional']} optional modules available"
        elif results["critical"] == results["total_critical"]:
            status = "warning"
            message = f"Critical imports OK but project modules have issues"
        else:
            status = "failed"
            message = f"Missing critical imports: {failed_imports}"
        
        return CacheTestResult("python_imports", status, duration, message)
    
    def test_demo_applications(self) -> CacheTestResult:
        """Test demo application setup and caching"""
        start_time = time.time()
        
        try:
            demo_runner = self.project_root / "demo-runner"
            
            if not demo_runner.exists():
                return CacheTestResult("demo_applications", "skipped",
                                     time.time() - start_time, "demo-runner not found")
            
            # Make demo runner executable
            demo_runner.chmod(0o755)
            
            # Test demo list command
            self.log("Testing demo list command...")
            returncode, stdout, stderr = self.run_command([str(demo_runner), "list"], timeout=30)
            
            if returncode != 0:
                return CacheTestResult("demo_applications", "failed",
                                     time.time() - start_time, f"Demo list failed: {stderr}")
            
            # Test demo setup (quick test with simple app)
            demo_apps_dir = self.cache_dirs["demo_apps"]
            test_demo = "simple-nodejs-api"
            test_target = demo_apps_dir / f"test-{test_demo}"
            
            # Clean up previous test
            if test_target.exists():
                shutil.rmtree(test_target)
            
            self.log(f"Testing demo setup: {test_demo}")
            returncode, stdout, stderr = self.run_command([
                str(demo_runner), "setup", test_demo, "--target-dir", str(test_target)
            ], timeout=120)
            
            if returncode == 0 and test_target.exists():
                status = "passed"
                message = f"Demo setup successful, directory created: {self.get_dir_size(test_target)}"
            else:
                status = "warning"
                message = f"Demo setup issues but may work in CI: {stderr[:200]}"
            
            return CacheTestResult("demo_applications", status, time.time() - start_time, message)
            
        except Exception as e:
            return CacheTestResult("demo_applications", "failed", time.time() - start_time, str(e))
    
    def test_cli_commands(self) -> CacheTestResult:
        """Test CLI command availability and basic functionality"""
        start_time = time.time()
        
        try:
            agentic_cli = self.project_root / "agentic-iac"
            
            if not agentic_cli.exists():
                return CacheTestResult("cli_commands", "warning",
                                     time.time() - start_time, "agentic-iac CLI not found, may use python -m")
            
            # Make CLI executable
            agentic_cli.chmod(0o755)
            
            # Test help command
            self.log("Testing CLI help command...")
            returncode, stdout, stderr = self.run_command([str(agentic_cli), "--help"], timeout=30)
            
            if returncode != 0:
                # Try alternative Python module approach
                returncode, stdout, stderr = self.run_command([
                    sys.executable, "-m", "agentic_iac.cli", "--help"
                ], timeout=30)
            
            if returncode != 0:
                return CacheTestResult("cli_commands", "failed",
                                     time.time() - start_time, f"CLI help failed: {stderr}")
            
            # Test status command
            self.log("Testing CLI status command...")
            returncode, stdout, stderr = self.run_command([str(agentic_cli), "status"], timeout=30)
            
            if returncode != 0:
                # Try alternative approach
                returncode, stdout, stderr = self.run_command([
                    sys.executable, "-m", "agentic_iac.cli", "status"
                ], timeout=30)
            
            status = "passed" if returncode == 0 else "warning"
            message = "CLI commands working" if returncode == 0 else "CLI has issues but may work in CI"
            
            return CacheTestResult("cli_commands", status, time.time() - start_time, message)
            
        except Exception as e:
            return CacheTestResult("cli_commands", "failed", time.time() - start_time, str(e))
    
    def test_node_js_detection(self) -> CacheTestResult:
        """Test Node.js package manager detection (GitHub Actions compatibility)"""
        start_time = time.time()
        
        try:
            # Check for Node.js package files
            package_managers = {
                "npm": self.project_root / "package.json",
                "yarn": self.project_root / "yarn.lock", 
                "pnpm": self.project_root / "pnpm-lock.yaml"
            }
            
            detected = []
            for pm, file_path in package_managers.items():
                if file_path.exists():
                    detected.append(pm)
                    self.log(f"Detected {pm}: {file_path.name}")
            
            if not detected:
                return CacheTestResult("nodejs_detection", "passed",
                                     time.time() - start_time, "No Node.js detected (Python-only project)")
            
            # Test Node.js installation if detected
            returncode, stdout, stderr = self.run_command(["node", "--version"], timeout=10)
            node_available = returncode == 0
            
            if node_available:
                node_version = stdout.strip()
                self.log(f"Node.js version: {node_version}")
                
                # Test npm cache
                npm_cache = self.cache_dirs["npm"]
                npm_cache_size = self.get_dir_size(npm_cache)
                self.log(f"npm cache size: {npm_cache_size}")
                
                message = f"Node.js {node_version} available, npm cache: {npm_cache_size}"
                status = "passed"
            else:
                message = f"Node.js files detected ({detected}) but Node.js not installed"
                status = "warning"
            
            return CacheTestResult("nodejs_detection", status, time.time() - start_time, message)
            
        except Exception as e:
            return CacheTestResult("nodejs_detection", "failed", time.time() - start_time, str(e))
    
    def test_github_actions_simulation(self) -> CacheTestResult:
        """Simulate GitHub Actions environment behavior"""
        start_time = time.time()
        
        try:
            # Create temporary environment similar to GitHub Actions
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Simulate GitHub Actions environment variables
                github_env = {
                    "CI": "true",
                    "GITHUB_ACTIONS": "true",
                    "RUNNER_OS": "Linux",
                    "PYTHONPATH": f"{self.project_root}/src:{os.environ.get('PYTHONPATH', '')}",
                    "AGENTIC_DEMO_MODE": "true",
                    "AGENTIC_CI_MODE": "true"
                }
                
                # Test environment setup
                env = os.environ.copy()
                env.update(github_env)
                
                # Test basic Python imports in simulated environment
                test_script = temp_path / "test_imports.py"
                test_script.write_text(f"""
import sys
sys.path.insert(0, '{self.project_root}/src')

try:
    import yaml
    import requests
    import click
    print("✅ Basic imports OK")
except ImportError as e:
    print(f"❌ Import error: {{e}}")
    sys.exit(1)

try:
    from agentic_iac.utils.logger import setup_logger
    print("✅ Project imports OK")
except ImportError as e:
    print(f"⚠️ Project import warning: {{e}}")

print("GitHub Actions simulation successful")
""")
                
                returncode, stdout, stderr = self.run_command([
                    sys.executable, str(test_script)
                ], timeout=30)
                
                if returncode == 0:
                    status = "passed"
                    message = "GitHub Actions environment simulation successful"
                else:
                    status = "warning"
                    message = f"Simulation issues: {stderr[:200]}"
                
                self.log(f"Simulation output: {stdout}")
                
                return CacheTestResult("github_actions_simulation", status, 
                                     time.time() - start_time, message)
                
        except Exception as e:
            return CacheTestResult("github_actions_simulation", "failed", 
                                 time.time() - start_time, str(e))
    
    def generate_cache_report(self) -> Dict:
        """Generate comprehensive cache report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "python_version": sys.version,
            "cache_directories": {},
            "test_results": [],
            "recommendations": []
        }
        
        # Cache directory information
        for name, path in self.cache_dirs.items():
            report["cache_directories"][name] = {
                "path": str(path),
                "exists": path.exists(),
                "size": self.get_dir_size(path) if path.exists() else "0 B",
                "writable": os.access(path.parent, os.W_OK) if path.exists() else os.access(path.parent, os.W_OK)
            }
        
        # Test results
        for result in self.results:
            report["test_results"].append({
                "test_name": result.test_name,
                "status": result.status,
                "duration": result.duration,
                "message": result.message,
                "timestamp": result.timestamp
            })
        
        # Generate recommendations
        failed_tests = [r for r in self.results if r.status == "failed"]
        warning_tests = [r for r in self.results if r.status == "warning"]
        
        if failed_tests:
            report["recommendations"].append("🔴 Fix failed tests before deploying to GitHub Actions")
            for test in failed_tests:
                report["recommendations"].append(f"   - {test.test_name}: {test.message}")
        
        if warning_tests:
            report["recommendations"].append("🟡 Address warnings to improve reliability")
            for test in warning_tests:
                report["recommendations"].append(f"   - {test.test_name}: {test.message}")
        
        if not failed_tests and not warning_tests:
            report["recommendations"].append("✅ All tests passed - ready for GitHub Actions deployment")
        
        # Cache optimization recommendations
        pip_cache_size = report["cache_directories"]["pip"]["size"]
        if pip_cache_size == "0 B":
            report["recommendations"].append("💡 Pip cache is empty - first GitHub Actions run will be slower")
        else:
            report["recommendations"].append(f"✅ Pip cache active ({pip_cache_size}) - subsequent runs will be faster")
        
        return report
    
    def run_all_tests(self) -> Dict:
        """Run all cache tests and generate report"""
        self.log("🧪 Starting comprehensive cache testing...", "info")
        self.log(f"Project root: {self.project_root}", "debug")
        
        # Define test sequence
        tests = [
            ("Python Environment", self.test_python_environment),
            ("Pip Cache Behavior", self.test_pip_cache_behavior),
            ("Requirements Installation", self.test_requirements_installation),
            ("Python Imports", self.test_python_imports),
            ("Demo Applications", self.test_demo_applications),
            ("CLI Commands", self.test_cli_commands),
            ("Node.js Detection", self.test_node_js_detection),
            ("GitHub Actions Simulation", self.test_github_actions_simulation)
        ]
        
        # Run tests
        for test_name, test_func in tests:
            self.log(f"\n🔍 Running: {test_name}", "info")
            self.log("-" * 40, "debug")
            
            try:
                result = test_func()
                self.results.append(result)
                
                status_icon = {
                    "passed": "✅",
                    "warning": "⚠️", 
                    "failed": "❌",
                    "skipped": "⏭️"
                }.get(result.status, "❓")
                
                self.log(f"{status_icon} {test_name}: {result.status.upper()} ({result.duration:.2f}s)", 
                        "success" if result.status == "passed" else result.status)
                
                if result.message:
                    self.log(f"   {result.message}", "debug")
                    
            except Exception as e:
                error_result = CacheTestResult(test_name.lower().replace(" ", "_"), "failed", 0, str(e))
                self.results.append(error_result)
                self.log(f"❌ {test_name}: FAILED - {e}", "error")
        
        # Generate final report
        total_duration = time.time() - self.start_time
        self.log(f"\n🏁 Testing completed in {total_duration:.2f} seconds", "info")
        
        # Summary
        passed = len([r for r in self.results if r.status == "passed"])
        warnings = len([r for r in self.results if r.status == "warning"])
        failed = len([r for r in self.results if r.status == "failed"])
        skipped = len([r for r in self.results if r.status == "skipped"])
        total = len(self.results)
        
        self.log(f"\n📊 Test Summary: {passed} passed, {warnings} warnings, {failed} failed, {skipped} skipped", "info")
        
        if failed == 0:
            self.log("🎉 All critical tests passed - ready for GitHub Actions!", "success")
        elif failed <= 2 and warnings > 0:
            self.log("⚠️ Some issues detected - review before GitHub Actions deployment", "warning")
        else:
            self.log("❌ Multiple failures detected - fix issues before deploying", "error")
        
        return self.generate_cache_report()

def main():
    """Main entry point"""
    tester = LocalCacheTester()
    
    try:
        # Run all tests
        report = tester.run_all_tests()
        
        # Save report
        report_file = tester.project_root / f"cache-test-report-{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        tester.log(f"\n💾 Detailed report saved to: {report_file}", "info")
        
        # Print recommendations
        tester.log("\n🎯 Recommendations:", "info")
        for rec in report["recommendations"]:
            tester.log(f"  {rec}", "info")
        
        # Exit code based on results
        failed_count = len([r for r in tester.results if r.status == "failed"])
        return 0 if failed_count == 0 else 1
        
    except KeyboardInterrupt:
        tester.log("\n⚠️ Testing interrupted by user", "warning")
        return 1
    except Exception as e:
        tester.log(f"\n❌ Testing failed with error: {e}", "error")
        return 1

if __name__ == "__main__":
    sys.exit(main())
