'''import os
import torch
from transformers import (AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq, EarlyStoppingCallback)
from datasets import Dataset
from tqdm import tqdm
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.model.config import *

# STEP 1 — CHECK GPU

def check_gpu():
    print("\n" + "="*60)
    print("  SYSTEM CHECK")
    print("="*60)
    if torch.cuda.is_available():
        print(f" GPU Found  : {torch.cuda.get_device_name(0)}")
        print(f" VRAM       : {round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2)} GB")
        print(f" CUDA       : {torch.version.cuda}")
    else:
        print("  No GPU found — training on CPU (will be very slow!)")
    print("="*60 + "\n")

# STEP 2 — LOAD TOKENIZER & MODEL

def load_model_and_tokenizer():
    print(" Loading IndicBART model and tokenizer...")
    print("   (First time will download ~1GB — please wait)\n")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_fast=False,
        keep_accents=True,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    # Move model to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    print(f" Model loaded on: {device}")
    print(f" Model parameters: {round(sum(p.numel() for p in model.parameters()) / 1e6, 1)}M\n")

    return tokenizer, model


# STEP 3 — LOAD STORIES FROM FILE

def load_stories(filepath):
    print(f" Loading stories from {filepath}...")
    stories = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        raw_stories = content.strip().split("\n\n")
        for story in raw_stories:
            story = story.strip()
            if len(story) > 100:
                stories.append(story)

    print(f" Loaded {len(stories)} stories\n")
    return stories


# STEP 4 — TOKENIZE DATASET

def tokenize_data(stories, tokenizer):
    print(" Tokenizing stories...")

    # For IndicBART — input is story beginning, output is full story
    # We split each story: first 30% = input prompt, rest = target output
    inputs  = []
    targets = []

    for story in tqdm(stories, desc="Preparing"):
        words = story.split()
        if len(words) < 20:
            continue
        split_point = max(10, len(words) // 3)   # first 33% as prompt
        input_text  = " ".join(words[:split_point])
        target_text = " ".join(words[split_point:])
        inputs.append(input_text)
        targets.append(target_text)

    # Tokenize
    model_inputs = tokenizer(
        inputs,
        max_length=MAX_SOURCE_LENGTH,
        padding="max_length",
        truncation=True,
    )

    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            targets,
            max_length=MAX_TARGET_LENGTH,
            padding="max_length",
            truncation=True,
        )

    model_inputs["labels"] = labels["input_ids"]

    # Replace padding token id with -100 so loss ignores padding
    model_inputs["labels"] = [
        [-100 if token == tokenizer.pad_token_id else token for token in label]
        for label in model_inputs["labels"]
    ]

    print(f" Tokenized {len(inputs)} story pairs\n")
    return model_inputs

# STEP 5 — CREATE HUGGINGFACE DATASET

def create_dataset(tokenized_data):
    return Dataset.from_dict(tokenized_data)

# STEP 6 — TRAIN

def train(model, tokenizer, train_dataset, val_dataset):
    print(" Starting Training...\n")

    # Training arguments optimized for RTX 2050
    training_args = Seq2SeqTrainingArguments(
        output_dir                  = "logs",
        num_train_epochs            = EPOCHS,
        per_device_train_batch_size = BATCH_SIZE,
        per_device_eval_batch_size  = BATCH_SIZE,
        learning_rate               = LEARNING_RATE,
        warmup_steps                = WARMUP_STEPS,
        gradient_accumulation_steps = GRADIENT_ACCUMULATION_STEPS,
        fp16                        = FP16,
        evaluation_strategy         = "steps",
        eval_steps                  = SAVE_STEPS,
        save_steps                  = SAVE_STEPS,
        save_total_limit            = 2,
        load_best_model_at_end      = True,
        predict_with_generate       = True,
        logging_dir                 = "logs",
        logging_steps               = LOGGING_STEPS,
       # report_to                   = "wandb",   # change to "wandb" if you want monitoring
        overwrite_output_dir        = True,
    )

    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        padding=True
    )

    trainer = Seq2SeqTrainer(
        model           = model,
        args            = training_args,
        train_dataset   = train_dataset,
        eval_dataset    = val_dataset,
        tokenizer       = tokenizer,
        data_collator   = data_collator,
        callbacks       = [EarlyStoppingCallback(early_stopping_patience=3)]
    )

    trainer.train()
    return trainer

# STEP 7 — SAVE MODEL

def save_model(model, tokenizer):
    print(f"\n Saving model to {SAVED_MODEL_DIR}...")
    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    model.save_pretrained(SAVED_MODEL_DIR)
    tokenizer.save_pretrained(SAVED_MODEL_DIR)
    print(f" Model saved to {SAVED_MODEL_DIR}\n")

# MAIN

def main():
    print("\n Hindi Horror Story Generator — Training Started")
    print("="*60)

    # Step 1 - Check GPU
    check_gpu()

    # Step 2 - Load model
    tokenizer, model = load_model_and_tokenizer()

    # Step 3 - Load stories
    train_stories = load_stories(TRAIN_FILE)
    val_stories   = load_stories(VAL_FILE)

    if len(train_stories) == 0:
        print(" No training stories found! Run data_prep.py first.")
        return

    # Step 4 - Tokenize
    train_tokenized = tokenize_data(train_stories, tokenizer)
    val_tokenized   = tokenize_data(val_stories,   tokenizer)

    # Step 5 - Create datasets
    train_dataset = create_dataset(train_tokenized)
    val_dataset   = create_dataset(val_tokenized)

    print(f" Train samples : {len(train_dataset)}")
    print(f" Val samples   : {len(val_dataset)}\n")

    # Step 6 - Train
    trainer = train(model, tokenizer, train_dataset, val_dataset)

    # Step 7 - Save
    save_model(model, tokenizer)

    print("="*60)
    print(" TRAINING COMPLETE!")
    print(f"   Model saved to : {SAVED_MODEL_DIR}/")
    print("   Next step      : Run generate.py to test your model")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()'''

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback
)
from datasets import Dataset
from tqdm import tqdm
import sys

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
))
from backend.model.config import *

