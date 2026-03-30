'''import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"  # for better error messages
import sys
import torch
torch.cuda.empty_cache()
from transformers import (GPT2LMHeadModel, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments, EarlyStoppingCallback)

# CONFIG

MODEL_NAME        = "gpt2-medium"
SAVED_MODEL_DIR   = "saved_model_english"
TRAIN_FILE        = "data/processed_english/train.txt"
VAL_FILE          = "data/processed_english/val.txt"

EPOCHS            = 10
BATCH_SIZE        = 2
LEARNING_RATE     = 3e-5
BLOCK_SIZE        = 256
GRAD_ACCUM        = 4
WARMUP_STEPS      = 100
SAVE_STEPS        = 200
LOGGING_STEPS     = 50
FP16              = True

# STEP 1 — CHECK GPU

def check_gpu():
    print("\n" + "="*60)
    print("  SYSTEM CHECK")
    print("="*60)
    if torch.cuda.is_available():
        print(f" GPU   : {torch.cuda.get_device_name(0)}")
        print(f" VRAM  : {round(torch.cuda.get_device_properties(0).total_memory/1024**3,2)} GB")
    else:
        print("  No GPU — training on CPU (slow!)")
    print("="*60 + "\n")


# STEP 2 — LOAD GPT-2

def load_model():
    print(" Loading GPT-2 model...")
    print("   (First time downloads ~500MB)\n")

    tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)

    # GPT2 needs a pad token
    tokenizer.pad_token = tokenizer.eos_token

    model = GPT2LMHeadModel.from_pretrained(MODEL_NAME, torch_dtype=torch.float16, low_cpu_mem_usage=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = model.to(device) #type: ignore

    print(f" GPT-2 loaded on : {device}")
    print(f" Parameters      : {round(sum(p.numel() for p in model.parameters())/1e6,1)}M\n")

    return tokenizer, model

# STEP 3 — LOAD DATASET

def load_datasets(tokenizer):
    print(" Loading datasets...")

    train_dataset = TextDataset(
        tokenizer  = tokenizer,
        file_path  = TRAIN_FILE,
        block_size = BLOCK_SIZE
    )

    val_dataset = TextDataset(
        tokenizer  = tokenizer,
        file_path  = VAL_FILE,
        block_size = BLOCK_SIZE
    )

    print(f" Train samples : {len(train_dataset)}")
    print(f" Val samples   : {len(val_dataset)}\n")

    return train_dataset, val_dataset

# STEP 4 — TRAIN

def train(model, tokenizer, train_dataset, val_dataset):
    print("  Starting English Horror Training...\n")

    data_collator = DataCollatorForLanguageModeling(
        tokenizer = tokenizer,
        mlm       = False
    )

    training_args = TrainingArguments( #type : ignore
    output_dir                  = "saved_model_english",
    overwrite_output_dir        = True,
    num_train_epochs            = 10,

    # ── Memory fixes ──
    per_device_train_batch_size = 1,        # reduced from 2/4 to 1
    per_device_eval_batch_size  = 1,        # reduced to 1
    gradient_accumulation_steps = 16,       # increased to compensate
    fp16                        = False,    # disabled — causes OOM on small GPU
    dataloader_pin_memory       = False,    # saves memory

    # ── Rest of settings ──
    save_steps                  = 200,
    save_total_limit            = 2,
    logging_steps               = 50,
    evaluation_strategy         = "steps",
    eval_steps                  = 200,
    warmup_steps                = 100,
    learning_rate               = 2e-5,
    weight_decay                = 0.01,
    load_best_model_at_end      = True,
    report_to                   = [], 
)

    trainer = Trainer(
        model         = model,
        args          = training_args,
        train_dataset = train_dataset,
        eval_dataset  = val_dataset,
        data_collator = data_collator,
        callbacks     = [EarlyStoppingCallback(early_stopping_patience=3)]
    )

    trainer.train()
    return trainer

# STEP 5 — SAVE

def save_model(model, tokenizer):
    print(f"\n Saving English model to {SAVED_MODEL_DIR}...")
    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    model.save_pretrained(SAVED_MODEL_DIR)
    tokenizer.save_pretrained(SAVED_MODEL_DIR)
    print(f" Model saved!\n")

# MAIN

def main():
    print("\n English Horror Story Generator — Training")
    print("="*60)

    check_gpu()

    tokenizer, model = load_model()

    if not os.path.exists(TRAIN_FILE):
        print(" Training file not found!")
        print("   Run: python data/data_prep_english.py first")
        return

    train_dataset, val_dataset = load_datasets(tokenizer)

    trainer = train(model, tokenizer, train_dataset, val_dataset)

    save_model(model, tokenizer)

    print("="*60)
    print(" ENGLISH TRAINING COMPLETE!")
    print(f"   Model saved to : {SAVED_MODEL_DIR}/")
    print("   Next step      : python backend/model/generate.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()'''

