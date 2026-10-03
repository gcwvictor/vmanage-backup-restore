import os
import json
import tarfile

INPUT_FOLDER = "./"
OUTPUT_FOLDER = "./non-default backup"
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

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_unique_filepath(directory, filename):
    """
    Menghasilkan path file unik jika file dengan nama sama sudah ada.
    Mendukung format nama file tunggal maupun ekstensi ganda seperti .tar.gz
    Contoh: 
      - device_template.json -> device_template_1.json -> device_template_2.json
      - config_backup_non-default.tar.gz -> config_backup_non-default_1.tar.gz
    """
    base_path = os.path.join(directory, filename)
    if not os.path.exists(base_path):
        return base_path

    if filename.endswith(".tar.gz"):
        name = filename[:-7]
        ext = ".tar.gz"
    else:
        name, ext = os.path.splitext(filename)

    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(directory, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1

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

def process_file(filename):
    input_path = os.path.join(INPUT_FOLDER, filename)

    if not os.path.exists(input_path):
        return None

    # Versioning/penamaan unik untuk file JSON di folder output
    output_path = get_unique_filepath(OUTPUT_FOLDER, filename)
    out_filename = os.path.basename(output_path)

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
        
    print(f"[OK] {out_filename:<35} -> {total_custom} custom item disimpan.")
    return output_path

def create_tar_gz(saved_files):
    # Versioning/penamaan unik untuk file archive .tar.gz
    output_tar_path = get_unique_filepath(INPUT_FOLDER, OUTPUT_TAR_NAME)
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

def main():
    print("=" * 65)
    print("  MEMPROSES FILTER BACKUP VMANAGE (CUSTOM ITEMS ONLY)  ")
    print("=" * 65)

    if not check_and_extract_tar():
        print("Proses dibatalkan.")
        return

    print("\n--- Memulai Pemfilteran ---")
    saved_files = []
    for filename in VMANAGE_JSON_FILES:
        res_path = process_file(filename)
        if res_path:
            saved_files.append(res_path)
            
    if saved_files:
        create_tar_gz(saved_files)
    else:
        print("[-] Tidak ada file JSON yang berhasil diproses.")

    print("=" * 65)
    print(f"Selesai! Hasil backup bersih tersimpan di folder: '{OUTPUT_FOLDER}'")

if __name__ == "__main__":
    main()
