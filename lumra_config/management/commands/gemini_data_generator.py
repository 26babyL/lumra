#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════
  GEMINI DATA GENERATOR — Generate realistis coffee shop data
  
  Menggunakan Google Generative AI untuk create data yang:
  - Realistis sesuai konsep coffee shop
  - Creative & variatif (Starbucks, Fore, Kopi Kenangan, etc)
  - Context-aware untuk alur bisnis LUMRA ERP
═══════════════════════════════════════════════════════════════════════
"""

import google.generativeai as genai
import json
import re
from typing import List, Dict, Any

# Configure Gemini
import time
genai.configure(api_key="AIzaSyAjHu-TizS48cZ_01Rngz1HFtUY1ZwrAnE")

# Try different model names - some work, some don't depending on library version
try:
    # Try newest first
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception:
    try:
        # Fallback to stable version
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        try:
            # Last resort - use gemini-pro
            model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            # If all fail, create a dummy model that returns fallback data
            print(f"Warning: All Gemini models failed ({e}). Using hardcoded data only.")
            model = None

# Rate limiting - to avoid ResourceExhausted
RATE_LIMIT_DELAY = 3  # seconds between requests

class CoffeeShopDataGenerator:
    """Generate realistic coffee shop data using Gemini AI"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.cache = {}
    
    def _prompt(self, prompt_text: str) -> str:
        """Helper untuk call Gemini API dengan rate limiting"""
        # If model initialization failed, return None to trigger fallback
        if model is None:
            return None
        
        # Apply rate limiting to avoid ResourceExhausted
        time.sleep(RATE_LIMIT_DELAY)
            
        if self.verbose:
            print(f"  [*] Gemini generating... ", end='', flush=True)
        
        try:
            response = model.generate_content(prompt_text)
            result = response.text.strip()
            if self.verbose:
                print("[OK]")
            return result
        except Exception as e:
            if self.verbose:
                print(f"[SKIP] {type(e).__name__}")
            return None
    
    # ─── PHASE 0: SETUP DATA ─────────────────────────────────────
    
    def generate_business_names(self, count: int = 5) -> List[str]:
        """Generate realistic coffee shop names (Starbucks style, Kopi Kenangan, etc)"""
        prompt = f"""
        Generate {count} creative Indonesian/English coffee shop business names inspired by:
        - Starbucks (premium, international)
        - Kopi Kenangan (local, affordable)
        - Fore Coffee (modern, trendy)
        - Coffeeology (specialty)
        
        Requirements:
        - Each name should be 1-4 words
        - Mix of Indonesian and English
        - Sound modern and professional
        - Suitable for F&B business
        
        Return ONLY a JSON array of names, NO explanation:
        ["Name1", "Name2", "Name3", ...]
        """
        
        response = self._prompt(prompt)
        try:
            names = json.loads(response)
            return names[:count]
        except:
            return [f"LUMRA Cafe {i}" for i in range(1, count + 1)]
    
    def generate_business_details(self, business_name: str) -> Dict[str, str]:
        """Generate bisnis details: industry, address, phone, email"""
        cache_key = f"business_{business_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""
        For coffee shop business named "{business_name}", generate realistic details:
        
        Return ONLY valid JSON format (no markdown, no extra text):
        {{
            "industry": "F&B",
            "phone": "+62xxxxxxxxx",
            "email": "info@example.com",
            "address": "Jl. Street Name No. XX, City District"
        }}
        """
        
        response = self._prompt(prompt)
        try:
            data = json.loads(response)
            self.cache[cache_key] = data
            return data
        except:
            return {
                "industry": "F&B",
                "phone": "021-8888-9999",
                "email": f"info@{business_name.lower().replace(' ', '')}.com",
                "address": "Jl. Merdeka No. 1, Jakarta Pusat"
            }
    
    def generate_locations(self, business_name: str, count: int = 4) -> List[Dict]:
        """Generate store locations dengan kode unik"""
        prompt = f"""
        Generate {count} realistic store locations for "{business_name}" coffee chain:
        
        Include types:
        - 2 store/outlet locations
        - 1 warehouse
        - 1 production kitchen
        
        Each location should have realistic Indonesian addresses (Jakarta, Bandung, Surabaya, etc)
        
        Return ONLY valid JSON (no markdown):
        [
            {{"name": "Store Name", "type": "store", "address": "Jl. ...", "city": "Jakarta"}},
            ...
        ]
        """
        
        response = self._prompt(prompt)
        try:
            locations = json.loads(response)
            # Add codes
            codes = {'store': 'TKO', 'warehouse': 'GUD', 'production': 'DPR'}
            for i, loc in enumerate(locations, 1):
                code_prefix = codes.get(loc.get('type', 'store'), 'LOK')
                loc['code'] = f"{code_prefix}-{i:03d}"
            return locations[:count]
        except:
            return [
                {"name": f"{business_name} Pusat", "code": "TKO-001", "type": "store"},
                {"name": "Gudang Utama", "code": "GUD-001", "type": "warehouse"},
                {"name": "Dapur Produksi", "code": "DPR-001", "type": "production"},
                {"name": f"{business_name} Cabang 2", "code": "TKO-002", "type": "store"},
            ]
    
    # ─── PHASE 1: MASTER DATA ────────────────────────────────────
    
    def generate_products(self, category: str, count: int = 5) -> List[Dict]:
        """Generate realistic coffee products (drinks, food, beans, etc)"""
        prompt = f"""
        Generate {count} realistic coffee shop {category} products with:
        - Professional names
        - Brief descriptions (max 2 sentences)
        - Realistic unit (pcs, liter, kg, cup, etc)
        
        Context: Premium Indonesian coffee chain like Starbucks, Kopi Kenangan, Fore
        
        Examples for reference:
        - Category "minuman": Espresso, Americano, Latte, Cappuccino, Cold Brew
        - Category "makanan": Croissant, Sandwich, Cake, Pastry, Donut
        - Category "biji kopi": Arabica Specialty, Robusta Premium, Blend Signature
        
        Return ONLY valid JSON:
        [
            {{"name": "Product Name", "description": "Description", "unit": "cup/pcs/kg"}},
            ...
        ]
        """
        
        response = self._prompt(prompt)
        try:
            products = json.loads(response)
            return products[:count]
        except:
            default_map = {
                'minuman': [
                    {"name": "Espresso", "description": "Single shot espresso", "unit": "cup"},
                    {"name": "Americano", "description": "Espresso with hot water", "unit": "cup"},
                    {"name": "Latte", "description": "Espresso with steamed milk", "unit": "cup"},
                    {"name": "Cappuccino", "description": "Espresso with foamed milk", "unit": "cup"},
                    {"name": "Cold Brew", "description": "Smooth cold coffee", "unit": "cup"},
                ],
                'makanan': [
                    {"name": "Croissant", "description": "Buttery pastry", "unit": "pcs"},
                    {"name": "Sandwich", "description": "Ham & cheese sandwich", "unit": "pcs"},
                    {"name": "Cake Slice", "description": "Chocolate or Vanilla", "unit": "pcs"},
                    {"name": "Pastry", "description": "Assorted pastries", "unit": "pcs"},
                    {"name": "Donut", "description": "Glazed or filled", "unit": "pcs"},
                ],
                'biji_kopi': [
                    {"name": "Arabica Specialty", "description": "Premium arabica beans", "unit": "kg"},
                    {"name": "Robusta Premium", "description": "Bold robusta blend", "unit": "kg"},
                    {"name": "Signature Blend", "description": "House blend mix", "unit": "kg"},
                    {"name": "Single Origin Ethiopia", "description": "Yirgacheffe origin", "unit": "kg"},
                    {"name": "Espresso Blend", "description": "Optimized for espresso", "unit": "kg"},
                ]
            }
            return default_map.get(category, [])[:count]
    
    def generate_suppliers(self, product_type: str = "coffee_beans", count: int = 3) -> List[Dict]:
        """Generate realistic coffee suppliers"""
        prompt = f"""
        Generate {count} realistic Indonesian coffee {product_type} suppliers:
        - Vendor names (distributor, farm, importer)
        - Contact details
        - Specialization
        
        Context: Supply for premium coffee shop chain
        
        Return ONLY valid JSON:
        [
            {{"name": "Supplier Name", "phone": "+62xxx", "email": "vendor@...", "specialty": "..."}},
            ...
        ]
        """
        
        response = self._prompt(prompt)
        try:
            suppliers = json.loads(response)
            return suppliers[:count]
        except:
            return [
                {"name": f"Supplier {i}", "phone": f"021-{1000000+i:07d}", 
                 "email": f"supplier{i}@vendor.com", "specialty": product_type}
                for i in range(1, count + 1)
            ]
    
    # ─── PHASE 2: RECIPES ────────────────────────────────────────
    
    def generate_recipe_names(self, count: int = 5) -> List[str]:
        """Generate realistic recipe/formula names"""
        prompt = f"""
        Generate {count} creative recipe/formula names for coffee shop operations:
        - Coffee blends (Signature Blend, House Roast, etc)
        - Drink recipes (Caramel Macchiato Mix, etc)
        - Food recipes (Brownies, Cookies, etc)
        
        Return ONLY JSON array:
        ["Recipe 1", "Recipe 2", ...]
        """
        
        response = self._prompt(prompt)
        try:
            names = json.loads(response)
            return names[:count]
        except:
            return [f"Recipe {i}" for i in range(1, count + 1)]
    
    # ─── PHASE 3-6: OPERATIONS DATA ──────────────────────────────
    
    def generate_transaction_narrative(self, phase: str) -> str:
        """Generate realistic transaction narrative for reporting"""
        prompt = f"""
        Generate brief realistic narrative (2-3 sentences) for coffee shop {phase}:
        - Be specific with amounts, quantities, times
        - Sound like real business operations
        - Include Indonesian business context
        
        Examples:
        - Phase "procurement": "Pembelian 50kg biji kopi Arabica Specialty..."
        - Phase "production": "Proses produksi espresso blend batch..."
        - Phase "sales": "Penjualan hari Jumat siang ramai..."
        """
        
        response = self._prompt(prompt)
        return response or f"Operasional {phase} normal"


# ═════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════

def get_generator(verbose=True) -> CoffeeShopDataGenerator:
    """Singleton-like generator instance"""
    return CoffeeShopDataGenerator(verbose=verbose)


# ═════════════════════════════════════════════════════════════════
# QUICK TEST
# ═════════════════════════════════════════════════════════════════

# Safely check __name__ before executing main block
if __name__ == '__main__':
    try:
        print("Testing Gemini Data Generator...\n")
        gen = get_generator()
        
        print("[*] Business Names:")
        names = gen.generate_business_names(3)
        for name in names:
            print(f"  - {name}")
        
        print("\n[*] Business Details:")
        if names:
            details = gen.generate_business_details(names[0])
            for key, val in details.items():
                print(f"  {key}: {val}")
        
        print("\n[*] Locations:")
        if names:
            locations = gen.generate_locations(names[0], 3)
            for loc in locations:
                print(f"  {loc['code']}: {loc['name']} ({loc['type']})")
        
        print("\n[*] Products (Minuman):")
        products = gen.generate_products('minuman', 3)
        for prod in products:
            print(f"  {prod['name']} ({prod.get('unit', 'cup')})")
        
        print("\n[OK] Generator ready!")
    except Exception as e:
        print(f"[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