import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

import sys
import torch
torch.cuda.empty_cache()

from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
MODEL_NAME      = "gpt2-medium"
SAVED_MODEL_DIR = "saved_model_english"
TRAIN_FILE      = "data/processed_english/train.txt"
VAL_FILE        = "data/processed_english/val.txt"

BLOCK_SIZE      = 128

# ─────────────────────────────────────────
# CATEGORY TOKENS
# teaches model category → story mapping
# ─────────────────────────────────────────
ENGLISH_CATEGORY_TOKENS = {
    "witch"         : "witch spell curse magic coven",
    "ghost"         : "ghost spirit haunted supernatural apparition",
    "haunted_house" : "haunted house mansion abandoned dark rooms",
    "graveyard"     : "graveyard cemetery grave tombstone dead",
    "demon"         : "demon devil evil dark entity possessed",
    "vampire"       : "vampire blood fangs immortal night creature",
    "monster"       : "monster creature beast lurking predator",
    "cursed_object" : "cursed object ancient artifact dark relic",
    "possessed"     : "possessed body taken over evil inside",
    "general_horror": "horror scary dark terrifying evil night",
}


# ─────────────────────────────────────────
# STEP 1 — CHECK GPU
# ─────────────────────────────────────────
def check_gpu():
    print("\n" + "="*60)
    print("  SYSTEM CHECK")
    print("="*60)
    if torch.cuda.is_available():
        print(f"  GPU   : {torch.cuda.get_device_name(0)}")
        print(f"  VRAM  : {round(torch.cuda.get_device_properties(0).total_memory/1024**3, 2)} GB")
        print(f"  CUDA  : {torch.version.cuda}")
    else:
        print("  No GPU — training on CPU (slow!)")
    print("="*60 + "\n")


