import hashlib
import os
import json

def hash_file(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def generate_table():
    directory = input("Enter the directory path to hash: ")
    
    if not os.path.isdir(directory):
        print("Invalid directory path!")
        return

    hash_results = {}
    
    for filename in os.listdir(directory):
        if filename.startswith('.'):
            continue 
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            file_hash = hash_file(path)
            hash_results[path] = file_hash
            print(f"Hashed: {filename}")

    with open("hash_table.json", "w") as f:
        json.dump(hash_results, f, indent=4)
    
    print("\n--- Hash table generated and saved to hash_table.json ---")

def validate_hashes():
    if not os.path.exists("hash_table.json"):
        print("No hash table found. Generate one first.")
        return

    with open("hash_table.json", "r") as f:
        stored_hashes = json.load(f)

    if not stored_hashes:
        print("Hash table is empty.")
        return
    
    first_path = list(stored_hashes.keys())[0]
    directory = os.path.dirname(first_path)
    
    files_on_disk = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.startswith('.'):
                continue
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                files_on_disk.append(path)
    else:
        print("Directory not found.")
        return

    missing_files = [p for p in stored_hashes if not os.path.exists(p)]
    new_files = [p for p in files_on_disk if p not in stored_hashes]
    
    renames_detected = False

    for new_path in list(new_files): 
        new_hash = hash_file(new_path)
        
        for old_path in missing_files:
            if stored_hashes[old_path] == new_hash:
                print(f"[rename detected] {old_path} -> {new_path}")
                
                stored_hashes[new_path] = stored_hashes.pop(old_path)
                
                missing_files.remove(old_path)
                new_files.remove(new_path)
                
                renames_detected = True
                break

    if renames_detected:
        with open("hash_table.json", "w") as f:
            json.dump(stored_hashes, f, indent=4)
        print("--- Hash table updated with new filenames ---")

    for path, saved_hash in stored_hashes.items():
        if os.path.exists(path):
            current_hash = hash_file(path)
            if current_hash == saved_hash:
                print(f"{path}: VALID")
            else:
                print(f"{path}: INVALID (Content has changed.)")
        else:
            print(f"{path}: DELETED (File is missing.)")

    for path in new_files:
        if path not in stored_hashes:
            print(f"{path}: NEW FILE (Not in original hash table.)")

def main():
    while True:
        print("\n--- File Integrity Monitor ---")
        print("1. Generate New Hash Table")
        print("2. Verify Hashes")
        print("3. Reset (Clear Hash Table)")
        print("4. Exit")
        
        choice = input("Select an option (1-4): ")

        if choice == '1':
            generate_table()
        elif choice == '2':
            validate_hashes()
        elif choice == '3':
            if os.path.exists("hash_table.json"):
                os.remove("hash_table.json")
                print("\n--- Hash table cleared! ---")
            else:
                print("\n--- No hash table found to delete. ---")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
