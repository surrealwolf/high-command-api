# Testing Guide - Hell Divers 2 API

## Quick Start

### Run All Tests with Coverage
```bash
make test
```

### Run Tests Without Coverage (Fast)
```bash
make test-fast
```

### Run All Quality Checks
```bash
make check-all  # Format, lint, and test
```

## Test Execution Commands

### Using Make
```bash
# Run tests with coverage report
make test

# Run tests quickly (no coverage)
make test-fast

# Run linters only
make lint

# Format code
make format

# Run linters and tests
make check

# Run format + lint + test (complete gate)
make check-all
```

### Using Pytest Directly
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html --cov-report=xml

# Run all tests with coverage report in terminal
pytest --cov=src --cov-report=term

# Run all tests with detailed coverage (show missing lines)
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_app.py -v

# Run specific test class
pytest tests/test_app.py::TestDatabase -v

# Run specific test function
pytest tests/test_app.py::TestDatabase::test_save_and_get_war_status -v

# Run tests matching a pattern
pytest -k "database" -v

# Run tests with output (show print statements)
pytest -s

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Stop on first failure
pytest -x

# Run last failed tests only
pytest --lf
```

## Coverage Reports

### View HTML Coverage Report
```bash
# Generate and open HTML report
pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in a browser
```

### Generate Coverage Reports
```bash
# XML report (for CI/CD)
pytest --cov=src --cov-report=xml

# HTML report (for local viewing)
pytest --cov=src --cov-report=html

# Terminal report
pytest --cov=src --cov-report=term

# All reports
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
```

### Check Coverage Threshold
```bash
# Fail if coverage is below 80%
pytest --cov=src --cov-fail-under=80
```

## Test Organization

### Test Files
- `tests/demo.py` - Original integration-style tests (11 tests)
- `tests/test_app.py` - Comprehensive unit tests (118 tests)

### Test Structure
```
tests/
├── __init__.py
├── demo.py              # Integration tests
└── test_app.py          # Unit tests
    ├── Config tests     # 5 tests
    ├── Database tests   # 60 tests
    ├── Scraper tests    # 20 tests
    ├── Collector tests  # 15 tests
    └── API tests        # 28 tests
```

## Test Categories

### 1. Configuration Tests (5 tests)
Tests for configuration management and environment variables.

```bash
pytest tests/test_app.py::test_config_defaults -v
```

### 2. Database Tests (60 tests)
Tests for all database operations including CRUD, snapshots, and error handling.

```bash
pytest tests/test_app.py::TestDatabase -v
```

### 3. Scraper Tests (20 tests)
Tests for HTTP scraper including rate limiting and error handling.

```bash
pytest tests/test_app.py::TestScraper -v
```

### 4. Collector Tests (15 tests)
Tests for background data collector and scheduler.

```bash
pytest tests/test_app.py::TestCollector -v
```

### 5. API Endpoint Tests (28 tests)
Tests for all FastAPI endpoints including cache fallback.

```bash
pytest tests/test_app.py::TestAPIEndpoints -v
```

## Debugging Tests

### Run with Verbose Output
```bash
pytest -vv
```

### Show Print Statements
```bash
pytest -s
```

### Run with Debugger
```bash
pytest --pdb  # Drop into debugger on failure
```

### Show Local Variables on Failure
```bash
pytest -l
```

### Full Debug Mode
```bash
pytest -vv -s -l --tb=long
```

## Code Quality Checks

### Linting
```bash
# Check code with ruff
ruff check src tests

# Auto-fix issues
ruff check --fix src tests
```

### Type Checking
```bash
# Run mypy
mypy src --ignore-missing-imports
```

### Formatting
```bash
# Check formatting
black src tests --check

# Format code
black src tests
```

### All Quality Checks
```bash
# Run all checks
make check-all
```

## Continuous Integration

The project is configured to run tests automatically on:
- Push to any branch
- Pull request creation/update
- Manual workflow dispatch

### Coverage Enforcement
- Minimum coverage: 80% (enforced in pytest.ini)
- Current coverage: 97%
- Coverage reports uploaded to CI/CD

### CI/CD Configuration
```toml
[tool.pytest.ini_options]
addopts = "-v --cov=src --cov-report=xml --cov-report=html --cov-fail-under=80"
```

## Test Development

### Writing New Tests

1. **Create test function**
   ```python
   def test_my_feature():
       """Test description"""
       # Arrange
       data = {"key": "value"}
       
       # Act
       result = my_function(data)
       
       # Assert
       assert result is not None
   ```

2. **Use fixtures for setup/teardown**
   ```python
   @pytest.fixture
   def temp_db():
       db = Database(":memory:")
       yield db
       # cleanup
   ```

3. **Mock external dependencies**
   ```python
   @patch('requests.Session.get')
   def test_api_call(mock_get):
       mock_get.return_value.json.return_value = {"data": "test"}
       result = fetch_data()
       assert result["data"] == "test"
   ```

### Test Best Practices

1. **Use descriptive names**
   - `test_save_war_status_with_valid_data`
   - `test_get_campaigns_when_cache_is_empty`

2. **One assertion per test** (when possible)
   - Focus each test on a single behavior

3. **Arrange-Act-Assert pattern**
   - Setup → Execute → Verify

4. **Use fixtures for common setup**
   - Database connections
   - Test data
   - Mock objects

5. **Test edge cases**
   - Empty inputs
   - None values
   - Invalid data
   - Error conditions

## Coverage Goals

### Current Status
- **Overall**: 97%
- **Target**: 80% minimum

### Coverage by Module
| Module | Coverage | Status |
|--------|----------|--------|
| config.py | 100% | ✅ |
| __init__.py | 100% | ✅ |
| database.py | 99% | ✅ |
| app.py | 98% | ✅ |
| collector.py | 97% | ✅ |
| scraper.py | 90% | ✅ |

### Maintaining Coverage

1. **Run tests before committing**
   ```bash
   make check-all
   ```

2. **Review coverage reports**
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

3. **Add tests for new features**
   - Write tests first (TDD)
   - Ensure coverage doesn't drop

4. **Check CI/CD results**
   - All tests must pass
   - Coverage must be ≥80%

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'httpx'`
```bash
# Solution: Install dev dependencies
pip install -e ".[dev]"
```

**Issue**: Tests fail with database errors
```bash
# Solution: Ensure test database is cleaned up
rm -f test.db
pytest --cache-clear
```

**Issue**: Coverage report not generated
```bash
# Solution: Install pytest-cov
pip install pytest-cov
```

**Issue**: Slow test execution
```bash
# Solution: Run without coverage
pytest --no-cov -q
```

## Performance

### Test Execution Time
- All tests (129): ~95 seconds
- Demo tests (11): ~1 second
- Unit tests (118): ~94 seconds

### Optimization Tips
1. Use `pytest-xdist` for parallel execution
2. Run quick tests first with `-k`
3. Use `--lf` to run only failed tests
4. Skip slow tests with markers

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Mocking](https://docs.python.org/3/library/unittest.mock.html)
