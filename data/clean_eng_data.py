import os
import re

# CONFIG
ENGLISH_RAW_DIR   = "data/raw_english"
ENGLISH_PROCESSED = "data/processed_english"
REPORT_FILE       = "data/english_cleaning_report.txt"

MIN_WORDS         = 200
MAX_WORDS         = 1500
MIN_ENGLISH_RATIO = 0.70

os.makedirs(ENGLISH_PROCESSED, exist_ok=True)


# CLEANERS

def remove_html_tags(text):
    text = re.sub(r'<[^>]+>',    ' ', text)
    text = re.sub(r'&[a-zA-Z]+;',' ', text)
    text = re.sub(r'&#\d+;',     ' ', text)
    return text


def remove_urls(text):
    text = re.sub(r'http[s]?://\S+', ' ', text)
    text = re.sub(r'www\.\S+',       ' ', text)
    text = re.sub(r'\S+@\S+\.\S+',   ' ', text)
    return text


def remove_numbers(text):
    text = re.sub(r'\d+', ' ', text)
    return text


def remove_special_characters(text):
    text = re.sub(r'[#@$%^&*+=\[\]{}|\\/<>~`_]', ' ', text)
    return text


def remove_non_english(text):
    allowed = []
    for ch in text:
        cp = ord(ch)
        if (
            0x0041 <= cp <= 0x005A or   # A-Z
            0x0061 <= cp <= 0x007A or   # a-z
            ch in ' \n\t.,!?;:\'"()- '
        ):
            allowed.append(ch)
        else:
            allowed.append(' ')
    return ''.join(allowed)