# ─────────────────────────────────────────
# CATEGORY TOKENS
# teaches model category → story mapping
# ─────────────────────────────────────────
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


# ─────────────────────────────────────────
# STEP 1 — CHECK GPU
# ─────────────────────────────────────────
def check_gpu():
    print("\n" + "="*60)
    print("  SYSTEM CHECK")
    print("="*60)
    if torch.cuda.is_available():
        print(f"  GPU Found  : {torch.cuda.get_device_name(0)}")
        print(f"  VRAM       : {round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2)} GB")
        print(f"  CUDA       : {torch.version.cuda}")
    else:
        print("  No GPU found — training on CPU (will be slow!)")
    print("="*60 + "\n")


# ─────────────────────────────────────────
# STEP 2 — LOAD TOKENIZER & MODEL
# ─────────────────────────────────────────
def load_model_and_tokenizer():
    print("  Loading IndicBART model and tokenizer...")
    print("  (First time will download ~1GB — please wait)\n")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_fast     = False,
        keep_accents = True,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = model.to(device)

    print(f"  Model loaded on : {device}")
    print(f"  Parameters      : {round(sum(p.numel() for p in model.parameters()) / 1e6, 1)}M\n")

    return tokenizer, model


# ─────────────────────────────────────────
# STEP 3 — LOAD STORIES FROM CATEGORY FOLDERS
# ─────────────────────────────────────────
def load_stories_category_wise(base_dir):
    print(f"  Loading stories from {base_dir}...")

    categories = [
        "witch", "ghost", "haunted_house", "graveyard",
        "demon", "vampire", "monster", "cursed_object",
        "possessed", "general_horror"
    ]

    all_stories = []

    for category in categories:
        cat_dir = os.path.join(base_dir, category)

        if not os.path.exists(cat_dir):
            # Try flat folder (old format)
            continue

        files = [
            f for f in os.listdir(cat_dir)
            if f.endswith('.txt')
        ]

        cat_token = HINDI_CATEGORY_TOKENS.get(category, "डरावना")
        cat_count = 0

        for filename in files:
            filepath = os.path.join(cat_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                story = f.read().strip()

            if len(story) < 100:
                continue

            # Add category prefix to story
            # This teaches model: category keyword → category story
            prefixed_story = (
                f"<s> <2hi> "
                f"यह एक {cat_token} की कहानी है। "
                f"{story} </s>"
            )
            all_stories.append(prefixed_story)
            cat_count += 1

        if cat_count > 0:
            print(f"  ✅ {category:20s} → {cat_count} stories")

    # Also load old flat format stories if exist
    if os.path.exists(base_dir):
        flat_files = [
            f for f in os.listdir(base_dir)
            if f.endswith('.txt')
        ]
        for filename in flat_files:
            filepath = os.path.join(base_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                story = f.read().strip()
            if len(story) > 100:
                prefixed = f"<s> <2hi> {story} </s>"
                all_stories.append(prefixed)

    print(f"\n  Total stories loaded : {len(all_stories)}\n")
    return all_stories


# ─────────────────────────────────────────
# LOAD FROM PROCESSED FILE (fallback)
# ─────────────────────────────────────────
def load_stories_from_file(filepath):
    print(f"  Loading from {filepath}...")
    stories = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        raw     = content.strip().split("\n\n")
        for story in raw:
            story = story.strip()
            if len(story) > 100:
                stories.append(story)
    print(f"  Loaded {len(stories)} stories\n")
    return stories


# ─────────────────────────────────────────
# STEP 4 — TOKENIZE DATASET
# ─────────────────────────────────────────
def tokenize_data(stories, tokenizer):
    print("  Tokenizing stories...")

    inputs  = []
    targets = []

    for story in tqdm(stories, desc="  Preparing"):
        # Clean story
        story = story.strip()
        if not story:
            continue

        words = story.split()
        if len(words) < 20:
            continue

        # Split: first 40% = input prompt, rest = target
        split_point = max(10, int(len(words) * 0.4))
        input_text  = " ".join(words[:split_point])
        target_text = " ".join(words[split_point:])

        inputs.append(input_text)
        targets.append(target_text)

    if not inputs:
        print("  ❌ No valid stories found!")
        return None

    # Tokenize inputs
    model_inputs = tokenizer(
        inputs,
        max_length = MAX_SOURCE_LENGTH,
        padding    = "max_length",
        truncation = True,
    )

    # Tokenize targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            targets,
            max_length = MAX_TARGET_LENGTH,
            padding    = "max_length",
            truncation = True,
        )

    model_inputs["labels"] = labels["input_ids"]

    # Replace padding with -100 so loss ignores padding
    model_inputs["labels"] = [
        [
            -100 if token == tokenizer.pad_token_id else token
            for token in label
        ]
        for label in model_inputs["labels"]
    ]

    print(f"  Tokenized {len(inputs)} story pairs\n")
    return model_inputs


# ─────────────────────────────────────────
# STEP 5 — CREATE DATASET
# ─────────────────────────────────────────
def create_dataset(tokenized_data):
    return Dataset.from_dict(tokenized_data)


# ─────────────────────────────────────────
# STEP 6 — TRAIN
# ─────────────────────────────────────────
def train(model, tokenizer, train_dataset, val_dataset):
    print("  Starting Hindi Horror Training...\n")

    training_args = Seq2SeqTrainingArguments(  # type: ignore
        output_dir                  = "logs_hindi",
        overwrite_output_dir        = True,
        num_train_epochs            = 20,
        per_device_train_batch_size = 1,
        per_device_eval_batch_size  = 1,
        gradient_accumulation_steps = 16,
        fp16                        = False,
        dataloader_pin_memory       = False,
        save_steps                  = 200,
        save_total_limit            = 2,
        logging_steps               = 50,
        evaluation_strategy         = "steps",
        eval_steps                  = 200,
        warmup_steps                = 200,
        learning_rate               = 1e-5,
        weight_decay                = 0.01,
        load_best_model_at_end      = True,
        predict_with_generate       = True,
        logging_dir                 = "logs_hindi",
        report_to                   = [],
    )

    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model   = model,
        padding = True
    )

    trainer = Seq2SeqTrainer(
        model         = model,
        args          = training_args,
        train_dataset = train_dataset,
        eval_dataset  = val_dataset,
        tokenizer     = tokenizer,
        data_collator = data_collator,
        callbacks     = [EarlyStoppingCallback(early_stopping_patience=5)]
    )

    trainer.train()
    return trainer