# ─────────────────────────────────────────
# STEP 2 — LOAD GPT-2
# ─────────────────────────────────────────
def load_model():
    print("  Loading GPT-2 Medium model...")
    print("  (First time downloads ~500MB)\n")

    tokenizer           = GPT2Tokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    model = GPT2LMHeadModel.from_pretrained(
        MODEL_NAME,
        torch_dtype       = torch.float16,
        low_cpu_mem_usage = True
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = model.to(device)  # type: ignore

    print(f"  GPT-2 loaded on : {device}")
    print(f"  Parameters      : {round(sum(p.numel() for p in model.parameters())/1e6, 1)}M\n")

    return tokenizer, model


# ─────────────────────────────────────────
# STEP 3 — PREPARE CATEGORY TRAINING FILE
# writes category-prefixed stories to train file
# ─────────────────────────────────────────
def prepare_category_training_file(english_raw_dir, output_train, output_val):
    import random

    categories = [
        "witch", "ghost", "haunted_house", "graveyard",
        "demon", "vampire", "monster", "cursed_object",
        "possessed", "general_horror"
    ]

    all_stories = []
    found_cats  = False

    print("  Loading category stories...")

    for category in categories:
        cat_dir = os.path.join(english_raw_dir, category)

        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith('.txt')]
        if not files:
            continue

        found_cats     = True
        cat_tokens     = ENGLISH_CATEGORY_TOKENS.get(category, "horror scary")
        cat_count      = 0

        for filename in files:
            filepath = os.path.join(cat_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                story = f.read().strip()

            if len(story) < 100:
                continue

            # Format with category prefix
            # This teaches GPT-2: category tokens → category story
            formatted = (
                f"This is a horror story about {cat_tokens}. "
                f"{story}"
                f"\n\n"
            )
            all_stories.append(formatted)
            cat_count += 1

        if cat_count > 0:
            print(f"  ✅ {category:20s} → {cat_count} stories")

    if not found_cats:
        print("  ⚠️  No category folders found")
        print("  Run: python data/generate_training_data.py first")
        return False

    if not all_stories:
        print("  ❌ No valid stories found!")
        return False

    # Shuffle
    random.shuffle(all_stories)

    # Split 80/20
    split      = max(1, int(len(all_stories) * 0.8))
    train_data = all_stories[:split]
    val_data   = all_stories[split:] if len(all_stories) > 1 else all_stories[:1]

    # Save to processed files
    os.makedirs(os.path.dirname(output_train), exist_ok=True)

    with open(output_train, 'w', encoding='utf-8') as f:
        f.write('\n'.join(train_data))

    with open(output_val, 'w', encoding='utf-8') as f:
        f.write('\n'.join(val_data))

    print(f"\n  Train : {len(train_data)} stories → {output_train}")
    print(f"  Val   : {len(val_data)} stories → {output_val}\n")
    return True


# ─────────────────────────────────────────
# STEP 4 — LOAD DATASETS
# ─────────────────────────────────────────
def load_datasets(tokenizer):
    print("  Loading datasets...")

    train_dataset = TextDataset(
        tokenizer  = tokenizer,
        file_path  = TRAIN_FILE,
        block_size = BLOCK_SIZE
    )

    val_dataset = TextDataset(
        tokenizer  = tokenizer,
        file_path  = VAL_FILE,
        block_size = BLOCK_SIZE
    )

    print(f"  Train samples : {len(train_dataset)}")
    print(f"  Val samples   : {len(val_dataset)}\n")

    return train_dataset, val_dataset


# ─────────────────────────────────────────
# STEP 5 — TRAIN
# ─────────────────────────────────────────
def train(model, tokenizer, train_dataset, val_dataset):
    print("  Starting English Horror Training...\n")

    data_collator = DataCollatorForLanguageModeling(
        tokenizer = tokenizer,
        mlm       = False
    )

    training_args = TrainingArguments(  # type: ignore
        output_dir                  = "logs_english",
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
        report_to                   = [],
    )

    trainer = Trainer(
        model         = model,
        args          = training_args,
        train_dataset = train_dataset,
        eval_dataset  = val_dataset,
        data_collator = data_collator,
        callbacks     = [EarlyStoppingCallback(early_stopping_patience=5)]
    )

    trainer.train()
    return trainer


# ─────────────────────────────────────────
# STEP 6 — SAVE
# ─────────────────────────────────────────
def save_model(model, tokenizer):
    print(f"\n  Saving English model to {SAVED_MODEL_DIR}...")
    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    model.save_pretrained(SAVED_MODEL_DIR)
    tokenizer.save_pretrained(SAVED_MODEL_DIR)
    print(f"  Model saved!\n")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n  English Horror Story Generator — Training")
    print("="*60)

    check_gpu()

    tokenizer, model = load_model()

    # Check category folders
    english_raw_dir  = "data/raw_english"
    has_categories   = any(
        os.path.exists(os.path.join(english_raw_dir, cat))
        for cat in ["witch", "ghost", "demon", "vampire"]
    )

    if has_categories:
        print("  ✅ Found category folders — preparing category training data\n")
        success = prepare_category_training_file(
            english_raw_dir, TRAIN_FILE, VAL_FILE
        )
        if not success:
            print("  ❌ Failed to prepare training data")
            return
    else:
        print("  ⚠️  No category folders found")
        if not os.path.exists(TRAIN_FILE):
            print("  ❌ Training file not found!")
            print("  Run: python data/generate_training_data.py first")
            return
        print("  Using existing processed files\n")

    train_dataset, val_dataset = load_datasets(tokenizer)

    trainer = train(model, tokenizer, train_dataset, val_dataset)

    save_model(model, tokenizer)

    print("="*60)
    print("  ENGLISH TRAINING COMPLETE!")
    print(f"  Model saved to : {SAVED_MODEL_DIR}/")
    print("  Next step      : python backend/model/generate.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()