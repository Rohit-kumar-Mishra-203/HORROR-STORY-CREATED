import os
import re
import unicodedata
import random
from tqdm import tqdm
from datetime import datetime

# CONFIG
HINDI_RAW_DIR         = "data/raw"
TRAIN_FILE            = "data/processed/train.txt"
VAL_FILE              = "data/processed/val.txt"
ENGLISH_RAW_DIR       = "data/raw_english"
TRAIN_FILE            = "data/processed_english/train.txt"
VAL_FILE              = "data/processed_english/val.txt"
HINDI_PROCESSED_DIR   = "data/processed"
ENGLISH_PROCESSED_DIR = "data/processed_english"
REPORT_FILE           = "data/cleaning_report.txt"

CATEGORIES = [
    "witch", "ghost", "haunted_house", "graveyard",
    "demon", "vampire", "monster", "cursed_object",
    "possessed", "general_horror"
]

# Hindi settings
HINDI_MIN_CHARS       = 80
HINDI_MAX_CHARS       =10500
HINDI_MIN_RATIO       = 0.70

# English settings
ENGLISH_MIN_WORDS     = 80
ENGLISH_MAX_WORDS     = 10500
ENGLISH_MIN_RATIO     = 0.70

TRAIN_SPLIT           = 0.8

os.makedirs(HINDI_PROCESSED_DIR,   exist_ok=True)
os.makedirs(ENGLISH_PROCESSED_DIR, exist_ok=True)



# HINDI CLEANERS


def clean_hindi_text(text):
    # Normalize unicode
    text = unicodedata.normalize("NFC", text)

    # Keep only Devanagari + basic punctuation
    cleaned = []
    for char in text:
        cp = ord(char)
        if (
            0x0900 <= cp <= 0x097F or
            0xA8E0 <= cp <= 0xA8FF or
            char in ' \n\r।?!,\'-\"' or
            0x0030 <= cp <= 0x0039
        ):
            cleaned.append(char)

    text = "".join(cleaned)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'http\S+',     '',  text)
    text = re.sub(r'\S+@\S+',     '',  text)
    text = re.sub(r' {2,}',       ' ', text)
    text = re.sub(r'\n{3,}',   '\n\n', text)
    return text.strip()


def get_hindi_ratio(text):
    hindi = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    total = len(text.replace(" ", "").replace("\n", ""))
    return hindi / total if total > 0 else 0


def validate_hindi(text):
    if len(text.strip()) < HINDI_MIN_CHARS:
        return False, f"too short ({len(text.strip())} chars)"
    ratio = get_hindi_ratio(text)
    if ratio < HINDI_MIN_RATIO:
        return False, f"low Hindi ratio ({int(ratio*100)}%)"
    return True, f"{len(text.split())}w {int(ratio*100)}% Hindi"



# ENGLISH CLEANERS


