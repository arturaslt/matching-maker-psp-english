import struct, os, json, shutil

# --- Constants from MatchingMaker Engine (Ghidra Verified) ---
LOAD_BASE = 0x08804000
FILE_BASE = 0x000001B4
SUB_ENTRY_DATA_START = 0x01EFE800  
ALLOC_LIMIT_OFFSET = 0x01E8011C    
ZONE_C_LOAD_OFFSET = 0x234C        

def va2file(va): return va - LOAD_BASE + FILE_BASE

def patch_game():
    output_root = 'patched_game'
    sysdir = os.path.join(output_root, 'PSP_GAME', 'SYSDIR')
    usrdir = os.path.join(output_root, 'PSP_GAME', 'USRDIR')
    os.makedirs(sysdir, exist_ok=True)
    os.makedirs(usrdir, exist_ok=True)

    boot_in = 'BOOT.BIN' if os.path.exists('BOOT.BIN') else 'Test/BOOT.BIN'
    arc1_in = 'archive1.arc' if os.path.exists('archive1.arc') else 'Test/archive1.arc'
    
    if not os.path.exists(boot_in) or not os.path.exists(arc1_in):
        print(f"Error: Required files not found.")
        return

    with open(boot_in, 'rb') as f: boot = bytearray(f.read())
    with open(arc1_in, 'rb') as f: arc1 = bytearray(f.read())

    redirected_entries = []
    zone_b_text = bytearray()
    direct_count = 0
    zoned_count = 0

    json_paths = []
    patch_dir = 'patches'
    if os.path.exists(patch_dir):
        for f in os.listdir(patch_dir):
            if f.endswith('.json'):
                json_paths.append(os.path.join(patch_dir, f))
    
    standard_json = 'archive1.arc.json' if os.path.exists('archive1.arc.json') else 'Test/archive1.arc.json'
    if os.path.exists(standard_json):
        if not any(os.path.abspath(standard_json) == os.path.abspath(jp) for jp in json_paths):
            json_paths.append(standard_json)

    if not json_paths:
        print("Error: No translation JSON files found in 'patches'.")
        return

    for json_path in json_paths:
        current_base = SUB_ENTRY_DATA_START
            
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                trans_data = json.load(f)
            except Exception as e:
                print(f"Failed to load {json_path}: {e}")
                continue

        all_entries = []
        if isinstance(trans_data, list):
            all_entries = trans_data
        elif isinstance(trans_data, dict):
            tabs_source = trans_data.get("tabs") or trans_data.get("dialogs")
            if tabs_source:
                if isinstance(tabs_source, dict):
                    for t_name in tabs_source:
                        all_entries.extend(tabs_source[t_name])
                else:
                    all_entries = tabs_source
            elif "offset_start" in trans_data:
                all_entries = [trans_data]
            else:
                for k, v in trans_data.items():
                    if isinstance(v, list):
                        all_entries.extend(v)

        if not isinstance(all_entries, list) or not all_entries:
            continue

        for entry in all_entries:
            if isinstance(entry, list) and len(entry) >= 3:
                entry = {
                    "offset_start": str(entry[0]),
                    "offset_end": str(entry[1]),
                    "file": str(entry[2])
                }
            
            if not isinstance(entry, dict) or "offset_start" not in entry:
                continue

            translation = entry.get("translation")
            file_to_patch = entry.get("file")
            
            abs_start = int(entry["offset_start"], 16)
            buf_off = (abs_start - current_base) & 0xFFFF
            
            filename_lower = os.path.basename(json_path).lower()
            if 'redirect' in filename_lower:
                method = 'redirect'
            elif 'replace' in filename_lower:
                method = 'replace'
            elif 'update' in filename_lower:
                method = 'update'
            else:
                method = 'redirect' if entry.get("zone", 'redirect' in json_path) else 'update'

            if method == 'redirect':
                if not translation: continue
                pos = len(zone_b_text)
                encoded = translation.encode('utf-16-le') + b'\x00\x00\xff\xff'
                zone_b_text += encoded
                redirected_entries.append({"id": buf_off, "redirect_pos": pos})
                
                if "offset_end" in entry:
                    abs_end = int(entry["offset_end"], 16)
                    size = abs_end - abs_start + 1
                    arc1[abs_start:abs_start+size] = b'\x00' * size
                zoned_count += 1

            elif method == 'replace':
                encoded = None
                if file_to_patch:
                    possible_paths = [
                        os.path.join(os.path.dirname(json_path), file_to_patch),
                        os.path.join('patches', file_to_patch),
                        file_to_patch
                    ]
                    for p in possible_paths:
                        if os.path.exists(p):
                            with open(p, 'rb') as bin_f:
                                encoded = bin_f.read()
                            break
                    
                    if encoded is None:
                        continue
                elif translation:
                    encoded = translation.encode('utf-16-le')
                
                if encoded:
                    arc1[abs_start:abs_start+len(encoded)] = encoded
                    direct_count += 1

            else: # update
                if not translation: continue
                encoded = translation.encode('utf-16-le') + b'\x00\x00'
                if "offset_end" in entry:
                    abs_end = int(entry["offset_end"], 16)
                    max_size = abs_end - abs_start + 1
                    if len(encoded) > max_size:
                        pass
                
                arc1[abs_start:abs_start+len(encoded)] = encoded
                direct_count += 1

    zone_d_size = zoned_count * 4
    zone_b_start_abs = ZONE_C_LOAD_OFFSET + zone_d_size
    
    archive_e = bytearray()
    for e in redirected_entries:
        redirect = (zone_b_start_abs + e["redirect_pos"]) & 0xFFFF
        archive_e += struct.pack('<HH', redirect, e["id"])
    archive_e += zone_b_text

    with open(os.path.join(usrdir, 'archiveE.arc'), 'wb') as f:
        f.write(archive_e)

    tramp_pos = va2file(0x0889DC24)
    boot[tramp_pos:tramp_pos+8] = struct.pack('<2I', 0x0A249C04, 0x00000000)

    mips_logic = [
        0x27BDFFF8, 0xAFBF0004, 0xAFA50000, 0x3C080893, 0x8D082680, 0x11000011, 0x3C090892, 0x8D297000,
        0x15200003, 0x00000000, 0x0E249BD2, 0x00000000, 0x8FA50000, 0x3C080893, 0x8D082680, 0x2509234C,
        0x24030000 | (zoned_count & 0xFFFF), 
        0x952A0002, 0x11450008, 0x25290004, 0x2463FFFF, 0x1460FFFB, 0x00000000, 
        0x01051021, 0x8FBF0004, 0x03E00008, 0x27BD0008, 
        0x9522FFFC, 0x01021021, 0x8FBF0004, 0x03E00008, 0x27BD0008
    ]
    boot[va2file(0x08927010):va2file(0x08927010)+len(mips_logic)*4] = struct.pack(f'<{len(mips_logic)}I', *mips_logic)
    
    e_size = len(archive_e)
    overlay_fn = [
        0x27BDFFF0, 0xAFBF000C, 0x3C040892, 0x24846F20, 0x24050001, 0x240601FF, 0x0E23E3F1, 0x00000000,
        0xAFA20008, 0x0440000D, 0x3C080893, 0x8D052680, 0x24A5234C, 0x8FA40008, 
        0x24060000 | (e_size & 0xFFFF),
        0x0E23E3E1, 0x00000000, 0x8FA40008, 0x0E23E3E7, 0x00000000, 0x3C080892, 0x24090001, 0xAD097000,
        0x8FBF000C, 0x27BD0010, 0x03E00008, 0x00000000
    ]
    boot[va2file(0x08926F48):va2file(0x08926F48)+len(overlay_fn)*4] = struct.pack(f'<{len(overlay_fn)}I', *overlay_fn)
    boot[va2file(0x08926F20):va2file(0x08926F20)+36] = b'disc0:/PSP_GAME/USRDIR/archiveE.arc\x00'

    with open(os.path.join(sysdir, 'BOOT.BIN'), 'wb') as f: f.write(boot)

    new_limit = (0x234C + e_size + 63) & ~63
    struct.pack_into('<I', arc1, ALLOC_LIMIT_OFFSET, new_limit)
    with open(os.path.join(usrdir, 'archive1.arc'), 'wb') as f: f.write(arc1)

    print(f"\nSuccess! Used exact original logic. archiveE.arc size: {e_size} bytes.")

if __name__ == "__main__":
    patch_game()
