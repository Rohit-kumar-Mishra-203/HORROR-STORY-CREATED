import os
import sys
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    GPT2LMHeadModel,
    GPT2Tokenizer
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.model.config          import *
from backend.model.prompt_engine   import process_user_input
from backend.model.story_builder   import build_story_prompt
from backend.model.tension_engine  import get_tension_suffix
from backend.model.twist_generator import get_twist, format_twist
from backend.features.story_library import init_library, add_story, rate_story
from backend.features.multi_voice_tts   import multivoice_menu
from backend.features.music_player import music_menu, stop_background_music


# ─────────────────────────────────────────
# LOAD HINDI MODEL
# ─────────────────────────────────────────
def load_hindi_model():
    print("\n📥 Loading Hindi Horror model (IndicBART)...")

    if not os.path.exists(SAVED_MODEL_DIR):
        print(f"❌ Hindi model not found at '{SAVED_MODEL_DIR}/'")
        print("   Run: python backend/model/train.py first")
        return None, None, None # type: ignore

    tokenizer = AutoTokenizer.from_pretrained(
        SAVED_MODEL_DIR,
        use_fast=False,
        keep_accents=True,
    )

    model: AutoModelForSeq2SeqLM = AutoModelForSeq2SeqLM.from_pretrained(
        SAVED_MODEL_DIR,
        torch_dtype=torch.float32
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = model.to(device)  # type: ignore
    model.eval()  #type: ignore

    print(f"✅ Hindi model loaded on : {device}\n")
    return tokenizer, model, device # type: ignore


# ─────────────────────────────────────────
# LOAD ENGLISH MODEL
# ─────────────────────────────────────────
def load_english_model():
    print("\n📥 Loading English Horror model (GPT-2)...")

    english_model_dir = "saved_model_english"

    if not os.path.exists(english_model_dir):
        print(f"❌ English model not found at '{english_model_dir}/'")
        print("   Run: python backend/model/train_english.py first")
        return None, None, None # type: ignore

    tokenizer           = GPT2Tokenizer.from_pretrained(english_model_dir)
    tokenizer.pad_token = tokenizer.eos_token

    model = GPT2LMHeadModel.from_pretrained(
        english_model_dir,
        torch_dtype=torch.float32
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = model.to(device)  # type: ignore
    model.eval() # type: ignore

    print(f"✅ English model loaded on : {device}\n")
    return tokenizer, model, device # type: ignore


# ─────────────────────────────────────────
# GENERATE HINDI STORY
# ─────────────────────────────────────────
def generate_hindi_story(prompt, tokenizer, model, device, max_length=700):
    print("✍️  Generating Hindi horror story...\n")

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
            input_ids            = inputs["input_ids"],
            attention_mask       = inputs["attention_mask"],
            max_length           = max_length,
            min_length           = 200,
            do_sample            = False,
            num_beams            = 4,
            repetition_penalty   = 2.5,
            no_repeat_ngram_size = 3,
            length_penalty       = 2.0,
            early_stopping       = True,
            forced_bos_token_id  = forced_bos_token_id,
        )

    story = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )
    return story


# ─────────────────────────────────────────
# GENERATE ENGLISH STORY
# ─────────────────────────────────────────
def generate_english_story(prompt, tokenizer, model, device, max_length=700):
    print("✍️  Generating English horror story...\n")

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=200,
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids            = inputs["input_ids"],
            attention_mask       = inputs["attention_mask"],
            max_length           = max_length,
            min_length           = 200,
            do_sample            = True,
            temperature          = 0.85,
            top_k                = 50,
            top_p                = 0.92,
            repetition_penalty   = 1.8,
            no_repeat_ngram_size = 3,
            pad_token_id         = tokenizer.eos_token_id,
        )

    story = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )
    return story


# ─────────────────────────────────────────
# BUILD COMPLETE ADVANCED STORY
# combines model output + tension + twist
# ─────────────────────────────────────────
def build_complete_story(base_story, language, category):
    # Add tension suffix
    tension = get_tension_suffix(language, intensity="high")

    # Add twist ending
    twist   = get_twist(language, category)
    twist   = format_twist(twist, language)

    # Combine everything
    complete_story = f"{base_story}\n\n{tension}\n{twist}"

    return complete_story


