import os
import re
import unicodedata

RAW_DIR = "data/raw"

ALLOWED_HINDI = set(range(0x0900, 0x0980))   # Devanagari only
ALLOWED_CHARS = set('।?!,\'-\" \n\r')
ALLOWED_DIGITS = set('0123456789०१२३४५६७८९')

def is_allowed(char):
    cp = ord(char)
    return (
        cp in ALLOWED_HINDI or
        char in ALLOWED_CHARS or
        char in ALLOWED_DIGITS
    )

def nuclear_clean(text):
    # Step 1 - Unicode normalize
    text = unicodedata.normalize("NFC", text)

    # Step 2 - Remove EVERY non-Hindi character strictly
    text = "".join(c for c in text if is_allowed(c))

    # Step 3 - Remove leftover garbage patterns
    text = re.sub(r'[^\u0900-\u097F\s।?!,\'\"\-\n०-९0-9]', '', text)

    # Step 4 - Fix spacing
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Step 5 - Remove lines with less than 5 Hindi words
    lines = text.split('\n')
    good_lines = []
    for line in lines:
        hindi_words = [w for w in line.split()
                      if any(0x0900 <= ord(c) <= 0x097F for c in w)]
        if len(hindi_words) >= 5:
            good_lines.append(line)
    text = '\n'.join(good_lines)

    return text.strip()

def main():
    files = [f for f in os.listdir(RAW_DIR) if f.endswith('.txt')]
    print(f"\n Nuclear cleaning {len(files)} files...\n")

    kept    = []
    deleted = []

    for filename in files:
        filepath = os.path.join(RAW_DIR, filename)

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original = f.read()

        cleaned = nuclear_clean(original)

        # Count Hindi chars ratio
        hindi  = sum(1 for c in cleaned if 0x0900 <= ord(c) <= 0x097F)
        total  = len(cleaned.replace(' ','').replace('\n',''))
        ratio  = (hindi/total*100) if total > 0 else 0
        words  = len(cleaned.split())

        if words >= 150 and ratio >= 75:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f" {filename}: {words} words, {ratio:.0f}% Hindi")
            kept.append(filename)
        else:
            os.remove(filepath)
            print(f"  DELETED {filename}: only {words} words, {ratio:.0f}% Hindi")
            deleted.append(filename)

    print(f"\n{'='*50}")
    print(f" Kept    : {len(kept)} files")
    print(f"  Deleted : {len(deleted)} files")

    if len(kept) < 30:
        print(f"\n  WARNING: Only {len(kept)} stories!")
        print("   You need at least 50 for good results.")
        print("   Add more stories from:")
        print("   → pratilipi.com (search: डरावनी कहानी)")
        print("   → hindiinhindi.com")
        print("   → kahaniyan.net")
    else:
        print(f"\n {len(kept)} clean stories ready for training!")

if __name__ == "__main__":
    main()