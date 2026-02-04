# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.1] - 2025-02-03 (Phase 1bis)

### Added
- **CLI arguments support**
  - `--bytecode` : Analyze bytecode directly from command line
  - `--file` : Read bytecode from binary (.bin) files
  - `--output` : Save JSON output to file
  - `--compact` : Single-line JSON output
  - `--verbose` : Detailed parsing information
  - `--version` : Display version number
  - `--help` : Show usage information

- **PUSH2-PUSH32 support**
  - Full argument extraction for all PUSH opcodes (1-32 bytes)
  - Dynamic argument size calculation
  - Incomplete PUSH detection with detailed errors

- **File I/O**
  - Read bytecode from binary files
  - Write JSON output to files
  - Automatic directory creation for output files

- **Enhanced testing**
  - 150+ comprehensive tests
  - >95% code coverage
  - Real contract bytecode tests (USDT, etc.)
  - Edge case and error path coverage

### Changed
- Parser now handles all PUSH opcodes uniformly
- CLI dispatcher logic (interactive vs CLI mode)
- Documentation updated with new features

### Fixed
- PUSH2-PUSH32 now extract arguments correctly
- Improved error messages for incomplete PUSH opcodes

---

## [0.1.0] - 2025-02-03 (Phase 1 - MVP)

### Added
- **Core functionality**
  - 140+ EVM opcodes mapping (Shanghai/Cancun)
  - Bytecode validation (5 atomic checks)
  - PUSH1 argument extraction
  - JSON output formatter
  - Interactive CLI mode

- **Modules**
  - `opcodes.py` : EVM opcodes definitions
  - `validator.py` : Bytecode validation and cleaning
  - `parser.py` : Bytecode parsing engine
  - `formatter.py` : JSON output formatting
  - `cli.py` : Interactive command-line interface

- **Testing**
  - 100+ unit and integration tests
  - pytest framework
  - >95% code coverage

- **Development tools**
  - Black code formatter
  - Flake8 linter
  - Git workflow
  - Virtual environment setup

### Documentation
- README with installation and usage
- Module docstrings
- GNU GPL v3.0 license

---

## [Unreleased]

### Planned for Phase 2
- Function selector detection
- Storage slot analysis
- Gas cost estimation
- Control flow analysis

### Planned for Phase 3
- REST API (FastAPI)
- Web frontend (React)
- Online deployment

---

[0.1.1]: https://github.com/Artyflex/ethereum-bytecode-analyzer/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Artyflex/ethereum-bytecode-analyzer/releases/tag/v0.1.0