# Ethereum Bytecode Analyzer

A Python tool for parsing and analyzing Ethereum Virtual Machine (EVM) bytecode.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL%20v3.0-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/Artyflex/ethereum-bytecode-analyzer/releases)

---

## ⚠️ Work In Progress

**IMPORTANT:** This tool is currently in early development (Phase 1 - MVP).

**Current Limitations:**
- ✅ Only **PUSH1** opcode handles arguments correctly
- ❌ All other OPCODES are recognized but arguments are **not extracted**
- ❌ Tool is **not reliable** for production use
- 🚧 Analysis results may be incomplete or inaccurate

**Use this tool for educational purposes and experimentation only.**

---

## 📋 Description

EVM Bytecode Analyzer is a command-line tool that parses Ethereum smart contract bytecode into human-readable opcode sequences. It identifies opcodes, extracts arguments (currently PUSH1 only), detects invalid bytes, and outputs results in JSON format.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/Artyflex/ethereum-bytecode-analyzer.git
cd ethereum-bytecode-analyzer

# Create and activate virtual environment
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

---

## 💻 Usage

### Interactive Mode

Launch the interactive CLI:
```bash
python -m bytecode_analyzer
```

Example session:
```
================================================================================
                    EVM Bytecode Analyzer - Interactive Mode
================================================================================

Instructions:
  - Enter bytecode with or without '0x' prefix
  - Type 'quit', 'exit', or 'q' to exit
  - Press Ctrl+C to exit

Enter EVM bytecode (or 'quit' to exit): 0x6080604052
✓ Bytecode validated successfully

Analysis Result:
================================================================================
{
  "bytecode": "0x6080604052",
  "length": 5,
  "opcodes": [
    {
      "offset": 0,
      "opcode": "PUSH1",
      "value": "0x60",
      "argument": "0x80",
      "description": "Place 1 byte item on stack"
    },
    {
      "offset": 2,
      "opcode": "PUSH1",
      "value": "0x60",
      "argument": "0x40",
      "description": "Place 1 byte item on stack"
    },
    {
      "offset": 4,
      "opcode": "MSTORE",
      "value": "0x52",
      "description": "Save word to memory"
    }
  ],
  "metadata": {
    "total_opcodes": 3,
    "parsing_errors": []
  }
}
================================================================================

Enter EVM bytecode (or 'quit' to exit): quit

Thank you for using EVM Bytecode Analyzer!
```

---

## 📖 Examples

### Example 1: Simple Bytecode

**Input:**
```
0x60425f525f3560ab145f515500
```

**Output (parsed opcodes):**
```json
{
  "bytecode": "0x60425f525f3560ab145f515500",
  "length": 13,
  "opcodes": [
    {
      "offset": 0,
      "opcode": "PUSH1",
      "value": "0x60",
      "argument": "0x42",
      "description": "Place 1 byte item on stack"
    },
    {
      "offset": 2,
      "opcode": "PUSH0",
      "value": "0x5f",
      "description": "Place 0 on stack"
    },
    ...
  ],
  "metadata": {
    "total_opcodes": 11,
    "parsing_errors": []
  }
}
```

### Example 2: Bytecode with Errors

**Input:**
```
0x600160  
```
*(Incomplete PUSH1 at the end)*

**Output:**
```json
{
  "bytecode": "0x600160",
  "length": 3,
  "opcodes": [
    {
      "offset": 0,
      "opcode": "PUSH1",
      "value": "0x60",
      "argument": "0x01",
      "description": "Place 1 byte item on stack"
    },
    {
      "offset": 2,
      "opcode": "PUSH1",
      "value": "0x60",
      "description": "Place 1 byte item on stack"
    }
  ],
  "metadata": {
    "total_opcodes": 2,
    "parsing_errors": [
      "PUSH1 at offset 2 is incomplete (missing 1-byte argument)"
    ]
  }
}
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src/bytecode_analyzer tests/ --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_parser.py -v
```

---

## 📊 Project Status

### Phase 1: MVP (Current) ✅

- [x] Complete EVM opcodes mapping (140+ opcodes)
- [x] Bytecode validation (format, structure)
- [x] Basic parser with PUSH1 support
- [x] JSON output formatter
- [x] Interactive CLI
- [x] Comprehensive test suite (100+ tests, >95% coverage)

### Phase 2: Extended Opcodes 🚧

- [ ] PUSH2-PUSH32 argument extraction
- [ ] CLI options (--file, --output, --verbose)
- [ ] Handle all opcode variations
- [ ] Performance optimization

### Phase 3: Advanced Analysis 📋

- [ ] Function selector detection
- [ ] Storage slot analysis
- [ ] Gas cost estimation
- [ ] Control flow analysis

### Phase 4: Web Interface 📋

- [ ] REST API (FastAPI)
- [ ] Web frontend (React)
- [ ] Deployment (Railway/Vercel)

### Phase 5: Improvements 📋

- [ ] Advanced formatter options
- [ ] YAML/XML output formats
- [ ] CLI with colors and styling
- [ ] Export to file functionality

---

## 🏗️ Architecture

### Module Overview

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **opcodes.py** | EVM opcode definitions | `get_opcode_info()`, `OPCODES_MAP` |
| **validator.py** | Input validation | `validate_bytecode()`, `clean_bytecode()` |
| **parser.py** | Bytecode parsing | `parse_bytecode()` |
| **formatter.py** | Output formatting | `format_output()` |
| **cli.py** | User interface | `run_interactive()` |

### Data Flow
```
User Input (bytecode string)
    ↓
validator.clean_bytecode()
    ↓
validator.validate_bytecode()
    ↓
parser.parse_bytecode()
    ↓
formatter.format_output()
    ↓
JSON Output
```

---

## 🛠️ Development

### Setup Development Environment
```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/ethereum-bytecode-analyzer.git
cd ethereum-bytecode-analyzer
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

### Code Quality

- **Testing:** pytest with >95% coverage
- **Formatting:** black (100 char line length)
- **Linting:** flake8
- **Type hints:** Python 3.9+ syntax

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**.

See the [LICENSE](LICENSE) file for details.

### Key Points:

- ✅ Free to use, modify, and distribute
- ✅ Open source
- ⚠️ Modified versions must also be GPL v3.0
- ⚠️ No warranty provided

---
