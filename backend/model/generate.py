import os
import sys
import torch
from transformers import (AutoTokenizer, AutoModelForSeq2SeqLM, GPT2LMHeadModel, GPT2Tokenizer)

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
))

from backend.model.config            import *
from backend.model.prompt_engine     import process_user_input
from backend.model.story_builder     import build_story_prompt
from backend.model.tension_engine    import get_tension_suffix
from backend.model.twist_generator   import get_twist, format_twist
from backend.features.story_library  import init_library, add_story, rate_story
from backend.features.multi_voice_tts import multivoice_menu
from backend.features.music_player   import music_menu, stop_background_music
from backend.features.voice_manager  import check_voices, voice_upload_menu
from backend.features.story_saver    import save_complete_story


# LOAD HINDI MODEL
def load_hindi_model():
    print("\n Loading Hindi model (IndicBART)...")

    if not os.path.exists(SAVED_MODEL_DIR):
        print(f" Hindi model not found at '{SAVED_MODEL_DIR}/'")
        print("   Run: python backend/model/train.py first")
        return None, None, None  # type: ignore

    tokenizer = AutoTokenizer.from_pretrained(
        SAVED_MODEL_DIR,
        use_fast=False,
        keep_accents=True,
    )

    model: AutoModelForSeq2SeqLM = AutoModelForSeq2SeqLM.from_pretrained(SAVED_MODEL_DIR, torch_dtype=torch.float16)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)   # type: ignore
    model.eval()       # type: ignore

    print(f" Hindi model loaded on: {device}\n")
    return tokenizer, model, device  # type: ignore


# LOAD ENGLISH MODEL
def load_english_model():
    print("\n Loading English model (GPT-2)...")

    english_model_dir = "saved_model_english"

    if not os.path.exists(english_model_dir):
        print(f" English model not found at'{english_model_dir}/'")
        print("   Run: python backend/model/train_english.py first")
        return None, None, None  # type: ignore

    tokenizer           = GPT2Tokenizer.from_pretrained(english_model_dir)
    tokenizer.pad_token = tokenizer.eos_token

    model: GPT2LMHeadModel = GPT2LMHeadModel.from_pretrained(english_model_dir, torch_dtype=torch.float16) # type: ignore

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)   # type: ignore
    model.eval()       # type: ignore

    print(f" English model loaded on: {device}\n")
    return tokenizer, model, device  # type: ignore

# GENERATE HINDI STORY
def generate_hindi_story(prompt, tokenizer, model, device,
                          max_length=700, category="general_horror"):
    print("  Generating Hindi horror story...\n")

    import random
    from backend.model.story_templates.templates_loader import get_template

    # Get quality template for category
    base_story = get_template("hindi", category)
    print(f"   Template selected for category: {category}\n")

    # Try model extension
    try:
        last_part = base_story[-100:]
        extension_prompt = f"<s> <2hi> {last_part}"
        inputs = tokenizer(
            extension_prompt,
            return_tensors = "pt",
            max_length     = MAX_SOURCE_LENGTH,
            truncation     = True,
            padding        = True,
        ).to(device)

        try:
            forced_bos_token_id = tokenizer.convert_tokens_to_ids("<2hi>")
            if forced_bos_token_id == tokenizer.unk_token_id:
                forced_bos_token_id = None
        except:
            forced_bos_token_id = None

        with torch.no_grad():
            outputs = model.generate(   # type: ignore
                input_ids            = inputs["input_ids"],
                attention_mask       = inputs["attention_mask"],
                max_length           = 200,
                min_length           = 30,
                do_sample            = True,
                temperature          = 0.7,
                top_k                = 40,
                top_p                = 0.85,
                repetition_penalty   = 3.0,
                no_repeat_ngram_size = 4,
                forced_bos_token_id  = forced_bos_token_id,
            )

        extension = tokenizer.decode(
            outputs[0],
            skip_special_tokens          = True,
            clean_up_tokenization_spaces = True
        )
        extension   = clean_generated_story(extension, "hindi")
        hindi_chars = sum(1 for c in extension if 0x0900 <= ord(c) <= 0x097F)
        total_chars = len(extension.replace(' ', ''))

        if total_chars > 0 and hindi_chars / total_chars > 0.7 and len(extension.split()) > 15:
            base_story = base_story + "\n\n" + extension

    except Exception as e:
        print(f"    Extension skipped: {e}")

    return base_story
    
    

