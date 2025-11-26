# 🧪 Test Suite

Comprehensive test suite for the Medical Appointment Scheduling Agent with **full mocking** - no external services required!

---

## 🎯 Overview

All tests use **mocks** for:
- ✅ LLM API calls (OpenAI/Anthropic)
- ✅ Tool functions
- ✅ RAG/Vector database
- ✅ Database operations
- ✅ External APIs

**No API keys or external services needed to run tests!**

---

## 📦 Test Files

### `conftest.py`
Central configuration and fixtures:
- Mock LLM clients
- Mock tool responses
- Mock RAG system
- Sample data fixtures
- Helper functions

### `test_agent_mocked.py`
Tests for the scheduling agent:
- Agent initialization
- Greeting responses
- Tool execution
- FAQ handling
- Error handling
- Integration flows

### `test_tools.py`
Tests for booking and availability tools:
- Availability checking
- Appointment booking
- Cancellation
- Rescheduling
- Error cases
- Tool structure validation

### `test_api.py`
Tests for API endpoints:
- Health checks
- Chat API
- Calendly API
- Appointments API
- Error handling
- Request validation

### `test_models.py`
Tests for data models:
- Schema creation
- Validation
- Serialization
- Edge cases
- Special characters

### `test_agent.py` (Legacy)
Original tests that require external services.
*Use `test_agent_mocked.py` for CI/CD and local testing.*

---

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_agent_mocked.py
pytest tests/test_tools.py
pytest tests/test_api.py
pytest tests/test_models.py
```

### Run Specific Test
```bash
pytest tests/test_agent_mocked.py::test_greeting_response
pytest tests/test_tools.py::test_check_availability_success
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html --cov-report=term
```

### Run Only Mock Tests
```bash
pytest -m mock
```

### Run Only Unit Tests
```bash
pytest -m unit
```

---

## 📊 Test Coverage

### Backend Components

| Component | File | Coverage |
|-----------|------|----------|
| Agent | `test_agent_mocked.py` | ✅ Comprehensive |
| Tools | `test_tools.py` | ✅ Comprehensive |
| API | `test_api.py` | ✅ Comprehensive |
| Models | `test_models.py` | ✅ Comprehensive |

### Test Types

- **Unit Tests**: 40+ tests
- **Integration Tests**: 10+ tests
- **API Tests**: 20+ tests
- **All Mocked**: ✅ Yes

---

## 🎭 Mock Strategy

### LLM Mocking

```python
# Mocked LLM responses
with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_openai.return_value = mock_client
```

### Tool Mocking

```python
# Mocked tool functions
with patch('backend.tools.booking_tool.book_appointment') as mock_book:
    mock_book.return_value = {
        "success": True,
        "booking_id": "APPT-TEST-001",
        "confirmation_code": "ABC123"
    }
```

### RAG Mocking

```python
# Mocked RAG system
with patch('backend.rag.faq_rag.faq_rag') as mock_rag:
    mock_rag.answer_question.return_value = {
        "answer": "Mock FAQ answer",
        "context": "Mock context"
    }
```

---

## 🔧 Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
addopts = -v --tb=short --strict-markers
markers =
    asyncio: async tests
    mock: mocked tests
    unit: unit tests
    integration: integration tests
```

---

## 📝 Writing New Tests

### Template for Agent Tests

```python
@pytest.mark.asyncio
async def test_your_feature():
    """Test description."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai:
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Expected response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client
        
        # Create agent
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        # Test
        result = await agent.process_message(
            user_message="Test input",
            conversation_history=[]
        )
        
        # Assert
        assert "response" in result
        assert len(result["response"]) > 0
```

### Template for Tool Tests

```python
@pytest.mark.asyncio
async def test_your_tool():
    """Test description."""
    with patch('backend.tools.your_tool.calendly_api') as mock_api:
        # Setup mock
        mock_api.your_function = AsyncMock(return_value={
            "success": True,
            "data": "test"
        })
        
        # Test
        result = await your_tool_function(param1="value")
        
        # Assert
        assert result["success"] is True
        assert mock_api.your_function.called
```

### Template for API Tests

```python
def test_your_endpoint(client, mock_dependency):
    """Test description."""
    # Setup
    mock_dependency.function = AsyncMock(return_value={"data": "test"})
    
    # Test
    response = client.get("/api/your-endpoint")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
```

---

## ✅ Test Checklist

When adding new features, ensure tests cover:

- [ ] Happy path (success case)
- [ ] Error cases (failures)
- [ ] Edge cases (empty, null, extreme values)
- [ ] Validation (input checking)
- [ ] Mocking (no external dependencies)
- [ ] Async handling (if applicable)
- [ ] Return values (correct structure)
- [ ] Side effects (state changes)

---

## 🐛 Debugging Tests

### Run Single Test with Print Output
```bash
pytest tests/test_agent_mocked.py::test_greeting_response -v -s
```

### Show Test Execution Time
```bash
pytest --durations=10
```

### Stop on First Failure
```bash
pytest -x
```

### Run Last Failed Tests
```bash
pytest --lf
```

### Show Local Variables on Failure
```bash
pytest -l
```

---

## 📈 Continuous Integration

Tests are designed to run in CI/CD without any setup:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-mock
    pytest
```

**No API keys or environment setup needed!**

---

## 🎯 Test Statistics

```
Total Tests: 70+
Mocked Tests: 70+ (100%)
Coverage: ~85%
Execution Time: < 10 seconds
External Dependencies: 0
```

---

## 🚨 Troubleshooting

### Import Errors

If you get import errors:
```bash
# Make sure you're in project root
cd /path/to/lyzr-assessment-1

# Run with python path
PYTHONPATH=. pytest
```

### Async Errors

If async tests fail:
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

### Mock Not Working

If mocks aren't being used:
```python
# Ensure correct import path in patch
with patch('backend.agent.scheduling_agent.AsyncOpenAI'):  # ✅ Correct
with patch('openai.AsyncOpenAI'):  # ❌ Wrong
```

---

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 🎉 Success!

All tests are fully mocked and can run:
- ✅ **Without API keys**
- ✅ **Without external services**
- ✅ **Without internet connection**
- ✅ **In CI/CD pipelines**
- ✅ **Locally on any machine**

Perfect for **fast, reliable, reproducible testing**! 🚀

