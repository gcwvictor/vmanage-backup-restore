import os
import json
import tarfile
import shutil
from datetime import datetime

INPUT_FOLDER = "./"
OUTPUT_BASE_FOLDER = "./non-default backup"
DEFAULT_BACKUP_FOLDER = "./default backup"
TARGET_TAR_NAME = "config_backup_all.tar.gz"
OUTPUT_TAR_NAME = "config_backup_non-default.tar.gz"

# Daftar nama file JSON spesifik vManage
VMANAGE_JSON_FILES = [
    "device_template.json",
    "feature_template.json",
    "policy_definition.json",
    "policy_list.json",
    "security_policy.json",
    "security_policy_id.json",
    "vedge_policy.json",
    "vedge_policy_id.json",
    "vsmart_policy.json",
    "vsmart_policy_id.json"
]

def check_and_extract_tar():
    tar_path = os.path.join(INPUT_FOLDER, TARGET_TAR_NAME)
    
    # 1. Prioritaskan mengekstrak jika file config_archive.tar.gz ditemukan
    if os.path.exists(tar_path):
        print(f"[+] Ditemukan '{TARGET_TAR_NAME}'. Mengekstrak ke '{INPUT_FOLDER}'...")
        try:
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=INPUT_FOLDER)
            print("[+] Ekstraksi berhasil.")
            return True
        except Exception as e:
            print(f"[-] Gagal mengekstrak {tar_path}: {e}")
            return False

    # 2. Jika config_archive.tar.gz tidak ada, cek apakah file JSON mentah sudah tersedia
    existing_jsons = [f for f in VMANAGE_JSON_FILES if os.path.exists(os.path.join(INPUT_FOLDER, f))]
    if existing_jsons:
        print(f"[i] File '{TARGET_TAR_NAME}' tidak ditemukan, tetapi file JSON mentah terdeteksi. Melanjutkan ke pemfilteran...")
        return True

    print(f"[-] Error: File '{TARGET_TAR_NAME}' maupun file JSON vManage tidak ditemukan di '{INPUT_FOLDER}'.")
    return False

def is_custom_item(item):
    if not isinstance(item, dict):
        return True
    
    if item.get("factoryDefault") is True:
        return False
    if item.get("readOnly") is True:
        return False
    if item.get("owner") == "system" or item.get("createdBy") == "system":
        return False
    if item.get("isDefault") is True:
        return False

    return True

def filter_recursive(data):
    if isinstance(data, list):
        return [filter_recursive(item) for item in data if is_custom_item(item)]
    
    elif isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                new_dict[key] = filter_recursive(value)
            else:
                new_dict[key] = value
        return new_dict
    
    return data

def count_items(data):
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        total = 0
        for k, v in data.items():
            if isinstance(v, list):
                total += len(v)
            elif isinstance(v, dict):
                total += count_items(v)
        return total
    return 0

def process_file(filename, output_dir):
    input_path = os.path.join(INPUT_FOLDER, filename)

    if not os.path.exists(input_path):
        return None

    # Simpan langsung memakai nama file asli di folder timestamp
    output_path = os.path.join(output_dir, filename)

    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Gagal membaca {filename}: {e}")
            return None

    filtered_data = filter_recursive(data)
    total_custom = count_items(filtered_data.get("configuration", filtered_data))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4)
        
    print(f"[OK] {filename:<35} -> {total_custom} custom item disimpan.")
    return output_path

def version_existing_file(base_path):
    """
    Jika base_path (file utama) sudah ada, rename file tersebut menjadi versioned filename
    seperti _2, _3, dst. sehingga base_path kosong untuk file terbaru.
    """
    if not os.path.exists(base_path):
        return

    dirname, filename = os.path.split(base_path)
    if filename.endswith(".tar.gz"):
        name = filename[:-7]
        ext = ".tar.gz"
    else:
        name, ext = os.path.splitext(filename)

    counter = 2
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(dirname, new_filename)
        if not os.path.exists(new_path):
            os.rename(base_path, new_path)
            print(f"[+] File lama diubah namanya menjadi: '{new_filename}'")
            break
        counter += 1

def create_tar_gz(saved_files):
    output_tar_path = os.path.join(INPUT_FOLDER, OUTPUT_TAR_NAME)
    
    # Versioning file lama jika config_backup_non-default.tar.gz sudah ada
    version_existing_file(output_tar_path)

    tar_filename = os.path.basename(output_tar_path)
    print(f"\n[+] Mengemas hasil filter ke file archive '{tar_filename}'...")
    
    try:
        with tarfile.open(output_tar_path, "w:gz") as tar:
            for file_path in saved_files:
                base_name = os.path.basename(file_path)
                
                # Pemetaan tepat kembali ke nama asli standar vManage
                clean_arcname = base_name
                for original_name in VMANAGE_JSON_FILES:
                    prefix = original_name.replace(".json", "")
                    if base_name.startswith(prefix):
                        clean_arcname = original_name
                        break
                
                tar.add(file_path, arcname=clean_arcname)
        print(f"[+] Berhasil membuat archive: '{output_tar_path}'")
    except Exception as e:
        print(f"[-] Gagal membuat file archive .tar.gz: {e}")

def move_raw_files_to_default_backup(timestamp_folder_name):
    """
    Memindahkan file-file JSON mentah dari INPUT_FOLDER ke:
    ./default backup/DD-MM-YYYY_HH-MM-SS/
    """
    target_dir = os.path.join(DEFAULT_BACKUP_FOLDER, timestamp_folder_name)
    os.makedirs(target_dir, exist_ok=True)
    
    moved_count = 0
    print(f"\n[+] Memindahkan file JSON mentah ke '{target_dir}'...")
    
    for filename in VMANAGE_JSON_FILES:
        raw_file_path = os.path.join(INPUT_FOLDER, filename)
        if os.path.exists(raw_file_path):
            dest_path = os.path.join(target_dir, filename)
            shutil.move(raw_file_path, dest_path)
            moved_count += 1
            
    if moved_count > 0:
        print(f"[+] Berhasil memindahkan {moved_count} file JSON mentah.")
    else:
        print("[-] Tidak ada file JSON mentah yang dipindahkan.")

def main():
    print("=" * 65)
    print("  MEMPROSES FILTER BACKUP VMANAGE (CUSTOM ITEMS ONLY)  ")
    print("=" * 65)

    if not check_and_extract_tar():
        print("Proses dibatalkan.")
        return

    # Gunakan satu timestamp yang sama untuk kedua folder
    timestamp_str = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    
    # Buat sub-folder non-default backup berbasis timestamp
    current_non_default_folder = os.path.join(OUTPUT_BASE_FOLDER, timestamp_str)
    os.makedirs(current_non_default_folder, exist_ok=True)

    print("\n--- Memulai Pemfilteran ---")
    saved_files = []
    for filename in VMANAGE_JSON_FILES:
        res_path = process_file(filename, current_non_default_folder)
        if res_path:
            saved_files.append(res_path)
            
    if saved_files:
        create_tar_gz(saved_files)
        # Pindahkan file JSON mentah ke default backup dengan nama timestamp yang sama
        move_raw_files_to_default_backup(timestamp_str)
    else:
        print("[-] Tidak ada file JSON yang berhasil diproses.")

    print("=" * 65)
    print(f"Selesai! Hasil backup bersih tersimpan di folder: '{current_non_default_folder}'")

if __name__ == "__main__":
    main()