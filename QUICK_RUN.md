# ⚡ QUICK START — Run LUMRA ERP Test

## 🎯 Run Test NOW

```powershell
cd d:\APPS\Project\lumra
python manage.py test_with_gemini
```

That's it! The test will:
- ✓ Initialize Django properly
- ✓ Load all models correctly
- ✓ Execute test phases
- ✓ Display results in console

---

## 📊 What Gets Tested

The test creates and validates:
- Categories (Minuman, Makanan, etc.)
- Locations (Store, Warehouse, Kitchen)  
- Units (Cup, Pcs, Kg, Liter)
- Vendors (Coffee suppliers)
- Products (Espresso, Latte, etc.)
- Stock levels
- Customer data
- ... and more (7 phases total)

---

## 🔧 If Test Fails

### Error: "models/gemini-1.5-flash is not found"
- This is OK! The test falls back to hardcoded data automatically
- Continue running - it will complete

### Error: "name 'X' is not defined"
- This is a missing model reference
- Check [TEST_EXECUTION_SUMMARY.md](TEST_EXECUTION_SUMMARY.md) for details

### Error: "No module named..."
- Use this instead:
  ```bash
  python manage.py shell
  ```
  Then in Python shell:
  ```python
  exec(open('lumra_config/management/commands/test_setup_with_gemini.py').read())
  ```

---

## 📝 Configuration

Edit this file to change test behavior:
```
lumra_config/management/commands/test_setup_with_gemini.py
```

Line ~50:
```python
USE_TRANSACTION = False  # False = keep data, True = rollback
USE_GEMINI = True        # True = AI data, False = hardcoded only
PRINT_STOCK_AT_EACH_STEP = True
```

---

## ✅ Success Looks Like

You'll see output like:

```
[OK] Starting LUMRA ERP Full Flow Test with Gemini AI

═════════════════════════════════════════════════════════════════
  LUMRA ERP ✓ FULL FLOW TEST DENGAN GEMINI AI
═════════════════════════════════════════════════════════════════

  FASE 0: SETUP AWAL
  ├─ STEP 0.1: Setup Nama Bisnis
  │  ✓ Business Name: LUMRA Premium Coffee
  └─ STEP 0.2: Setup Locations
     ✓ Location: LOC-001 (Main Store)

  FASE 1: MASTER DATA
  ...

[OK] Test completed successfully!
```

---

## 🚀 What's Fixed

✓ ModuleNotFoundError - Now uses proper Django management command  
✓ Import errors - Updated to use existing models only  
✓ Execution flow - Test auto-runs when imported  
✓ Console encoding - ASCII-only output for Windows  
✓ Syntax errors - Fixed try-except blocks  

---

## 📚 More Info

- Full details: [TEST_EXECUTION_SUMMARY.md](TEST_EXECUTION_SUMMARY.md)
- Setup guide: [TEST_GEMINI_SETUP_GUIDE.md](TEST_GEMINI_SETUP_GUIDE.md)  
- Runner config: [RUN_TEST_INSTRUCTIONS.md](RUN_TEST_INSTRUCTIONS.md)

---

**Ready?** Run: `python manage.py test_with_gemini`
