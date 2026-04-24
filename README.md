# Matching Maker Patcher

A tool to apply translation patches and reduce the ISO size for Matching Maker games on the PSP.

> [!IMPORTANT]
> **Status: Work in Progress**  
> This translation is currently incomplete. Many parts of the game are still in Japanese, and more work is needed to fully translate the experience.

> [!WARNING]
> **Stability Notice**  
> As this is an experimental patch, stability is not guaranteed. Crashes may occur during gameplay. It is highly recommended to keep multiple save files and backup your original ISO.

## ⚖️ Disclaimer
This is a non-commercial fan translation. This project is not affiliated with or endorsed by the original game developers or publishers. Please support the official release by owning a copy of the game.

## Prerequisites
* **UMDGen:** Required for modifying the PSP ISO.
* **patcher.exe / Python 3.x:** To run the patching script.
* **Original Game ISO:** The Japanese version of the game.

---

## Installation & Usage Guide

### Step 1: Initial ISO Cleanup & Extraction
1. Open **UMDGen** and load your original game ISO.
2. **Size Reduction:** Navigate to `PSP_GAME/SYSDIR`. Right-click the **UPDATE** folder and select **Delete**.
3. **Extraction:** 
   * Navigate to `PSP_GAME/USRDIR` and extract `archive1.arc` to the same project folder.

### Step 2: Running the Patcher
You have two ways to run the patcher:

**Option A: Using the Executable (Fastest)**
1. Ensure your project folder contains `patcher.exe`, `BOOT.BIN`, `archive1.arc`, and the `patches/` folder.
2. Run **`patcher.exe`**.

**Option B: Using Python (Recommended for Transparency)**
1. Install [Python 3.x](https://www.python.org/downloads/).
2. Open a terminal or command prompt in your project folder.
3. Run the script directly:
   ```bash
   python src/patcher.py
   ```
4. Once finished, a new folder named `patched_game` will be created.

### Step 3: Merging Patched Files
1. Open the `patched_game` folder. You will see a `PSP_GAME` folder inside.
2. In **UMDGen**, make sure you are in the **root** of the ISO (where you see `PSP_GAME` and `UMD_DATA.BIN`).
3. Drag and drop the `PSP_GAME` folder from `patched_game` directly into the UMDGen window. 
4. When prompted to overwrite existing files, select **Yes to All**.

### Step 4: Relinking the Executable (Required)
To ensure the game uses your patched code, you must "relink" the encrypted `EBOOT.BIN` to your new `BOOT.BIN`:
1. In UMDGen, navigate to **`PSP_GAME/SYSDIR`**.
2. Right-click **`BOOT.BIN`** and select **File Relinker** → **Use Selected File as Source**.
3. Right-click **`EBOOT.BIN`** and select **File Relinker** → **Relink to Source**.
   * *Note: Both files should now show the same "LBA" or size in the list.*

### Step 5: Finalizing
1. Click **Save** in UMDGen and choose **Uncompressed (.iso)**.
2. Transfer the new ISO to your PSP or emulator.

---