# ─────────────────────────────────────────
# DISPLAY STORY
# ─────────────────────────────────────────
def display_story(prompt, story, language, category):
    flag         = "🇮🇳" if language == "hindi" else "🇬🇧"
    category_str = category.replace("_", " ").title()

    print("\n" + "="*60)
    print(f"🎃 {flag} {category_str.upper()} HORROR STORY")
    print("="*60)
    print(f"📝 Prompt : {prompt}")
    print("-"*60)
    print(f"\n{story}\n")
    print("="*60)


# ─────────────────────────────────────────
# INTERACTIVE MODE
# ─────────────────────────────────────────
def interactive_mode(hindi_tok, hindi_model, hindi_device,
                     eng_tok,   eng_model,   eng_device):

    # Initialize story library
    init_library()

    print("\n" + "="*60)
    print("🎃 ADVANCED HORROR STORY GENERATOR")
    print("   Hindi 🇮🇳  |  English 🇬🇧")
    print("="*60)
    print("   Just type what you want naturally!")
    print()
    print("   Examples:")
    print("   → 'give me a witch story'")
    print("   → 'एक चुड़ैल की कहानी सुनाओ'")
    print("   → 'write a vampire horror story'")
    print("   → 'भूतिया हवेली की कहानी बताओ'")
    print("   → 'library' to manage your stories")
    print("   → 'exit' to quit")
    print("="*60 + "\n")

    while True:
        print("-"*60)
        user_input = input("📝 What story do you want? : ").strip()

        # Exit
        if user_input.lower() == "exit":
            print("\n👋 Goodbye! Stay scared! 🎃\n")
            break

        # Open library
        if user_input.lower() == "library":
            from backend.features.story_library import library_menu
            library_menu()
            continue

        if len(user_input) < 3:
            print("⚠️  Please type something!\n")
            continue

        # ── Process input through prompt engine ──
        prompt, language, category = process_user_input(user_input)

        # ── Check model available ──
        if language == "hindi" and hindi_model is None:
            print("❌ Hindi model not loaded!")
            print("   Run: python backend/model/train.py first\n")
            continue

        if language == "english" and eng_model is None:
            print("❌ English model not loaded!")
            print("   Run: python backend/model/train_english.py first\n")
            continue

        # ── Build smart story prompt ──
        smart_prompt, character, category = build_story_prompt(language, category)
        print(f"👤 Main Character : {character}")

        # ── Story length ──
        print("\n📏 Story length:")
        print("   1. Short  (~200 words)")
        print("   2. Medium (~400 words) — recommended")
        print("   3. Long   (~600 words)")
        choice     = input("   Choose (1/2/3): ").strip()
        length_map = {"1": 300, "2": 500, "3": 700}
        max_length = length_map.get(choice, 500)

        # ── Background music ──
        music_playing = music_menu(category)

        # ── Generate base story ──
        if language == "hindi":
            base_story = generate_hindi_story(
                smart_prompt, hindi_tok, hindi_model,
                hindi_device, max_length
            )
        else:
            base_story = generate_english_story(
                smart_prompt, eng_tok, eng_model,
                eng_device, max_length
            )

        # ── Build complete story with tension + twist ──
        complete_story = build_complete_story(base_story, language, category)

        # ── Stop music ──
        if music_playing:
            stop_background_music()

        # ── Display story ──
        display_story(user_input, complete_story, language, category)

        # ── Text to speech ──
        multivoice_menu(complete_story, language, story_id=str(id(complete_story)))

        # ── Rate story ──
        print("⭐ Rate this story (1-5) or press Enter to skip:")
        rating_input = input("   Rating: ").strip()
        rating = int(rating_input) if rating_input.isdigit() and 1 <= int(rating_input) <= 5 else None

        # ── Save to library ──
        print("💾 Save to library? (y/n): ", end="")
        save = input().strip().lower()
        if save == "y":
            story_id = add_story(
                prompt   = user_input,
                story    = complete_story,
                language = language,
                category = category,
                rating   = rating
            )
            if rating:
                rate_story(story_id, rating)

        print()


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n🚀 Loading Advanced Horror Story Generator...\n")

    # Load both models
    hindi_tok,  hindi_model,  hindi_device  = load_hindi_model()
    eng_tok,    eng_model,    eng_device    = load_english_model()

    # Check at least one model available
    if hindi_model is None and eng_model is None:
        print("❌ No models found!")
        print("   Hindi  : python backend/model/train.py")
        print("   English: python backend/model/train_english.py")
        return

    # Run
    interactive_mode(
        hindi_tok, hindi_model, hindi_device,
        eng_tok,   eng_model,   eng_device
    )


if __name__ == "__main__":
    main()