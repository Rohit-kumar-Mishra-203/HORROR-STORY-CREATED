import os
import re
import pandas as pd
from tqdm import tqdm

# CONFIG
RAW_DIR       = "data/raw"
PROCESSED_DIR = "data/processed"
TRAIN_FILE    = "data/processed/train.txt"
VAL_FILE      = "data/processed/val.txt"
TRAIN_SPLIT   = 0.8   # 80% train, 20% validation

# ─────────────────────────────────────────
# STEP 1 — READ ALL STORIES FROM data/raw/
# ─────────────────────────────────────────
def load_stories(raw_dir):
    stories = []
    files = [f for f in os.listdir(raw_dir) if f.endswith(".txt")]

    if len(files) == 0:
        print("❌ No .txt files found in data/raw/ folder!")
        return stories

    print(f"📂 Found {len(files)} story files...\n")

    for filename in tqdm(files, desc="Reading stories"):
        filepath = os.path.join(raw_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                stories.append(content)

    print(f"✅ Loaded {len(stories)} stories\n")
    return stories


# ─────────────────────────────────────────
# STEP 2 — CLEAN EACH STORY
# ─────────────────────────────────────────
def clean_story(text):
    import unicodedata

    # Step 1 - Normalize unicode
    text = unicodedata.normalize("NFC", text)

    # Step 2 - Remove Chinese, Tibetan, Japanese, Korean and all non-Hindi scripts
    cleaned = []
    for char in text:
        cp = ord(char)
        # Allow only:
        # Hindi Devanagari        : 0x0900–0x097F
        # Devanagari Extended     : 0xA8E0–0xA8FF
        # Common punctuation      : spaces, newlines, ।?!,'-"
        # Basic ASCII digits      : 0–9
        if (
            0x0900 <= cp <= 0x097F or   # Devanagari (Hindi)
            0xA8E0 <= cp <= 0xA8FF or   # Devanagari Extended
            cp in (0x0020, 0x000A, 0x000D) or  # space, newline
            char in '।?!,\'-"\n ' or
            (0x0030 <= cp <= 0x0039)     # digits 0-9
        ):
            cleaned.append(char)

    text = "".join(cleaned)

    # Step 3 - Remove leftover HTML entities like &nbsp; &amp; etc
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)

    # Step 4 - Remove extra whitespace and blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()

    return text

## valid story
def is_valid_story(text):
    if len(text.strip()) < 200:
        return False, "too short"

    # Count Hindi characters
    hindi_chars = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    total_chars = len(text.replace(" ", "").replace("\n", ""))

    if total_chars == 0:
        return False, "empty"

    hindi_ratio = hindi_chars / total_chars

    if hindi_ratio < 0.7:   # at least 70% must be Hindi
        return False, f"not enough Hindi ({int(hindi_ratio*100)}%)"

    return True, "ok"


# ─────────────────────────────────────────
# STEP 3 — FORMAT WITH IndicBART TAGS
# ─────────────────────────────────────────
def format_story(text):
    # <2hi> = Hindi language tag for IndicBART
    # <s> = start token, </s> = end token
    return f"<s> <2hi> {text} </s>"


# ─────────────────────────────────────────
# STEP 4 — SPLIT INTO TRAIN & VALIDATION
# ─────────────────────────────────────────
def split_data(stories, train_split=0.8):
    split_idx = int(len(stories) * train_split)
    train = stories[:split_idx]
    val   = stories[split_idx:]
    print(f"📊 Train stories : {len(train)}")
    print(f"📊 Val stories   : {len(val)}\n")
    return train, val


# ─────────────────────────────────────────
# STEP 5 — SAVE TO PROCESSED FOLDER
# ─────────────────────────────────────────
def save_stories(stories, filepath):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for story in stories:
            f.write(story + "\n\n")
    print(f"✅ Saved → {filepath}")


# ─────────────────────────────────────────
# STEP 6 — SHOW SAMPLE AFTER PROCESSING
# ─────────────────────────────────────────
def show_sample(stories):
    print("\n" + "="*60)
    print("📖 SAMPLE PROCESSED STORY:")
    print("="*60)
    print(stories[0][:500])
    print("...(truncated)")
    print("="*60 + "\n")


# ─────────────────────────────────────────
# MAIN — RUN ALL STEPS
# ─────────────────────────────────────────
def main():
    print("\n🚀 Starting Data Preparation...\n")

    # Step 1 - Load
    stories = load_stories(RAW_DIR)
    if not stories:
        return

    
    # Step 2 - Clean
    print("🧹 Cleaning stories...")
    cleaned = []
    skipped = 0
    for story in tqdm(stories, desc="Cleaning"):
        cleaned_story = clean_story(story)
        valid, reason = is_valid_story(cleaned_story)
        if valid:
            cleaned.append(cleaned_story)
        else:
            skipped += 1
            print(f"   ⚠️  Skipped story — reason: {reason}")

    print(f"✅ {len(cleaned)} valid stories after cleaning")
    print(f"⚠️  {skipped} stories skipped\n")

    # Step 3 - Format with IndicBART tags
    print("🏷️  Adding IndicBART language tags...")
    formatted = [format_story(s) for s in cleaned]

    # Step 4 - Split
    print("✂️  Splitting into train/val...\n")
    train_stories, val_stories = split_data(formatted, TRAIN_SPLIT)

    # Step 5 - Save
    print("💾 Saving processed files...")
    save_stories(train_stories, TRAIN_FILE)
    save_stories(val_stories,   VAL_FILE)

    # Step 6 - Show sample
    show_sample(formatted)

    # Summary
    print("="*60)
    print("✅ DATA PREPARATION COMPLETE!")
    print(f"   Train file : {TRAIN_FILE}")
    print(f"   Val file   : {VAL_FILE}")
    print(f"   Total stories processed: {len(formatted)}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()