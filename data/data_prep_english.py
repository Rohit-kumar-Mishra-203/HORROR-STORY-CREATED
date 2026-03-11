import os
import re
from tqdm import tqdm

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
RAW_DIR       = "data/raw_english"
PROCESSED_DIR = "data/processed_english"
TRAIN_FILE    = "data/processed_english/train.txt"
VAL_FILE      = "data/processed_english/val.txt"
TRAIN_SPLIT   = 0.8
MIN_WORDS     = 150


# ─────────────────────────────────────────
# CLEAN ENGLISH TEXT
# ─────────────────────────────────────────
def clean_english(text):
    # Remove non-ASCII characters
    text = text.encode("ascii", errors="ignore").decode("ascii")

    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)

    # Remove URLs
    text = re.sub(r'http\S+', '', text)

    # Remove extra spaces and newlines
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# ─────────────────────────────────────────
# VALIDATE STORY
# ─────────────────────────────────────────
def is_valid(text):
    words = len(text.split())
    if words < MIN_WORDS:
        return False, f"too short ({words} words)"

    # Check mostly English letters
    english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total_chars   = sum(1 for c in text if c.isalpha())
    if total_chars == 0:
        return False, "empty"

    ratio = english_chars / total_chars
    if ratio < 0.8:
        return False, f"not enough English ({int(ratio*100)}%)"

    return True, "ok"


# ─────────────────────────────────────────
# FORMAT FOR GPT-2
# ─────────────────────────────────────────
def format_story(text):
    return f"<|startoftext|> {text} <|endoftext|>"


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n🚀 English Data Preparation Started\n")

    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]
    if not files:
        print("❌ No .txt files in data/raw_english/")
        return

    print(f"📂 Found {len(files)} files\n")

    # Load and clean
    cleaned = []
    skipped = 0

    for filename in tqdm(files, desc="Cleaning"):
        filepath = os.path.join(RAW_DIR, filename)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        cleaned_text = clean_english(content)
        valid, reason = is_valid(cleaned_text)

        if valid:
            cleaned.append(cleaned_text)
            print(f"  ✅ {filename}: {len(cleaned_text.split())} words")
        else:
            print(f"  ⚠️  {filename}: skipped ({reason})")
            skipped += 1

    print(f"\n✅ Valid stories  : {len(cleaned)}")
    print(f"⚠️  Skipped        : {skipped}\n")

    if not cleaned:
        print("❌ No valid stories found!")
        return

    # Format
    formatted = [format_story(s) for s in cleaned]

    # Shuffle
    import random
    random.seed(42)
    random.shuffle(formatted)

    # Split
    split_idx     = int(len(formatted) * TRAIN_SPLIT)
    train_stories = formatted[:split_idx]
    val_stories   = formatted[split_idx:]

    print(f"📊 Train : {len(train_stories)} stories")
    print(f"📊 Val   : {len(val_stories)} stories\n")

    # Save
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    with open(TRAIN_FILE, "w", encoding="utf-8") as f:
        for story in train_stories:
            f.write(story + "\n\n")

    with open(VAL_FILE, "w", encoding="utf-8") as f:
        for story in val_stories:
            f.write(story + "\n\n")

    print(f"✅ Saved → {TRAIN_FILE}")
    print(f"✅ Saved → {VAL_FILE}")
    print("\n🎉 English Data Preparation Complete!")
    print("   Next: python backend/model/train_english.py\n")


if __name__ == "__main__":
    main()