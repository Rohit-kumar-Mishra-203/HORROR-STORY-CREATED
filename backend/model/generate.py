import os
import sys
import torch
from transformers import (AutoTokenizer, AutoModelForSeq2SeqLM, GPT2LMHeadModel, GPT2Tokenizer)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.model.config import *


# LOAD HINDI MODEL (IndicBART)

def load_hindi_model():
    print("\n Loading Hindi Horror model (IndicBART)...")

    if not os.path.exists(SAVED_MODEL_DIR):
        print(f" Hindi model not found at '{SAVED_MODEL_DIR}/'")
        print("   Run: python backend/model/train.py first")
        return None, None, None

    tokenizer = AutoTokenizer.from_pretrained(
        SAVED_MODEL_DIR,
        use_fast=False,
        keep_accents=True,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        SAVED_MODEL_DIR,
        torch_dtype=torch.float32
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = model.to(device)
    model.eval()

    print(f" Hindi model loaded on : {device}\n")
    return tokenizer, model, device



# LOAD ENGLISH MODEL (GPT-2)

def load_english_model():
    print("\n Loading English Horror model (GPT-2)...")

    english_model_dir = "saved_model_english"

    if not os.path.exists(english_model_dir):
        print(f" English model not found at '{english_model_dir}/'")
        print("   Run: python backend/model/train_english.py first")
        return None, None, None

    tokenizer          = GPT2Tokenizer.from_pretrained(english_model_dir)
    tokenizer.pad_token = tokenizer.eos_token

    model = GPT2LMHeadModel.from_pretrained(
        english_model_dir,
        torch_dtype=torch.float32
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = model.to(device) #type: ignore
    model.eval()

    print(f" English model loaded on : {device}\n")
    return tokenizer, model, device



# GENERATE HINDI STORY

def generate_hindi_story(prompt, tokenizer, model, device, max_length=700):
    print("  Generating Hindi horror story...\n")

    hindi_prompt = f"<s> <2hi> {prompt}"

    inputs = tokenizer(
        hindi_prompt,
        return_tensors="pt",
        max_length=MAX_SOURCE_LENGTH,
        truncation=True,
        padding=True,
    ).to(device)

    try:
        forced_bos_token_id = tokenizer.convert_tokens_to_ids("<2hi>")
        if forced_bos_token_id == tokenizer.unk_token_id:
            forced_bos_token_id = None
    except:
        forced_bos_token_id = None

    with torch.no_grad():
        outputs = model.generate(
            input_ids           = inputs["input_ids"],
            attention_mask      = inputs["attention_mask"],
            max_length          = max_length,
            min_length          = 200,
            do_sample           = False,
            num_beams           = 4,
            repetition_penalty  = 2.5,
            no_repeat_ngram_size= 3,
            length_penalty      = 2.0,
            early_stopping      = True,
            forced_bos_token_id = forced_bos_token_id,
        )

    story = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )
    return story



# GENERATE ENGLISH STORY

def generate_english_story(prompt, tokenizer, model, device, max_length=700):
    print("  Generating English horror story...\n")

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=200,
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids           = inputs["input_ids"],
            attention_mask      = inputs["attention_mask"],
            max_length          = max_length,
            min_length          = 200,
            do_sample           = True,
            temperature         = 0.85,
            top_k               = 50,
            top_p               = 0.92,
            repetition_penalty  = 1.8,
            no_repeat_ngram_size= 3,
            pad_token_id        = tokenizer.eos_token_id,
        )

    story = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )
    return story



# DISPLAY STORY

def display_story(prompt, story, language):
    flag = "🇮🇳" if language == "hindi" else "🇬🇧"
    print("="*60)
    print(f" {flag} HORROR STORY")
    print("="*60)
    print(f" Prompt : {prompt}")
    print("-"*60)
    print(f"\n{story}\n")
    print("="*60)



# SAVE STORY

def save_story(prompt, story, language):
    output_dir = f"output_stories/{language}"
    os.makedirs(output_dir, exist_ok=True)
    files    = os.listdir(output_dir)
    file_num = len(files) + 1
    filename = f"{output_dir}/story_{file_num}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Language: {language.upper()}\n")
        f.write(f"Prompt: {prompt}\n\n")
        f.write(story)

    print(f" Story saved to {filename}\n")



# INTERACTIVE MODE

def interactive_mode(hindi_tok, hindi_model, hindi_device, eng_tok, eng_model, eng_device):

    print("\n" + "="*60)
    print(" HORROR STORY GENERATOR")
    print("   Hindi 🇮🇳  |  English 🇬🇧")
    print("="*60)
    print("   Type 'exit' to quit\n")

    while True:
        print("-"*60)

        # Language selection
        print(" Select Language:")
        print("   1. Hindi (हिंदी)")
        print("   2. English")
        lang_choice = input("   Choose (1/2): ").strip()

        if lang_choice not in ["1", "2"]:
            print("  Invalid choice. Please enter 1 or 2.\n")
            continue

        language = "hindi" if lang_choice == "1" else "english"

        # Check model available
        if language == "hindi" and hindi_model is None:
            print(" Hindi model not loaded!")
            print("   Run: python backend/model/train.py first\n")
            continue

        if language == "english" and eng_model is None:
            print(" English model not loaded!")
            print("   Run: python backend/model/train_english.py first\n")
            continue

        # Get prompt
        if language == "hindi":
            prompt = input("\n अपना prompt यहाँ लिखें: ").strip()
        else:
            prompt = input("\n Enter your horror prompt: ").strip()

        if prompt.lower() == "exit":
            print("\n Goodbye!\n")
            break

        if len(prompt) < 5:
            print("  Prompt too short!\n")
            continue

        # Story length
        print("\n Story length:")
        print("   1. Short  (~200 words)")
        print("   2. Medium (~400 words) — recommended")
        print("   3. Long   (~600 words)")
        choice     = input("   Choose (1/2/3): ").strip()
        length_map = {"1": 300, "2": 500, "3": 700}
        max_length = length_map.get(choice, 500)

        # Generate
        if language == "hindi":
            story = generate_hindi_story(
                prompt, hindi_tok, hindi_model, hindi_device, max_length
            )
        else:
            story = generate_english_story(
                prompt, eng_tok, eng_model, eng_device, max_length
            )

        # Display
        display_story(prompt, story, language)

        # Save
        save = input(" Save this story? (y/n): ").strip().lower()
        if save == "y":
            save_story(prompt, story, language)

        print()



# MAIN

def main():
    print("\n Loading Horror Story Generator...\n")

    # Load both models
    hindi_tok,   hindi_model,   hindi_device   = load_hindi_model()
    eng_tok,     eng_model,     eng_device     = load_english_model()

    # Check at least one model is available
    if hindi_model is None and eng_model is None:
        print(" No models found! Please train at least one model first.")
        print("   Hindi  : python backend/model/train.py")
        print("   English: python backend/model/train_english.py")
        return

    # Run interactive mode
    interactive_mode(
        hindi_tok, hindi_model, hindi_device,
        eng_tok,   eng_model,   eng_device
    )


if __name__ == "__main__":
    main()