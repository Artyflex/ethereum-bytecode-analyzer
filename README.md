# Ethereum Bytecode Analyzer

Analyze and decode Ethereum smart contract bytecode.

## 🚧 Work in Progress (Phase 1 - MVP)

### Planned Features
- [ ] Parse basic EVM opcodes
- [ ] Bytecode validation
- [ ] Interactive CLI
- [ ] JSON export

## Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ethereum-bytecode-analyzer.git
cd ethereum-bytecode-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Testing
```bash
pytest
pytest --cov=src/bytecode_analyzer
```

## Development
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

## Roadmap

- [x] Phase 0: Project setup
- [ ] Phase 1: MVP (7 basic opcodes)
- [ ] Phase 2: Extended support (140+ opcodes)
- [ ] Phase 3: Advanced analysis (function selectors, storage, gas estimation)
- [ ] Phase 4: Web interface & REST API

## License

GNU General Public License v3.0