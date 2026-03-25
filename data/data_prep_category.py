import os
import sys
import random

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
HINDI_RAW_DIR        = "data/raw"
ENGLISH_RAW_DIR      = "data/raw_english"
HINDI_PROCESSED_DIR  = "data/processed"
ENGLISH_PROCESSED_DIR= "data/processed_english"

CATEGORIES = [
    "witch", "ghost", "haunted_house", "graveyard",
    "demon", "vampire", "monster", "cursed_object",
    "possessed", "general_horror"
]

# Category tokens for IndicBART
HINDI_CATEGORY_TOKENS = {
    "witch"         : "चुड़ैल डायन जादू टोना",
    "ghost"         : "भूत प्रेत आत्मा भूतिया",
    "haunted_house" : "हवेली भूतिया घर वीरान",
    "graveyard"     : "कब्रिस्तान कब्र मुर्दा शमशान",
    "demon"         : "राक्षस शैतान दानव असुर",
    "vampire"       : "पिशाच खून रक्त अमर",
    "monster"       : "राक्षस जीव भयानक दानव",
    "cursed_object" : "शापित श्राप पुरानी चीज़",
    "possessed"     : "भूत चढ़ना आवेश शरीर",
    "general_horror": "डरावना भूत रात अंधेरा खौफ",
}

ENGLISH_CATEGORY_TOKENS = {
    "witch"         : "witch spell curse magic",
    "ghost"         : "ghost spirit haunted supernatural",
    "haunted_house" : "haunted house mansion abandoned",
    "graveyard"     : "graveyard cemetery grave tombstone",
    "demon"         : "demon devil evil dark entity",
    "vampire"       : "vampire blood fangs immortal",
    "monster"       : "monster creature beast lurking",
    "cursed_object" : "cursed object ancient artifact",
    "possessed"     : "possessed body evil inside",
    "general_horror": "horror scary dark terrifying",
}

os.makedirs(HINDI_PROCESSED_DIR,   exist_ok=True)
os.makedirs(ENGLISH_PROCESSED_DIR, exist_ok=True)


# ─────────────────────────────────────────
# PREPARE HINDI TRAINING DATA
# ─────────────────────────────────────────
def prepare_hindi_data():
    print("\n🇮🇳 Preparing Hindi category training data...")

    all_train = []
    all_val   = []

    for category in CATEGORIES:
        cat_dir = os.path.join(HINDI_RAW_DIR, category)

        if not os.path.exists(cat_dir):
            print(f"  ⚠️  Missing: {cat_dir}")
            continue

        files = [
            f for f in os.listdir(cat_dir)
            if f.endswith('.txt')
        ]

        if not files:
            print(f"  ⚠️  No files in: {cat_dir}")
            continue

        # Category keywords for training
        cat_tokens = HINDI_CATEGORY_TOKENS.get(category, "")
        cat_stories= []

        for filename in files:
            filepath = os.path.join(cat_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                story = f.read().strip()

            if not story:
                continue

            # Format: category prefix + story
            # This teaches model to generate category-specific stories
            formatted = (
                f"<s> <2hi> "
                f"यह एक {cat_tokens} की कहानी है। "
                f"{story} </s>"
            )
            cat_stories.append(formatted)

        # Split 80/20 train/val
        random.shuffle(cat_stories)
        split     = max(1, int(len(cat_stories) * 0.8))
        train     = cat_stories[:split]
        val       = cat_stories[split:] if len(cat_stories) > 1 else cat_stories[:1]

        all_train.extend(train)
        all_val.extend(val)

        print(f"  ✅ {category:20s} → {len(train)} train  {len(val)} val")

    # Save combined train/val
    train_file = os.path.join(HINDI_PROCESSED_DIR, "train.txt")
    val_file   = os.path.join(HINDI_PROCESSED_DIR, "val.txt")

    random.shuffle(all_train)
    random.shuffle(all_val)

    with open(train_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_train))

    with open(val_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_val))

    print(f"\n  📁 Saved: {train_file} ({len(all_train)} stories)")
    print(f"  📁 Saved: {val_file} ({len(all_val)} stories)")


# ─────────────────────────────────────────
# PREPARE ENGLISH TRAINING DATA
# ─────────────────────────────────────────
def prepare_english_data():
    print("\n🇬🇧 Preparing English category training data...")

    all_train = []
    all_val   = []

    for category in CATEGORIES:
        cat_dir = os.path.join(ENGLISH_RAW_DIR, category)

        if not os.path.exists(cat_dir):
            print(f"  ⚠️  Missing: {cat_dir}")
            continue

        files = [
            f for f in os.listdir(cat_dir)
            if f.endswith('.txt')
        ]

        if not files:
            print(f"  ⚠️  No files in: {cat_dir}")
            continue

        cat_tokens = ENGLISH_CATEGORY_TOKENS.get(category, "")
        cat_stories= []

        for filename in files:
            filepath = os.path.join(cat_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                story = f.read().strip()

            if not story:
                continue

            # Format with category prefix
            formatted = (
                f"This is a horror story about {cat_tokens}. "
                f"{story}"
            )
            cat_stories.append(formatted)

        random.shuffle(cat_stories)
        split  = max(1, int(len(cat_stories) * 0.8))
        train  = cat_stories[:split]
        val    = cat_stories[split:] if len(cat_stories) > 1 else cat_stories[:1]

        all_train.extend(train)
        all_val.extend(val)

        print(f"  ✅ {category:20s} → {len(train)} train  {len(val)} val")

    train_file = os.path.join(ENGLISH_PROCESSED_DIR, "train.txt")
    val_file   = os.path.join(ENGLISH_PROCESSED_DIR, "val.txt")

    random.shuffle(all_train)
    random.shuffle(all_val)

    with open(train_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_train))

    with open(val_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_val))

    print(f"\n  📁 Saved: {train_file} ({len(all_train)} stories)")
    print(f"  📁 Saved: {val_file} ({len(all_val)} stories)")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n" + "="*60)
    print("📚 CATEGORY-WISE DATA PREPARATION")
    print("="*60)

    prepare_hindi_data()
    prepare_english_data()

    print("\n" + "="*60)
    print("✅ DONE! Now run training:")
    print("   python backend/model/train.py")
    print("   python backend/model/train_english.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()