def clean_english_text(text):
    # Remove HTML
    text = re.sub(r'<[^>]+>',     ' ', text)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;',      ' ', text)

    # Remove URLs
    text = re.sub(r'http[s]?://\S+', ' ', text)
    text = re.sub(r'www\.\S+',        ' ', text)
    text = re.sub(r'\S+@\S+\.\S+',    ' ', text)

    # Remove numbers and special chars
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[#@$%^&*+=\[\]{}|\\/<>~`_]', ' ', text)

    # Keep only English letters + punctuation
    allowed = []
    for ch in text:
        cp = ord(ch)
        if (
            0x0041 <= cp <= 0x005A or
            0x0061 <= cp <= 0x007A or
            ch in ' \n\t.,!?;:\'"()-'
        ):
            allowed.append(ch)
        else:
            allowed.append(' ')
    text = ''.join(allowed)

    # Remove short lines
    lines       = text.split('\n')
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        words    = re.findall(r'[a-zA-Z]+', stripped)
        if len(words) >= 3:
            clean_lines.append(stripped)
        elif not stripped:
            clean_lines.append('')
    text = '\n'.join(clean_lines)

    text = re.sub(r'[ \t]+',  ' ',   text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def get_english_ratio(text):
    english = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total   = sum(1 for c in text if c.isalpha())
    return english / total if total > 0 else 0


def count_words(text):
    return len(text.split())


def validate_english(text):
    words = count_words(text)
    ratio = get_english_ratio(text)
    if words < ENGLISH_MIN_WORDS:
        return False, f"too short ({words} words)"
    if ratio < ENGLISH_MIN_RATIO:
        return False, f"low English ratio ({int(ratio*100)}%)"
    return True, f"{words}w {int(ratio*100)}% English"


def split_long_english(text, filename):
    if count_words(text) <= ENGLISH_MAX_WORDS:
        return [(text, filename)]

    paragraphs = text.split('\n\n')
    chunks     = []
    current    = []
    cur_words  = 0
    chunk_num  = 1

    for para in paragraphs:
        pw = count_words(para)
        if cur_words + pw > ENGLISH_MAX_WORDS and current:
            base = os.path.splitext(filename)[0]
            chunks.append(('\n\n'.join(current), f"{base}_part{chunk_num}.txt"))
            chunk_num += 1
            current    = [para]
            cur_words  = pw
        else:
            current.append(para)
            cur_words += pw

    if current:
        base = os.path.splitext(filename)[0]
        chunks.append(('\n\n'.join(current), f"{base}_part{chunk_num}.txt"))

    return chunks



# PROCESS HINDI — CATEGORY WISE


def process_hindi():
    print("\n" + "="*60)
    print("IN CLEANING HINDI DATA")
    print("="*60)

    report  = []
    passed  = 0
    failed  = 0

    # Process category folders
    for category in CATEGORIES:
        cat_dir = os.path.join(HINDI_RAW_DIR, category)

        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith('.txt')]
        if not files:
            continue

        cat_passed = 0
        print(f"\n  📂 {category} ({len(files)} files)")

        for filename in sorted(files):
            filepath = os.path.join(cat_dir, filename)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()

            clean = clean_hindi_text(raw)
            valid, reason = validate_hindi(clean)

            if valid:
                # Save cleaned back to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(clean)
                passed    += 1
                cat_passed += 1
                report.append(f"HINDI OK: {category}/{filename} — {reason}")
                print(f"    ✅ {filename:30s} → {reason}")
            else:
                failed += 1
                report.append(f"HINDI FAIL: {category}/{filename} — {reason}")
                print(f"    ❌ {filename:30s} → {reason}")

    # Also process flat files in root raw dir
    flat_files = [f for f in os.listdir(HINDI_RAW_DIR) if f.endswith('.txt')]
    if flat_files:
        print(f"\n  📂 root ({len(flat_files)} files)")
        for filename in sorted(flat_files):
            filepath = os.path.join(HINDI_RAW_DIR, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
            clean = clean_hindi_text(raw)
            valid, reason = validate_hindi(clean)
            if valid:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(clean)
                passed += 1
                report.append(f"HINDI OK: {filename} — {reason}")
                print(f"    ✅ {filename:30s} → {reason}")
            else:
                failed += 1
                report.append(f"HINDI FAIL: {filename} — {reason}")
                print(f"    ❌ {filename:30s} → {reason}")

    print(f"\n  ✅ Passed : {passed}  ❌ Failed : {failed}")
    return report, passed, failed



# PROCESS ENGLISH — CATEGORY WISE


def process_english():
    print("\n" + "="*60)
    print("🇬🇧 CLEANING ENGLISH DATA")
    print("="*60)

    report  = []
    passed  = 0
    failed  = 0
    skipped = 0

    for category in CATEGORIES:
        cat_dir = os.path.join(ENGLISH_RAW_DIR, category)

        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith('.txt')]
        if not files:
            continue

        print(f"\n  📂 {category} ({len(files)} files)")

        for filename in sorted(files):
            filepath = os.path.join(cat_dir, filename)

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    raw = f.read()
            except Exception as e:
                failed += 1
                report.append(f"ENGLISH FAIL: {category}/{filename} — {e}")
                continue

            if not raw.strip():
                failed += 1
                report.append(f"ENGLISH FAIL: {category}/{filename} — empty")
                continue

            clean = clean_english_text(raw)
            valid, reason = validate_english(clean)

            if not valid:
                failed += 1
                report.append(f"ENGLISH FAIL: {category}/{filename} — {reason}")
                print(f"    ❌ {filename:30s} → {reason}")
                continue

            # Split if too long
            chunks = split_long_english(clean, filename)

            for chunk_text, chunk_name in chunks:
                if count_words(chunk_text) < ENGLISH_MIN_WORDS:
                    skipped += 1
                    continue

                # Save cleaned back
                out_path = os.path.join(cat_dir, chunk_name)
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(chunk_text)

            passed += 1
            report.append(f"ENGLISH OK: {category}/{filename} — {reason}")
            print(f"    ✅ {filename:30s} → {reason}")

    # Also process flat files
    flat_files = [f for f in os.listdir(ENGLISH_RAW_DIR) if f.endswith('.txt')]
    if flat_files:
        print(f"\n  📂 root ({len(flat_files)} files)")
        for filename in sorted(flat_files):
            filepath = os.path.join(ENGLISH_RAW_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    raw = f.read()
            except:
                continue
            clean = clean_english_text(raw)
            valid, reason = validate_english(clean)
            if valid:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(clean)
                passed += 1
                report.append(f"ENGLISH OK: {filename} — {reason}")
                print(f"    ✅ {filename:30s} → {reason}")
            else:
                failed += 1
                report.append(f"ENGLISH FAIL: {filename} — {reason}")
                print(f"    ❌ {filename:30s} → {reason}")

    print(f"\n  ✅ Passed : {passed}  ❌ Failed : {failed}  ⚠️  Skipped : {skipped}")
    return report, passed, failed, skipped



# PREPARE PROCESSED FILES FOR TRAINING


def prepare_hindi_processed():
    print("\n" + "="*60)
    print("🇮🇳 PREPARING HINDI TRAINING FILES")
    print("="*60)

    all_stories = []

    HINDI_CATEGORY_TOKENS = {
        "witch"         : "चुड़ैल डायन जादू टोना मंत्र",
        "ghost"         : "भूत प्रेत आत्मा भूतिया डरावना",
        "haunted_house" : "हवेली भूतिया घर वीरान खंडहर",
        "graveyard"     : "कब्रिस्तान कब्र मुर्दा शमशान",
        "demon"         : "राक्षस शैतान दानव असुर दैत्य",
        "vampire"       : "पिशाच खून रक्त अमर रात",
        "monster"       : "राक्षस जीव भयानक दानव खौफनाक",
        "cursed_object" : "शापित श्राप पुरानी चीज़ अभिशाप",
        "possessed"     : "भूत चढ़ना आवेश शरीर आत्मा",
        "general_horror": "डरावना भूत रात अंधेरा खौफ",
    }

    for category in CATEGORIES:
        cat_dir   = os.path.join(HINDI_RAW_DIR, category)
        cat_token = HINDI_CATEGORY_TOKENS.get(category, "डरावना")

        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith('.txt')]

        for filename in files:
            filepath = os.path.join(cat_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                story = f.read().strip()
            if len(story) < HINDI_MIN_CHARS:
                continue
            formatted = (
                f"<s> <2hi> "
                f"यह एक {cat_token} की कहानी है। "
                f"{story} </s>"
            )
            all_stories.append(formatted)

    # Also add flat files
    flat_files = [f for f in os.listdir(HINDI_RAW_DIR) if f.endswith('.txt')]
    for filename in flat_files:
        filepath = os.path.join(HINDI_RAW_DIR, filename)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            story = f.read().strip()
        if len(story) >= HINDI_MIN_CHARS:
            all_stories.append(f"<s> <2hi> {story} </s>")

    if not all_stories:
        print("  ❌ No Hindi stories found!")
        return

    random.shuffle(all_stories)
    split      = max(1, int(len(all_stories) * TRAIN_SPLIT))
    train      = all_stories[:split]
    val        = all_stories[split:] if len(all_stories) > 1 else all_stories[:1]

    train_file = os.path.join(HINDI_PROCESSED_DIR, "train.txt")
    val_file   = os.path.join(HINDI_PROCESSED_DIR, "val.txt")

    with open(train_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(train))

    with open(val_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(val))

    print(f"  ✅ Train : {len(train)} stories → {train_file}")
    print(f"  ✅ Val   : {len(val)} stories   → {val_file}")


def prepare_english_processed():
    print("\n" + "="*60)
    print("🇬🇧 PREPARING ENGLISH TRAINING FILES")
    print("="*60)

    all_stories = []

    ENGLISH_CATEGORY_TOKENS = {
        "witch"         : "witch spell curse magic coven",
        "ghost"         : "ghost spirit haunted supernatural",
        "haunted_house" : "haunted house mansion abandoned",
        "graveyard"     : "graveyard cemetery grave tombstone",
        "demon"         : "demon devil evil dark entity",
        "vampire"       : "vampire blood fangs immortal",
        "monster"       : "monster creature beast lurking",
        "cursed_object" : "cursed object ancient artifact",
        "possessed"     : "possessed body taken over evil",
        "general_horror": "horror scary dark terrifying evil",
    }

    for category in CATEGORIES:
        cat_dir    = os.path.join(ENGLISH_RAW_DIR, category)
        cat_tokens = ENGLISH_CATEGORY_TOKENS.get(category, "horror scary")

        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith('.txt')]

        for filename in files:
            filepath = os.path.join(cat_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                story = f.read().strip()
            if count_words(story) < ENGLISH_MIN_WORDS:
                continue
            formatted = (
                f"This is a horror story about {cat_tokens}. "
                f"{story}"
            )
            all_stories.append(formatted)

    # Also add flat files
    flat_files = [f for f in os.listdir(ENGLISH_RAW_DIR) if f.endswith('.txt')]
    for filename in flat_files:
        filepath = os.path.join(ENGLISH_RAW_DIR, filename)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            story = f.read().strip()
        if count_words(story) >= ENGLISH_MIN_WORDS:
            all_stories.append(story)

    if not all_stories:
        print("  ❌ No English stories found!")
        return

    random.shuffle(all_stories)
    split      = max(1, int(len(all_stories) * TRAIN_SPLIT))
    train      = all_stories[:split]
    val        = all_stories[split:] if len(all_stories) > 1 else all_stories[:1]

    train_file = os.path.join(ENGLISH_PROCESSED_DIR, "train.txt")
    val_file   = os.path.join(ENGLISH_PROCESSED_DIR, "val.txt")

    with open(train_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(train))

    with open(val_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(val))

    print(f"  ✅ Train : {len(train)} stories → {train_file}")
    print(f"  ✅ Val   : {len(val)} stories   → {val_file}")



# SAVE REPORT


def save_report(hindi_report, english_report, stats):
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("COMPLETE DATA CLEANING REPORT\n")
        f.write(f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")

        f.write("SUMMARY:\n")
        for line in stats:
            f.write(f"  {line}\n")

        f.write("\nHINDI FILES:\n")
        for line in hindi_report:
            f.write(f"  {line}\n")

        f.write("\nENGLISH FILES:\n")
        for line in english_report:
            f.write(f"  {line}\n")

    print(f"\n  📄 Report saved → {REPORT_FILE}")



# SHOW STATS


def show_final_stats():
    print("\n" + "="*60)
    print("📊 FINAL DATASET STATS")
    print("="*60)

    for lang, raw_dir, proc_dir in [
        ("Hindi 🇮🇳",   HINDI_RAW_DIR,   HINDI_PROCESSED_DIR),
        ("English 🇬🇧", ENGLISH_RAW_DIR, ENGLISH_PROCESSED_DIR),
    ]:
        total_stories = 0
        total_words   = 0

        for category in CATEGORIES:
            cat_dir = os.path.join(raw_dir, category)
            if not os.path.exists(cat_dir):
                continue
            files = [f for f in os.listdir(cat_dir) if f.endswith('.txt')]
            for fn in files:
                fp = os.path.join(cat_dir, fn)
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                total_stories += 1
                total_words   += len(text.split())

        train_file = os.path.join(proc_dir, "train.txt")
        val_file   = os.path.join(proc_dir, "val.txt")
        t_count    = 0
        v_count    = 0

        if os.path.exists(train_file):
            with open(train_file, 'r', encoding='utf-8') as f:
                t_count = f.read().count("<s>") if lang.startswith("Hindi") else f.read().count("This is a horror")
        if os.path.exists(val_file):
            with open(val_file, 'r', encoding='utf-8') as f:
                v_count = f.read().count("<s>") if lang.startswith("Hindi") else f.read().count("This is a horror")

        print(f"\n  {lang}")
        print(f"    Raw stories  : {total_stories}")
        print(f"    Total words  : {total_words:,}")
        print(f"    Train file   : {t_count} stories")
        print(f"    Val file     : {v_count} stories")

    print("="*60 + "\n")



# MAIN


def main():
    print("\n" + "="*60)
    print("🧹 COMPLETE DATA CLEANER — Hindi + English")
    print("="*60)
    print("  1. Clean + prepare both Hindi and English")
    print("  2. Clean only")
    print("  3. Prepare processed files only")
    print("  4. Show stats only")
    print("="*60)

    choice = input("\n  Choose (1/2/3/4): ").strip()

    hindi_report   = []
    english_report = []
    stats          = []

    if choice in ["1", "2"]:
        # Clean Hindi
        h_report, h_pass, h_fail = process_hindi()
        hindi_report = h_report
        stats.append(f"Hindi   → {h_pass} passed  {h_fail} failed")

        # Clean English
        e_report, e_pass, e_fail, e_skip = process_english()
        english_report = e_report
        stats.append(f"English → {e_pass} passed  {e_fail} failed  {e_skip} skipped")

        # Save report
        save_report(hindi_report, english_report, stats)

    if choice in ["1", "3"]:
        # Prepare training files
        prepare_hindi_processed()
        prepare_english_processed()

    if choice in ["1", "2", "3", "4"]:
        show_final_stats()

    print("="*60)
    print("✅ DONE!")
    if choice in ["1", "3"]:
        print("   Next steps:")
        print("   → python backend/model/train.py")
        print("   → python backend/model/train_english.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()