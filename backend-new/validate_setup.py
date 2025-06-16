#!/usr/bin/env python3
"""
Setup validation script for PocketFlow backend.
Run this script to verify your development environment is correctly configured.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required, found:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_virtual_environment():
    """Check if running in virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment - recommended to use venv")
        return True  # Not required, just recommended

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'pocketflow',
        'ollama', 
        'fastapi',
        'python-dotenv',
        'duckduckgo-search',
        'requests',
        'pydantic',
        'uvicorn',
        'pyyaml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - not installed")
    
    if missing_packages:
        print(f"\n💡 Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    return True

def check_environment_file():
    """Check if .env file exists and has required variables."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    print("✅ .env.example found")
    
    if not env_file.exists():
        print("⚠️  .env file not found - copy from .env.example")
        return False
    print("✅ .env file found")
    
    # Check required variables
    required_vars = [
        'OLLAMA_HOST',
        'OLLAMA_QUERY_MODEL', 
        'OLLAMA_RESEARCH_MODEL',
        'OLLAMA_REFLECTION_MODEL',
        'OLLAMA_ANSWER_MODEL'
    ]
    
    with open(env_file) as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in env_content:
            missing_vars.append(var)
        else:
            print(f"✅ {var} configured")
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def check_source_files():
    """Check if source files exist."""
    required_files = [
        'src/graph.py',
        'src/nodes.py', 
        'src/flow.py',
        'src/app.py',
        'run_server.py',
        'test_new_graph.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - missing")
    
    return len(missing_files) == 0

def test_imports():
    """Test critical imports."""
    try:
        sys.path.append(str(Path('src')))
        
        # Test PocketFlow import
        from pocketflow import Flow, Node
        print("✅ PocketFlow imports successful")
        
        # Test Ollama import  
        import ollama
        print("✅ Ollama import successful")
        
        # Test module imports
        from graph import ResearchAgentConfig, create_research_graph
        print("✅ Graph module imports successful")
        
        from nodes import QueryGenerationNode
        print("✅ Nodes module imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🔍 Validating PocketFlow Backend Setup")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment), 
        ("Dependencies", check_dependencies),
        ("Environment Configuration", check_environment_file),
        ("Source Files", check_source_files),
        ("Module Imports", test_imports)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Setup validation successful! Ready for development.")
        print("\nNext steps:")
        print("1. Configure Ollama models in .env if needed")
        print("2. Run: python test_new_graph.py")
        print("3. Start development server: python run_server.py")
        return True
    else:
        print("⚠️  Setup incomplete. Please address the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)