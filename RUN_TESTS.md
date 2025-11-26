# 🧪 Quick Test Reference

Run tests **without any API keys or external services!**

---

## ⚡ Quick Start

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run all mocked tests
pytest tests/test_agent_mocked.py tests/test_tools.py tests/test_api.py tests/test_models.py -v

# Or simply
pytest -v
```

---

## 📋 Common Commands

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_models.py -v
pytest tests/test_agent_mocked.py -v
pytest tests/test_tools.py -v
pytest tests/test_api.py -v
```

### Run Specific Test
```bash
pytest tests/test_models.py::test_chat_message_creation -v
pytest tests/test_agent_mocked.py::test_greeting_response -v
```

### Run with Short Output
```bash
pytest -q
```

### Stop on First Failure
```bash
pytest -x
```

### Show Print Statements
```bash
pytest -s
```

### Run Last Failed Tests
```bash
pytest --lf
```

---

## 📊 Current Status

```
✅ test_models.py          22 tests    ALL PASSING
✅ test_agent_mocked.py    15+ tests   FULLY MOCKED
✅ test_tools.py           18+ tests   FULLY MOCKED
✅ test_api.py             20+ tests   FULLY MOCKED

Total: 70+ tests, all mocked, no external services needed
```

---

## 🚫 What You DON'T Need

- ❌ No OpenAI API key
- ❌ No Anthropic API key
- ❌ No database setup
- ❌ No environment variables
- ❌ No internet connection
- ❌ No external services

---

## ✅ What You DO Need

- ✅ Python 3.8+ (you have 3.13.7)
- ✅ pytest installed (`pip install pytest pytest-asyncio`)
- ✅ Virtual environment activated
- ✅ That's it!

---

## 🎯 Test Verification

Run this to verify everything works:

```bash
cd /Users/vjt/Desktop/lyzr-assessment-1
source venv/bin/activate
pytest tests/test_models.py -v
```

Expected output:
```
============================== 22 passed in 0.02s ==============================
```

---

## 📖 More Information

- **Full guide:** `tests/README.md`
- **Summary:** `TESTING_SUMMARY.md`
- **Configuration:** `pytest.ini`
- **Fixtures:** `tests/conftest.py`

---

## 🆘 Troubleshooting

### ImportError
```bash
# Make sure you're in project root
cd /Users/vjt/Desktop/lyzr-assessment-1

# Activate venv
source venv/bin/activate
```

### Module Not Found
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock
```

### Tests Not Found
```bash
# Check you're in the right directory
pwd  # Should show: /Users/vjt/Desktop/lyzr-assessment-1

# List test files
ls tests/test_*.py
```

---

## 🎉 Success!

If you see this:
```
============================== XX passed in X.XXs ==============================
```

**All tests are passing!** No external services needed! 🚀

---

*For detailed documentation, see `tests/README.md`*

