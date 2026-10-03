import os
import json
import tarfile
import glob

INPUT_FOLDER = "./"
OUTPUT_FOLDER = "./non-default backup"

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

def get_unique_output_path(output_dir, filename):
    """
    Menghasilkan path file unik.
    Contoh: device_template.json -> device_template_1.json -> device_template_2.json
    """
    base_path = os.path.join(output_dir, filename)
    if not os.path.exists(base_path):
        return base_path

    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(output_dir, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def check_and_extract_tar():
    existing_jsons = [f for f in VMANAGE_JSON_FILES if os.path.exists(os.path.join(INPUT_FOLDER, f))]
    
    if existing_jsons:
        print("[i] File JSON backup vManage ditemukan. Melanjutkan ke pemfilteran...")
        return True

    print("[!] File JSON backup belum ada. Mencari file archive .tar.gz...")
    tar_files = glob.glob(os.path.join(INPUT_FOLDER, "*.tar.gz"))

    if tar_files:
        tar_path = tar_files[0]
        print(f"[+] Mengekstrak '{tar_path}' ke '{INPUT_FOLDER}'...")
        try:
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=INPUT_FOLDER)
            print("[+] Ekstraksi berhasil.")
            return True
        except Exception as e:
            print(f"[-] Gagal mengekstrak {tar_path}: {e}")
            return False
    else:
        print("[-] Tidak ditemukan file JSON vManage maupun file .tar.gz.")
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
        return

    # Tentukan path output unik agar tidak menimpa file lama
    output_path = get_unique_output_path(OUTPUT_FOLDER, filename)
    out_filename = os.path.basename(output_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Gagal membaca {filename}: {e}")
            return

    filtered_data = filter_recursive(data)
    total_custom = count_items(filtered_data.get("configuration", filtered_data))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4)
        
    print(f"[OK] {out_filename:<30} -> {total_custom} custom item disimpan.")

def main():
    print("=" * 65)
    print("  MEMPROSES FILTER BACKUP VMANAGE (CUSTOM ITEMS ONLY)  ")
    print("=" * 65)

    if not check_and_extract_tar():
        print("Proses dibatalkan.")
        return

    print("\n--- Memulai Pemfilteran ---")
    for filename in VMANAGE_JSON_FILES:
        process_file(filename)
            
    print("=" * 65)
    print(f"Selesai! Hasil backup bersih tersimpan di: '{OUTPUT_FOLDER}'")

if __name__ == "__main__":
    main()