def remove_extra_spaces(text):
    text = re.sub(r'[ \t]+',  ' ',   text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def remove_short_lines(text):
    lines       = text.split('\n')
    clean_lines = []
    for line in lines:
        stripped      = line.strip()
        words_in_line = re.findall(r'[a-zA-Z]+', stripped)
        if len(words_in_line) >= 3:
            clean_lines.append(stripped)
        elif not stripped:
            clean_lines.append('')
    return '\n'.join(clean_lines)


# FULL CLEAN PIPELINE

def clean_english_story(text):
    print("     → removing HTML tags")
    text = remove_html_tags(text)

    print("     → removing URLs and emails")
    text = remove_urls(text)

    print("     → removing numbers")
    text = remove_numbers(text)

    print("     → removing special characters")
    text = remove_special_characters(text)

    print("     → removing non-English characters")
    text = remove_non_english(text)

    print("     → removing short lines")
    text = remove_short_lines(text)

    print("     → cleaning extra spaces")
    text = remove_extra_spaces(text)

    return text


# VALIDATION

def get_english_ratio(text):
    english = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total   = sum(1 for c in text if c.isalpha())
    return english / total if total > 0 else 0


def count_words(text):
    return len(text.split())


def validate_story(text, filename):
    words = count_words(text)
    ratio = get_english_ratio(text)

    if words < MIN_WORDS:
        return False, f"too short ({words} words — min {MIN_WORDS})"
    if ratio < MIN_ENGLISH_RATIO:
        return False, f"low English ratio ({ratio:.0%} — min {MIN_ENGLISH_RATIO:.0%})"
    return True, f"{words} words  {ratio:.0%} English"


# SPLIT LONG STORIES

def split_long_story(text, filename):
    words = count_words(text)
    if words <= MAX_WORDS:
        return [(text, filename)]

    print(f"     Splitting '{filename}' ({words}w) into chunks...")

    paragraphs = text.split('\n\n')
    chunks     = []
    current    = []
    cur_words  = 0
    chunk_num  = 1

    for para in paragraphs:
        para_words = count_words(para)
        if cur_words + para_words > MAX_WORDS and current:
            chunk_text = '\n\n'.join(current)
            base       = os.path.splitext(filename)[0]
            chunk_name = f"{base}_part{chunk_num}.txt"
            chunks.append((chunk_text, chunk_name))
            chunk_num += 1
            current    = [para]
            cur_words  = para_words
        else:
            current.append(para)
            cur_words += para_words

    if current:
        chunk_text = '\n\n'.join(current)
        base       = os.path.splitext(filename)[0]
        chunk_name = f"{base}_part{chunk_num}.txt"
        chunks.append((chunk_text, chunk_name))

    print(f"     Split into {len(chunks)} parts")
    return chunks


# PROCESS ALL FILES

def process_english_files():
    print("\n" + "="*60)
    print("🇬🇧 ENGLISH STORY CLEANER")
    print("="*60)

    if not os.path.exists(ENGLISH_RAW_DIR):
        print(f" Raw dir not found: {ENGLISH_RAW_DIR}")
        print(f"   Create it and add your .txt story files")
        return

    files = [f for f in os.listdir(ENGLISH_RAW_DIR) if f.endswith('.txt')]

    if not files:
        print(f" No .txt files found in {ENGLISH_RAW_DIR}/")
        return

    print(f" Found {len(files)} files in {ENGLISH_RAW_DIR}/\n")

    passed  = 0
    failed  = 0
    skipped = 0
    report  = []

    for filename in sorted(files):
        filepath = os.path.join(ENGLISH_RAW_DIR, filename)
        print(f"   Processing: {filename}")

        # Read file
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
        except Exception as e:
            print(f"      Read error: {e}\n")
            failed += 1
            report.append(f"FAIL: {filename} — read error: {e}")
            continue

        if not raw_text.strip():
            print(f"      File is empty\n")
            failed += 1
            report.append(f"FAIL: {filename} — empty file")
            continue

        # Clean
        clean_text = clean_english_story(raw_text)

        # Validate
        valid, reason = validate_story(clean_text, filename)

        if not valid:
            print(f"      FAILED → {reason}\n")
            report.append(f"FAIL: {filename} — {reason}")
            failed += 1
            continue

        # Split if too long
        chunks = split_long_story(clean_text, filename)

        # Save chunks
        saved_count = 0
        for chunk_text, chunk_name in chunks:
            if count_words(chunk_text) < MIN_WORDS:
                print(f"       Chunk '{chunk_name}' too short — skipped")
                skipped += 1
                continue

            out_path = os.path.join(ENGLISH_PROCESSED, chunk_name)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(chunk_text)

            saved_count += 1

        words = count_words(clean_text)
        ratio = get_english_ratio(clean_text)
        print(f"      PASSED → {words}w  {ratio:.0%} English  ({saved_count} file(s) saved)\n")
        report.append(f"OK: {filename} — {words}w {ratio:.0%}")
        passed += 1

    # ── Summary ──
    print("="*60)
    print(" SUMMARY")
    print("="*60)
    print(f"  Total files  : {len(files)}")
    print(f"   Passed    : {passed}")
    print(f"   Failed    : {failed}")
    print(f"    Skipped   : {skipped}")
    print(f"   Saved to  : {ENGLISH_PROCESSED}/")
    print("="*60)

    # Save report
    save_report(report, passed, failed, skipped, len(files))


# SAVE REPORT

def save_report(report, passed, failed, skipped, total):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("ENGLISH DATA CLEANING REPORT\n")
        f.write(f"Generated : {timestamp}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total  : {total}\n")
        f.write(f"Passed : {passed}\n")
        f.write(f"Failed : {failed}\n")
        f.write(f"Skipped: {skipped}\n\n")
        f.write("DETAILS:\n")
        for line in report:
            f.write(f"  {line}\n")

    print(f"\n Report saved → {REPORT_FILE}\n")


# CHECK PROCESSED FILES

def check_processed():
    print("\n" + "="*60)
    print(" PROCESSED ENGLISH FILES")
    print("="*60)

    if not os.path.exists(ENGLISH_PROCESSED):
        print(" Processed folder not found")
        print("   Run cleaner first\n")
        return

    files      = [f for f in os.listdir(ENGLISH_PROCESSED) if f.endswith('.txt')]
    total_words= 0

    for filename in sorted(files):
        filepath = os.path.join(ENGLISH_PROCESSED, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            text  = f.read()
        words      = count_words(text)
        total_words+= words
        print(f"   {filename:35s} → {words:5d} words")

    print("="*60)
    print(f"  Total files : {len(files)}")
    print(f"  Total words : {total_words:,}")
    print("="*60 + "\n")


# MAIN

def main():
    print("\n ENGLISH STORY CLEANER")
    print("="*60)
    print("  What do you want to do?")
    print("  1. Clean raw English stories")
    print("  2. Check processed files")
    print("  3. Both")
    print("="*60)

    choice = input("\n  Choose (1/2/3): ").strip()

    if choice == "1":
        process_english_files()
    elif choice == "2":
        check_processed()
    elif choice == "3":
        process_english_files()
        check_processed()
    else:
        print("  Invalid choice — running cleaner\n")
        process_english_files()


if __name__ == "__main__":
    main()