# ─────────────────────────────────────────
# STEP 7 — SAVE MODEL
# ─────────────────────────────────────────
def save_model(model, tokenizer):
    print(f"\n  Saving model to {SAVED_MODEL_DIR}...")
    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    model.save_pretrained(SAVED_MODEL_DIR)
    tokenizer.save_pretrained(SAVED_MODEL_DIR)
    print(f"  Model saved to {SAVED_MODEL_DIR}\n")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n  Hindi Horror Story Generator — Training")
    print("="*60)

    # Check GPU
    check_gpu()

    # Load model
    tokenizer, model = load_model_and_tokenizer()

    # Load stories — try category folders first
    hindi_raw_dir = "data/raw"
    train_stories = []
    val_stories   = []

    # Check if category folders exist
    has_categories = any(
        os.path.exists(os.path.join(hindi_raw_dir, cat))
        for cat in ["witch", "ghost", "demon", "vampire"]
    )

    if has_categories:
        print("  ✅ Found category folders — loading category-wise\n")
        all_stories = load_stories_category_wise(hindi_raw_dir)

        if not all_stories:
            print("  ❌ No stories found in category folders!")
            print("  Run: python data/generate_training_data.py first")
            return

        # Split 80/20
        import random
        random.shuffle(all_stories)
        split       = max(1, int(len(all_stories) * 0.8))
        train_stories = all_stories[:split]
        val_stories   = all_stories[split:] if len(all_stories) > 1 else all_stories[:1]

    else:
        # Fallback to processed files
        print("  ⚠️  No category folders — using processed files\n")
        if not os.path.exists(TRAIN_FILE):
            print("  ❌ Training file not found!")
            print("  Run: python data/data_prep_category.py first")
            return
        train_stories = load_stories_from_file(TRAIN_FILE)
        val_stories   = load_stories_from_file(VAL_FILE)

    if not train_stories:
        print("  ❌ No training data found!")
        return

    print(f"  Train stories : {len(train_stories)}")
    print(f"  Val stories   : {len(val_stories)}\n")

    # Tokenize
    train_tokenized = tokenize_data(train_stories, tokenizer)
    val_tokenized   = tokenize_data(val_stories,   tokenizer)

    if not train_tokenized or not val_tokenized:
        print("  ❌ Tokenization failed!")
        return

    # Create datasets
    train_dataset = create_dataset(train_tokenized)
    val_dataset   = create_dataset(val_tokenized)

    print(f"  Train samples : {len(train_dataset)}")
    print(f"  Val samples   : {len(val_dataset)}\n")

    # Train
    trainer = train(model, tokenizer, train_dataset, val_dataset)

    # Save
    save_model(model, tokenizer)

    print("="*60)
    print("  HINDI TRAINING COMPLETE!")
    print(f"  Model saved to : {SAVED_MODEL_DIR}/")
    print("  Next step      : python backend/model/generate.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()