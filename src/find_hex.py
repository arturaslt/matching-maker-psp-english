import os
import sys

def find_hex_globally(hex_pattern):
    hex_pattern = "".join(hex_pattern.split()).lower()
    try:
        search_bytes = bytes.fromhex(hex_pattern)
    except ValueError:
        print("Error: Invalid hex string provided. Ensure it only contains 0-9 and A-F.")
        return

    patches_dir = 'patches'
    if not os.path.exists(patches_dir):
        print(f"Error: Folder '{patches_dir}' not found.")
        return

    print(f"Searching for hex: {hex_pattern}")
    print("-" * 50)

    found_any = False
    for root, dirs, files in os.walk(patches_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    index = content.find(search_bytes)
                    
                    if index != -1:
                        print(f"MATCH FOUND!")
                        print(f"  File:   {file_path}")
                        print(f"  Offset: 0x{index:X}")
                        found_any = True
            except Exception as e:
                continue

    if not found_any:
        print("No matches found in any file within the 'patches' directory.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/find_hex.py <hex_string>")
    else:
        # Join all arguments in case the user used spaces
        pattern = "".join(sys.argv[1:])
        find_hex_globally(pattern)
