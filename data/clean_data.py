import os
import re
import unicodedata
from tqdm import tqdm

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
RAW_DIR       = "data/raw"
PROCESSED_DIR = "data/processed"
TRAIN_FILE    = "data/processed/train.txt"
VAL_FILE      = "data/processed/val.txt"
TRAIN_SPLIT   = 0.8
MIN_STORY_LEN = 200   # minimum characters


# ─────────────────────────────────────────
# STEP 1 — SCAN FILES FOR BAD CHARACTERS
# ─────────────────────────────────────────
def scan_files(raw_dir):
    print("\n" + "="*60)
    print("🔍 STEP 1 — SCANNING FILES FOR BAD CHARACTERS")
    print("="*60 + "\n")

    files = [f for f in os.listdir(raw_dir) if f.endswith(".txt")]

    if not files:
        print("❌ No .txt files found in data/raw/")
        return []

    dirty_files = []

    for filename in files:
        filepath = os.path.join(raw_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        bad_chars = []
        for char in content:
            cp = ord(char)
            if not (
                0x0900 <= cp <= 0x097F or    # Hindi Devanagari
                0x0020 <= cp <= 0x007E or    # Basic ASCII
                cp in (0x000A, 0x000D)       # newlines
            ):
                bad_chars.append((char, hex(cp)))

        if bad_chars:
            unique_bad = list(set(bad_chars))[:5]
            print(f"❌ {filename} → bad chars found: {unique_bad}")
            dirty_files.append(filename)
        else:
            print(f"✅ {filename} → clean")

    print(f"\n📊 Total files  : {len(files)}")
    print(f"📊 Dirty files  : {len(dirty_files)}")
    print(f"📊 Clean files  : {len(files) - len(dirty_files)}\n")

    return files


# ─────────────────────────────────────────
# STEP 2 — DEEP CLEAN EACH STORY FILE
# ─────────────────────────────────────────
def deep_clean_text(text):
    # 1. Normalize unicode (fixes invisible broken characters)
    text = unicodedata.normalize("NFC", text)

    # 2. Remove ALL non-Hindi characters strictly
    cleaned = []
    for char in text:
        cp = ord(char)
        if (
            0x0900 <= cp <= 0x097F or        # Devanagari Hindi
            0xA8E0 <= cp <= 0xA8FF or        # Devanagari Extended
            char in ' \n\r।?!,\'-\"' or      # Hindi punctuation
            (0x0030 <= cp <= 0x0039)          # digits 0-9
        ):
            cleaned.append(char)

    text = "".join(cleaned)

    # 3. Remove HTML entities (&nbsp; &amp; etc)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)

    # 4. Remove leftover URLs or email patterns
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)

    # 5. Fix multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    # 6. Fix multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 7. Strip
    text = text.strip()

    return text


# ─────────────────────────────────────────
# STEP 3 — VALIDATE STORY QUALITY
# ─────────────────────────────────────────
def is_valid_story(text):
    # Check minimum length
    if len(text.strip()) < MIN_STORY_LEN:
        return False, f"too short ({len(text.strip())} chars, min {MIN_STORY_LEN})"

    # Count Hindi characters
    hindi_chars = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    total_chars = len(text.replace(" ", "").replace("\n", ""))

    if total_chars == 0:
        return False, "empty after cleaning"

    hindi_ratio = hindi_chars / total_chars

    # At least 70% must be Hindi
    if hindi_ratio < 0.70:
        return False, f"not enough Hindi ({int(hindi_ratio*100)}% Hindi, need 70%+)"

    return True, "ok"


