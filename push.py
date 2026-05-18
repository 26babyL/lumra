import requests
import pandas as pd
import logging
import os
import time
from urllib.parse import quote

# --- KONFIGURASI ---
URL_UPDATE = "http://195.35.52.86/omniinventoryapi/apinushal/msitmitem/createdataupload"
# KEMBALI KE URL USER YANG LAMA
URL_LOGIN_PING = "http://195.35.52.86/omniinventoryapi/apinushal/msgenuser/loadalluserlogininventories"
TOKEN = "2y$13$erN8m249faiqirVt.CfK5uLszUGW9JugVSeQvQvO0ECtTLDdf6.lm"
FILE_CSV = "master_mapping_id_baru.csv"
BATCH_SIZE = 1000

# Default values
DEFAULT_PAYLOAD_VALUES = {
    "QuantityIn": "Pieces",
    "QuantityConverterIn": "Pieces",
    "Active": "1",
    "isMerchandise": "0",
    "Weight": "0",
    "Length": "0",
    "Breadth": "0",
    "Height": "0",
    "Remarks": "-",
    "Currency": "Rp",
    "Size": "-",
    "Color": "-"
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_payload_from_csv(file_path):
    try:
        logger.info(f"📂 Membaca file: {file_path}")
        df = pd.read_csv(file_path)
        df = df.fillna('')
        
        payload_list = []
        
        for index, row in df.iterrows():
            item_code = str(row.get('ItemCode', '')).strip()
            item_name = str(row.get('ItemName', row.get('Name', ''))).strip()
            
            if not item_code:
                continue
            
            payload = {
                "ItemParentName": str(row.get('ItemParentName', 'General')).strip(),
                "ItemCode": item_code,
                "ItemName": item_name,
                "Barcode": str(row.get('Barcode', item_code)).strip(),
                "PurchasePrice": str(row.get('PurchasePrice', '0')).replace('.0', ''),
                "SellPrice": str(row.get('SellPrice', '0')).replace('.0', ''),
                "Group": str(row.get('Group', '-')).strip(),
            }
            
            for key, value in DEFAULT_PAYLOAD_VALUES.items():
                payload[key] = value
            
            for col in df.columns:
                if col not in payload:
                    payload[col] = str(row[col])

            payload_list.append(payload)
            
        logger.info(f"✅ {len(payload_list)} data siap dikirim.")
        return payload_list

    except Exception as e:
        logger.error(f"❌ Gagal memproses CSV: {e}")
        return []

def get_fresh_cookie():
    """
    Mengambil Cookie segar secara manual dan mengembalikannya sebagai string.
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://195.35.52.86/nushal/"
    })

    try:
        logger.info(f"🔄 Ping URL: {URL_LOGIN_PING}")
        response = session.get(URL_LOGIN_PING, timeout=10)
        
        if response.status_code == 200:
            # Ambil cookie dari response
            cookies = session.cookies.get_dict()
            if '_csrf' in cookies:
                csrf_val = cookies['_csrf']
                # Format manual string cookie persis seperti browser
                # requests biasanya menghandle url-encoding, tapi kita buat manual untuk aman
                cookie_str = f"_csrf={csrf_val}"
                logger.info(f"✅ Cookie didapat: {cookie_str[:50]}...")
                return cookie_str
            else:
                logger.warning("⚠️ Cookie _csrf tidak ditemukan di respon.")
                return None
        else:
            logger.warning(f"⚠️ Ping gagal status: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Gagal mengambil cookie: {e}")
        return None

def main():
    # 1. Ambil Cookie Manual
    fresh_cookie = get_fresh_cookie()
    
    if not fresh_cookie:
        logger.error("💥 Gagal mendapatkan cookie. Program berhenti.")
        return

    # 2. Siapkan Data
    if not os.path.exists(FILE_CSV):
        logger.error(f"File CSV '{FILE_CSV}' tidak ditemukan!")
        return
        
    data_payload = prepare_payload_from_csv(FILE_CSV)
    
    if not data_payload:
        logger.warning("Tidak ada data untuk dikirim.")
        return

    # 3. Setup Headers untuk Upload (MENGGUNAKAN COOKIE MANUAL)
    # Kita TIDAK menggunakan Session.post lagi, tapi requests.post biasa
    # agar kita bisa kontrol Cookie-nya 100%
    upload_headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": fresh_cookie,  # <-- Cookie Manual masuk sini
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://195.35.52.86/nushal/"
    }

    # 4. Proses Batching
    total_data = len(data_payload)
    total_batches = (total_data + BATCH_SIZE - 1) // BATCH_SIZE
    
    logger.info(f"🚀 Memulai upload dengan Cookie Manual...")
    logger.info(f"📊 Total Data: {total_data} | Batch Size: {BATCH_SIZE}")
    logger.info("-" * 60)

    success_count = 0
    fail_count = 0

    for i in range(0, total_data, BATCH_SIZE):
        batch_num = (i // BATCH_SIZE) + 1
        chunk = data_payload[i : i + BATCH_SIZE]
        
        logger.info(f"📦 Mengirim Batch {batch_num}/{total_batches}...")
        
        try:
            # Menggunakan requests.post biasa (bukan session)
            response = requests.post(URL_UPDATE, json=chunk, headers=upload_headers, timeout=120)
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"   ✅ Sukses Batch {batch_num}")
                success_count += len(chunk)
            else:
                logger.error(f"   ❌ Gagal Batch {batch_num}. Status: {response.status_code}")
                logger.error(f"   Detail: {response.text}")
                fail_count += len(chunk)
                if response.status_code == 401:
                    logger.error("💥 Auth Error! Cookie mungkin kadaluarsa cepat sekali.")
                    break

        except requests.exceptions.Timeout:
            logger.error(f"   ⏱️ Timeout pada Batch {batch_num}.")
            fail_count += len(chunk)
        except Exception as e:
            logger.error(f"   💥 Error: {e}")
            fail_count += len(chunk)

        time.sleep(0.5)

    logger.info("-" * 60)
    logger.info("🏁 PROSES SELESAI")
    logger.info(f"✅ Berhasil: {success_count} data")
    logger.info(f"❌ Gagal   : {fail_count} data")

if __name__ == "__main__":
    main()