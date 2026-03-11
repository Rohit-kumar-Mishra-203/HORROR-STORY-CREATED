import os
import sys
import torch
from transformers import (GPT2LMHeadModel, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments, EarlyStoppingCallback)

# CONFIG

MODEL_NAME        = "gpt2"
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

    model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)

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

    training_args = TrainingArguments(
        output_dir                  = "logs_english",
        num_train_epochs            = EPOCHS,
        per_device_train_batch_size = BATCH_SIZE,
        per_device_eval_batch_size  = BATCH_SIZE,
        learning_rate               = LEARNING_RATE,
        warmup_steps                = WARMUP_STEPS,
        gradient_accumulation_steps = GRAD_ACCUM,
        fp16                        = FP16,
        evaluation_strategy         = "steps",
        eval_steps                  = SAVE_STEPS,
        save_steps                  = SAVE_STEPS,
        save_total_limit            = 2,
        load_best_model_at_end      = True,
        logging_dir                 = "logs_english",
        logging_steps               = LOGGING_STEPS,
       # report_to                   = "none",
        overwrite_output_dir        = True,
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
    main()