# ─────────────────────────────────────────
# STEP 4 — CLEAN AND SAVE ALL RAW FILES
# ─────────────────────────────────────────
def clean_all_files(raw_dir, files):
    print("="*60)
    print("🧹 STEP 2 — DEEP CLEANING ALL STORY FILES")
    print("="*60 + "\n")

    cleaned_stories = []
    skipped = 0

    for filename in tqdm(files, desc="Cleaning files"):
        filepath = os.path.join(raw_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Deep clean
        cleaned = deep_clean_text(content)

        # Validate
        valid, reason = is_valid_story(cleaned)

        if valid:
            # Save cleaned version back to raw file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(cleaned)
            cleaned_stories.append(cleaned)
            print(f"  ✅ {filename} → cleaned & saved ({len(cleaned.split())} words)")
        else:
            print(f"  ⚠️  {filename} → skipped ({reason})")
            skipped += 1

    print(f"\n📊 Successfully cleaned : {len(cleaned_stories)} stories")
    print(f"📊 Skipped              : {skipped} stories\n")

    return cleaned_stories


# ─────────────────────────────────────────
# STEP 5 — VERIFY FILES ARE CLEAN
# ─────────────────────────────────────────
def verify_clean_files(raw_dir, files):
    print("="*60)
    print("✅ STEP 3 — VERIFYING ALL FILES ARE CLEAN")
    print("="*60 + "\n")

    all_clean = True

    for filename in files:
        filepath = os.path.join(raw_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        bad = [
            char for char in content
            if not (
                0x0900 <= ord(char) <= 0x097F or
                0xA8E0 <= ord(char) <= 0xA8FF or
                char in ' \n\r।?!,\'-\"' or
                0x0030 <= ord(char) <= 0x0039
            )
        ]

        if bad:
            unique_bad = list(set(bad))[:3]
            print(f"❌ Still dirty: {filename} → {unique_bad}")
            all_clean = False
        else:
            print(f"✅ Verified clean: {filename}")

    if all_clean:
        print("\n🎉 ALL FILES ARE PERFECTLY CLEAN!\n")
    else:
        print("\n⚠️  Some files still have issues. Check manually.\n")

    return all_clean


# ─────────────────────────────────────────
# STEP 6 — FORMAT WITH IndicBART TAGS
# ─────────────────────────────────────────
def format_story(text):
    return f"<s> <2hi> {text} </s>"


# ─────────────────────────────────────────
# STEP 7 — SPLIT AND SAVE PROCESSED DATA
# ─────────────────────────────────────────
def split_and_save(stories):
    print("="*60)
    print("💾 STEP 4 — SPLITTING AND SAVING PROCESSED DATA")
    print("="*60 + "\n")

    # Format stories with IndicBART tags
    formatted = [format_story(s) for s in stories]

    # Shuffle for better training
    import random
    random.seed(42)
    random.shuffle(formatted)

    # Split 80/20
    split_idx     = int(len(formatted) * TRAIN_SPLIT)
    train_stories = formatted[:split_idx]
    val_stories   = formatted[split_idx:]

    print(f"📊 Total stories  : {len(formatted)}")
    print(f"📊 Train stories  : {len(train_stories)}")
    print(f"📊 Val stories    : {len(val_stories)}\n")

    # Save
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    with open(TRAIN_FILE, "w", encoding="utf-8") as f:
        for story in train_stories:
            f.write(story + "\n\n")

    with open(VAL_FILE, "w", encoding="utf-8") as f:
        for story in val_stories:
            f.write(story + "\n\n")

    print(f"✅ Train data saved → {TRAIN_FILE}")
    print(f"✅ Val data saved   → {VAL_FILE}\n")


# ─────────────────────────────────────────
# STEP 8 — SHOW STATS AND SAMPLE
# ─────────────────────────────────────────
def show_stats(stories):
    print("="*60)
    print("📊 DATASET STATISTICS")
    print("="*60)

    word_counts  = [len(s.split()) for s in stories]
    total_words  = sum(word_counts)
    avg_words    = total_words // len(stories)
    min_words    = min(word_counts)
    max_words    = max(word_counts)

    print(f"  Total stories    : {len(stories)}")
    print(f"  Total words      : {total_words:,}")
    print(f"  Average words    : {avg_words}")
    print(f"  Shortest story   : {min_words} words")
    print(f"  Longest story    : {max_words} words")
    print()

    print("📖 SAMPLE CLEANED STORY (first 300 chars):")
    print("-"*60)
    print(stories[0][:300])
    print("...(truncated)")
    print("="*60 + "\n")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n🚀 FULL DATA CLEANING PIPELINE STARTED")

    # Step 1 - Scan
    files = scan_files(RAW_DIR)
    if not files:
        return

    # Step 2 - Clean all files
    cleaned_stories = clean_all_files(RAW_DIR, files)
    if not cleaned_stories:
        print("❌ No valid stories after cleaning!")
        print("   Add more Hindi stories to data/raw/ folder")
        return

    # Step 3 - Verify
    verify_clean_files(RAW_DIR, files)

    # Step 4 - Split and save
    split_and_save(cleaned_stories)

    # Step 5 - Show stats
    show_stats(cleaned_stories)

    print("="*60)
    print("🎉 DATA CLEANING COMPLETE!")
    print("   Next step: python backend/model/train.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()