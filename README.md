# Ethereum Bytecode Analyzer

A Python tool for parsing and analyzing Ethereum Virtual Machine (EVM) bytecode.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL%20v3.0-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)](https://github.com/Artyflex/ethereum-bytecode-analyzer/releases)

---

## ⚠️ Work In Progress

**IMPORTANT:** This tool is in early development (v0.1.1).

**Use for educational purposes and experimentation.**

---

## 📋 Description

EVM Bytecode Analyzer parses Ethereum smart contract bytecode into human-readable opcode sequences. It extracts PUSH arguments (1-32 bytes), detects invalid bytes, and outputs structured JSON.

**Features:**
- EVM opcodes (Shanghai/Cancun)
- PUSH1-PUSH32 argument extraction
- Interactive and CLI modes
- File input/output (.bin files)
- JSON formatting (normal and compact)
- Bytecode validation
- Comprehensive error handling

---

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/Artyflex/ethereum-bytecode-analyzer.git
cd ethereum-bytecode-analyzer

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Install
pip install -r requirements.txt
pip install -e .
```

---

## 💻 Usage

### Interactive Mode
```bash
python -m bytecode_analyzer
```

Example:
```
Enter EVM bytecode (or 'quit' to exit): 0x6080604052
✓ Bytecode validated successfully

Analysis Result:
{
  "bytecode": "0x6080604052",
  "opcodes": [
    {"offset": 0, "opcode": "PUSH1", "argument": "0x80", ...},
    {"offset": 2, "opcode": "PUSH1", "argument": "0x40", ...},
    {"offset": 4, "opcode": "MSTORE", ...}
  ],
  "metadata": {"total_opcodes": 3, "parsing_errors": []}
}
```

---

### CLI Mode

**Analyze bytecode directly:**
```bash
python -m bytecode_analyzer --bytecode "0x6080604052"
```

**Read from binary file:**
```bash
python -m bytecode_analyzer --file contract.bin
```

**Save output to file:**
```bash
python -m bytecode_analyzer --bytecode "0x6080604052" --output result.json
```

**Compact JSON output:**
```bash
python -m bytecode_analyzer --bytecode "0x6080604052" --compact
```

**Verbose mode (detailed info):**
```bash
python -m bytecode_analyzer --bytecode "0x6080604052" --verbose
```

**Combine options:**
```bash
python -m bytecode_analyzer --file contract.bin --output result.json --verbose
```

**Show version:**
```bash
python -m bytecode_analyzer --version
```

**Show help:**
```bash
python -m bytecode_analyzer --help
```

---

## 📖 Examples

### Example 1: PUSH Opcodes

**Input:**
```bash
python -m bytecode_analyzer --bytecode "0x60425f525f3560ab145f515500"
```

**Output:**
```json
{
  "bytecode": "0x60425f525f3560ab145f515500",
  "length": 13,
  "opcodes": [
    {"offset": 0, "opcode": "PUSH1", "argument": "0x42"},
    {"offset": 2, "opcode": "PUSH0"},
    {"offset": 3, "opcode": "MSTORE"},
    ...
  ]
}
```

### Example 2: Incomplete Bytecode

**Input:**
```bash
python -m bytecode_analyzer --bytecode "0x600160"
```

**Output:**
```json
{
  "bytecode": "0x600160",
  "opcodes": [
    {"offset": 0, "opcode": "PUSH1", "argument": "0x01"},
    {"offset": 2, "opcode": "PUSH1"}
  ],
  "metadata": {
    "parsing_errors": [
      "PUSH1 at offset 2 is incomplete (missing 1-byte argument)"
    ]
  }
}
```

### Example 3: Binary File

**Create binary file:**
```bash
echo -n "6080604052" | xxd -r -p > contract.bin
```

**Analyze:**
```bash
python -m bytecode_analyzer --file contract.bin --output analysis.json
```

---

## 🧪 Testing
```bash
# All tests
pytest

# With coverage
pytest --cov=src/bytecode_analyzer tests/ --cov-report=term-missing

# Specific module
pytest tests/test_parser.py -v
```

**Stats:**
- 250+ tests
- 98% coverage
- All critical paths tested

---

## 🏗️ Architecture

| Module | Purpose |
|--------|---------|
| **opcodes.py** | EVM opcodes mapping |
| **validator.py** | Bytecode validation (5 checks) |
| **parser.py** | Bytecode → opcodes with arguments |
| **formatter.py** | JSON output formatting |
| **cli.py** | Interactive + CLI modes |

**Flow:** Input → Clean → Validate → Parse → Format → Output

---

## 🛠️ Development
```bash
# Setup
git clone https://github.com/Artyflex/ethereum-bytecode-analyzer.git
cd ethereum-bytecode-analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Quality checks
pytest                    # Tests
black src/ tests/         # Format
flake8 src/ tests/        # Lint
```

---

## 📄 License

**GNU General Public License v3.0**

- ✅ Free to use, modify, distribute
- ✅ Open source
- ⚠️ Derivatives must be GPL v3.0
- ⚠️ No warranty

See [LICENSE](LICENSE) for details.