# CLEAN GENERATED STORY
def clean_generated_story(text, language):
    import re

    if language == "hindi":
        cleaned_lines = []
        for line in text.split('\n'):
            cleaned_chars = []
            for ch in line:
                cp = ord(ch)
                if (
                    0x0900 <= cp <= 0x097F or
                    0x0964 <= cp <= 0x0965 or
                    ch in ' .,!?;:\'"()-'
                ):
                    cleaned_chars.append(ch)
                else:
                    cleaned_chars.append(' ')
            cleaned_line = ''.join(cleaned_chars).strip()
            # Only keep lines with actual Hindi words
            hindi_words = [
                c for c in cleaned_line
                if 0x0900 <= ord(c) <= 0x097F
            ]
            if len(hindi_words) > 5:
                cleaned_lines.append(cleaned_line)
        text = '\n'.join(cleaned_lines)

    elif language == "english":
        cleaned_lines = []
        for line in text.split('\n'):
            cleaned_chars = []
            for ch in line:
                cp = ord(ch)
                if (
                    0x0041 <= cp <= 0x005A or
                    0x0061 <= cp <= 0x007A or
                    ch in ' .,!?;:\'"()-'
                ):
                    cleaned_chars.append(ch)
                else:
                    cleaned_chars.append(' ')
            cleaned_line = ''.join(cleaned_chars).strip()
            # Only keep lines with actual English words
            eng_words = re.findall(r'[a-zA-Z]{3,}', cleaned_line)
            if len(eng_words) > 3:
                cleaned_lines.append(cleaned_line)
        text = '\n'.join(cleaned_lines)

    # Remove repeated sentences
    text = remove_repeated_sentences(text, language)

    # Clean spaces
    text = re.sub(r'[ \t]+',  ' ',   text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def remove_repeated_sentences(text, language="english"):
    import re

    # Split by sentence endings
    if language == "hindi":
        parts = re.split(r'[।!?]+', text)
        joiner = '। '
    else:
        parts  = re.split(r'[.!?]+', text)
        joiner = '. '

    seen   = set()
    result = []

    for part in parts:
        cleaned = part.strip().lower()
        cleaned = re.sub(r'\s+', ' ', cleaned)

        if not cleaned or len(cleaned) < 8:
            continue

        # Check if very similar to already seen sentence
        is_duplicate = False
        for seen_sent in seen:
            # If 80% of words match → duplicate
            words1 = set(cleaned.split())
            words2 = set(seen_sent.split())
            if len(words1) > 0:
                overlap = len(words1 & words2) / len(words1)
                if overlap > 0.8:
                    is_duplicate = True
                    break

        if not is_duplicate:
            seen.add(cleaned)
            result.append(part.strip())

    return joiner.join(result)


# GENERATE ENGLISH STORY
def generate_english_story(prompt, tokenizer, model, device,
                             max_length=700, category="general_horror"):
    print("  Generating English horror story...\n")

    import random
    from backend.model.story_templates.templates_loader import get_template

    # Get quality template for category
    base_story = get_template("english", category)
    print(f"   Template selected for category: {category}\n")

    # Try model extension
    try:
        last_part = base_story[-200:]
        inputs    = tokenizer(
            last_part,
            return_tensors = "pt",
            truncation     = True,
            max_length     = 300,
            padding        = True
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(   # type: ignore
                input_ids            = inputs["input_ids"],
                attention_mask       = inputs["attention_mask"],
                max_length           = 350,
                min_length           = 30,
                do_sample            = True,
                temperature          = 0.75,
                top_k                = 40,
                top_p                = 0.88,
                repetition_penalty   = 2.5,
                no_repeat_ngram_size = 4,
                pad_token_id         = tokenizer.eos_token_id,
            )

        extension = tokenizer.decode(
            outputs[0],
            skip_special_tokens          = True,
            clean_up_tokenization_spaces = True
        )
        extension = clean_generated_story(extension, "english")
        eng_words = len([w for w in extension.split() if w.isalpha() and ord(w[0]) < 128])

        if eng_words > 20:
            base_story = base_story + "\n\n" + extension

    except Exception as e:
        print(f"    Extension skipped: {e}")

    return base_story


# BUILD COMPLETE STORY
# base story + tension + twist
def build_complete_story(base_story, language, category):
    import random
    import time
    from backend.features.sound_inserter import insert_sound_cues
    random.seed(time.time_ns())

    # add sound cues to story text
    story_with_sounds = insert_sound_cues(base_story, language, category)

    tension = get_tension_suffix(language, intensity="high")
    twist   = get_twist(language, category)
    twist   = format_twist(twist, language)
    return f"{story_with_sounds}\n\n{tension}\n{twist}"

# DISPLAY STORY
def display_story(prompt, story, language, category):
    flag         = "🇮🇳" if language == "hindi" else "🇬🇧"
    category_str = category.replace("_", " ").title()

    print("\n" + "="*60)
    print(f" {flag} {category_str.upper()} HORROR STORY")
    print("="*60)
    print(f" Prompt : {prompt}")
    print("-"*60)
    print(f"\n{story}\n")
    print("="*60)


# INTERACTIVE MODE
def interactive_mode(
    hindi_tok, hindi_model, hindi_device,
    eng_tok,   eng_model,   eng_device
):
    # Initialize library
    init_library()

    # Story counter for IDs
    story_counter = [0]

    print("\n" + "="*60)
    print(" ADVANCED HORROR STORY GENERATOR")
    print("   Hindi 🇮🇳  |  English 🇬🇧")
    print("="*60)
    print("   Type your story request naturally!")
    print()
    print("   Examples:")
    print("   → 'give me a witch story'")
    print("   → 'एक चुड़ैल की कहानी सुनाओ'")
    print("   → 'write a vampire horror story'")
    print("   → 'भूतिया हवेली की कहानी बताओ'")
    print()
    print("   Commands:")
    print("   → 'voices'  — manage your voice profiles")
    print("   → 'library' — manage saved stories")
    print("   → 'exit'    — quit")
    print("="*60 + "\n")

    while True:
        print("-"*60)
        user_input = input(" What story do you want? : ").strip()

        #Commands
        if user_input.lower() == "exit":
            print("\n Goodbye! Stay scared! \n")
            break

        if user_input.lower() == "library":
            from backend.features.story_library import library_menu
            library_menu()
            continue

        if user_input.lower() == "voices":
            check_voices()
            voice_upload_menu()
            continue

        if len(user_input) < 3:
            print("  Please type something!\n")
            continue

        #Detect category from prompt
        prompt, detected_language, category = process_user_input(user_input)

        #Always ask user which language
        print("\n In which language do you want the story?")
        print("   1. Hindi 🇮🇳")
        print("   2. English 🇬🇧")
        lang_choice = input("   Choose (1/2): ").strip()

        if lang_choice == "1":
            language = "hindi"
        elif lang_choice == "2":
            language = "english"
        else:
            # fallback to detected language
            language = detected_language
            print(f"   Invalid choice — using detected: {language}")

        #Check model available
        if language == "hindi" and hindi_model is None:
            print(" Hindi model not loaded!")
            print("   Run: python backend/model/train.py\n")
            continue

        if language == "english" and eng_model is None:
            print(" English model not loaded!")
            print("   Run: python backend/model/train_english.py\n")
            continue

        # Build smart story prompt in chosen language
        smart_prompt, character, category = build_story_prompt(language, category)
        lang_flag = "🇮🇳 Hindi" if language == "hindi" else "🇬🇧 English"
        print(f"\n Generating in  : {lang_flag}")
        print(f" Main Character : {character}")

        # Story length
        print("\n Story length:")
        print("   1. Short  (~200 words)")
        print("   2. Medium (~400 words) — recommended")
        print("   3. Long   (~600 words)")
        choice     = input("   Choose (1/2/3): ").strip()
        length_map = {"1": 300, "2": 500, "3": 700}
        max_length = length_map.get(choice, 500)

        # Background music
        music_playing = music_menu(category)

        # Generate story
        if language == "hindi":
            base_story = generate_hindi_story(
                user_input, hindi_tok,
                hindi_model, hindi_device,
                max_length, category        # ← pass category
            )
        else:
            base_story = generate_english_story(
                user_input, eng_tok,
                eng_model, eng_device,
                max_length, category        # ← pass category
            )

        # Add tension + twist
        complete_story = build_complete_story(base_story, language, category)

        #  Stop music 
        if music_playing:
            stop_background_music()

        #  Display story 
        display_story(user_input, complete_story, language, category)

        #  Generate story ID 
        story_counter[0] += 1
        story_id = f"{story_counter[0]:03d}"

        #  Multi voice audio with horror sounds
        from backend.features.horror_audio_producer import horror_audio_menu
        generated_audio = horror_audio_menu(
            complete_story, language, story_id, category
        )

        #  Rate story 
        print(" Rate this story (1-5) or press Enter to skip:")
        rating_input = input("   Rating: ").strip()
        rating = (
            int(rating_input)
            if rating_input.isdigit() and 1 <= int(rating_input) <= 5
            else None
        )

        #  Save everything 
        print("\n Save story? (y/n): ", end="")
        save = input().strip().lower()

        if save == "y":
            # Save txt + pdf + mp3 in one folder
            folder_path, saved_files = save_complete_story(
                story_text = complete_story,
                prompt     = user_input,
                language   = language,
                category   = category,
                audio_path = generated_audio,
                story_id   = story_id
            )

            # Also save to library
            lib_id = add_story(
                prompt   = user_input,
                story    = complete_story,
                language = language,
                category = category,
                rating   = rating
            )

            if rating:
                rate_story(lib_id, rating)

            print(f" Everything saved in: {folder_path}")

        print()


# MAIN
def main():
    print("\n Starting Advanced Horror Story Generator...\n")

    # Show voice status
    print("  Checking voice profiles...")
    check_voices()

    # Load models
    hindi_tok,  hindi_model,  hindi_device  = load_hindi_model()
    eng_tok,    eng_model,    eng_device    = load_english_model()

    # Check at least one model loaded
    if hindi_model is None and eng_model is None:
        print(" No models found!")
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