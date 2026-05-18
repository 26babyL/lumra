import requests
import pandas as pd

# --- KONFIGURASI ---
TOKEN = "$2y$13$erN8m249faiqirVt.CfK5uLszUGW9JugVSeQvQvO0ECtTLDdf6.lm"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
BASE_UPLOAD = "http://195.35.52.86/omniinventoryapi/apinushal/msappupload"
FILE_CSV = "master_mapping_id_baru.csv" # Pastikan file ini ada

# Kemungkinan URL endpoint untuk Upload
POSSIBLE_URLS = [
    f"{BASE_UPLOAD}/upload",      # Paling umum
    f"{BASE_UPLOAD}/save",        # Paling umum
    f"{BASE_UPLOAD}/import",       # Umum untuk file
    f"{BASE_UPLOAD}/process",      # Umum untuk proses
    f"{BASE_UPLOAD}/create",       # Pencatatan data baru
]

def prepare_dummy_data():
    """Buat data dummy kecil untuk tes koneksi"""
    df = pd.DataFrame([{
        "ItemID": "TEST123", 
        "ItemCode": "TEST01", 
        "ItemName": "Tes Koneksi API",
        "ItemStock": 0
    }])
    return df.to_dict(orient='records')

def try_all_endpoints():
    dummy_data = prepare_dummy_data()
    
    print("🚀 Mencoba menghubungi beberapa URL upload...\n")
    
    for url in POSSIBLE_URLS:
        try:
            print(f"👉 Mencoba: {url}")
            response = requests.post(url, json=dummy_data, headers=HEADERS, timeout=5)
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"   ✅ SUKSES! (Status: {response.status_code})")
                print(f"   Pesan: {response.text}")
                print("-" * 50)
                return url # Kembalikan URL yang berhasil
            elif response.status_code == 404:
                print(f"   ❌ 404 (Alamat Salah)")
            elif response.status_code == 500:
                print(f"   ⚠️  500 Error Internal (Alamat Benar, tapi format data salah)")
                # 500 sering terjadi jika format JSON tidak match, tapi URLnya sudah ketemu
                print(f"   💡 KEMUNGKINAN BESAR INI URL YANG BENAR!")
                print("-" * 50)
                return url
            else:
                print(f"   ❓ Status: {response.status_code} -> {response.text[:50]}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print("\nTidak ada URL yang merespons dengan baik.")
    return None

if __name__ == "__main__":
    found_url = try_all_endpoints()
    
    if found_url:
        print(f"\n🎉 URL YANG DITEMUKAN: {found_url}")
        print("Silakan gunakan URL ini di script utama Anda.")
    else:
        print("\nGagal menemukan URL otomatis. Harap cari manual lewat Network tab (F12).")