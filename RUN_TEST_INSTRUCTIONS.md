# Quick test runner - Configure and Run

The **RECOMMENDED** way to run the test is via Django shell:

```powershell
cd d:\APPS\Project\lumra
.venv\Scripts\python manage.py shell
```

Then in the Python shell, run:

```python
# Load and execute the test
with open('lumra_config/management/commands/test_setup_with_gemini.py', 'r') as f:
    code = f.read()
    exec(code)
```

---

## ALTERNATIVE: Direct Python (for future use)

To enable direct Python execution (`python run_test.py`), the script needs proper sys.path setup which is complex with the project structure.

The Django shell approach is simpler and more reliable.

---

## QUICK COMMAND (Copy & Paste)

```powershell
cd d:\APPS\Project\lumra; Get-Content lumra_config/management/commands/test_setup_with_gemini.py | .venv\Scripts\python manage.py shell
```

This command will:
1. Run Django shell via manage.py
2. Pipe the test script into it
3. Execute all test phases with Gemini AI integration
4. Display results with proper output formatting

---

## KONFIGURASI TEST

If you want to change test behavior, edit `test_setup_with_gemini.py` around line 50:

```python
USE_TRANSACTION = False  # False = keep data, True = rollback
USE_GEMINI = True        # True = AI data, False = hardcoded fallback  
PRINT_STOCK_AT_EACH_STEP = True
```

Then run the command again with the same pipe.
