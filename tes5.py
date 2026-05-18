import os
import logging
import requests
import pandas as pd
from typing import Optional, List, Dict

# --- KONFIGURASI ---
TOKEN = os.getenv("API_TOKEN", "$2y$13$erN8m249faiqirVt.CfK5uLszUGW9JugVSeQvQvO0ECtTLDdf6.lm") 
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}
URL_EXTRACT = "http://195.35.52.86/omniinventoryapi/apinushal/extract/extractitemstock"
FILE_MASTER = "master_mapping_id_baru.csv"

# --- SETUP LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def fetch_data_from_api(url: str, headers: Dict, timeout: int = 120) -> Optional[List[Dict]]:
    """Mengambil data mentah dari API."""
    try:
        logger.info(f"📡 Mengambil data dari {url}...")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  
        
        raw_data = response.json()
        items = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
        logger.info(f"✅ Berhasil mengambil {len(items)} baris data dari server.")
        return items
        
    except requests.exceptions.Timeout:
        logger.error("❌ Koneksi timeout.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Gagal menghubungi server: {e}")
    except ValueError as e:
        logger.error(f"❌ Gagal memparsing JSON: {e}")
        
    return None

def clean_new_data(items: List[Dict]) -> pd.DataFrame:
    """
    Membersihkan data. Menyimpan SEMUA kolom, bukan cuma ID & Code.
    """
    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)
    
    # Cek kolom kunci
    if 'ItemID' not in df.columns:
        logger.error("⚠️ Struktur data API salah (kurang ItemID).")
        return pd.DataFrame()

    # Normalisasi nama kolom ItemCode jika perlu
    if 'Item_Code' in df.columns and 'ItemCode' not in df.columns:
        df['ItemCode'] = df['Item_Code']

    # Bersihkan ItemID (wajib string dan strip spasi)
    df['ItemID'] = df['ItemID'].astype(str).str.strip()
    
    # Bersihkan ItemCode jika ada
    if 'ItemCode' in df.columns:
        df['ItemCode'] = df['ItemCode'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

    # Hapus baris dengan ID kosong
    df = df[(df['ItemID'] != '') & (df['ItemID'] != 'nan')]
    
    # Kembalikan semua kolom (jangan filter kolom disini)
    return df.copy()

def load_local_data(file_path: str) -> pd.DataFrame:
    """Memuat database lokal."""
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Pastikan ID di file lama juga string agar matching berhasil
            if 'ItemID' in df.columns:
                df['ItemID'] = df['ItemID'].astype(str)
            logger.info(f"📁 Database lokal dimuat: {len(df)} item.")
            return df
        except Exception as e:
            logger.warning(f"⚠️ Gagal baca file lama: {e}. Membuat database baru.")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def merge_and_save(df_old: pd.DataFrame, df_new: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """
    Menggabungkan data dengan logika UPDATE.
    Jika ID sama, data baru (df_new) akan menimpa data lama (df_old).
    """
    if df_new.empty:
        return df_old

    # 1. Pastikan tipe data ItemID konsisten (String)
    # (df_new sudah dibersihkan di clean_new_data, pastikan df_old juga)
    if not df_old.empty and 'ItemID' in df_old.columns:
        df_old['ItemID'] = df_old['ItemID'].astype(str)
    
    # 2. Gabungkan: Data Lama + Data Baru
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    
    # 3. Hapus Duplikat berdasarkan ItemID
    # keep='last' berarti: Jika ada ID ganda, ambil yang paling belakang (yaitu data baru)
    df_final = df_combined.drop_duplicates(subset=['ItemID'], keep='last')
    
    # 4. Simpan
    try:
        df_final.to_csv(file_path, index=False)
        
        old_count = len(df_old)
        new_count = len(df_final)
        
        logger.info("-" * 50)
        logger.info(f"✅ Sinkronisasi Selesai!")
        logger.info(f"📦 Total database akhir    : {new_count} item.")
        logger.info(f"💾 Database diperbarui di : {file_path}")
        logger.info("-" * 50)
        return df_final
    except Exception as e:
        logger.error(f"❌ Gagal menyimpan file: {e}")
        return df_old

def build_master_mapping():
    logger.info("🚀 Memulai Sinkronisasi Database (Mode Update)...")
    
    df_old = load_local_data(FILE_MASTER)
    raw_items = fetch_data_from_api(URL_EXTRACT, HEADERS)
    
    if raw_items is None:
        return None

    df_new = clean_new_data(raw_items)
    df_final = merge_and_save(df_old, df_new, FILE_MASTER)
    
    return df_final

if __name__ == "__main__":
    build_master_mapping()