import os
import sys
import time
import threading

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
TTS_OUTPUT_DIR = "tts_output"
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────
# CHECK DEPENDENCIES
# ─────────────────────────────────────────
def check_dependencies():
    try:
        from gtts import gTTS
        import pygame
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install gtts==2.5.1 pygame==2.5.2")
        return False


# ─────────────────────────────────────────
# CONVERT TEXT TO SPEECH
# ─────────────────────────────────────────
def text_to_speech(text, language, story_id=None, slow=False):
    if not check_dependencies():
        return None

    from gtts import gTTS

    # Map language to gTTS language code
    lang_code = "hi" if language == "hindi" else "en"

    # Clean text for TTS
    clean_text = text.replace("<s>", "").replace("</s>", "")
    clean_text = clean_text.replace("<2hi>", "").strip()

    # Filename
    filename = f"story_{story_id}.mp3" if story_id else "story_latest.mp3"
    filepath = os.path.join(TTS_OUTPUT_DIR, filename)

    print(f"\n🎙️  Converting story to speech...")
    print(f"   Language : {'Hindi 🇮🇳' if language == 'hindi' else 'English 🇬🇧'}")
    print(f"   Words    : {len(clean_text.split())}")

    try:
        tts = gTTS(
            text     = clean_text,
            lang     = lang_code,
            slow     = slow,
            tld      = "co.in" if language == "hindi" else "com"
        )
        tts.save(filepath)
        print(f"✅ Audio saved → {filepath}\n")
        return filepath

    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None


# ─────────────────────────────────────────
# PLAY AUDIO
# ─────────────────────────────────────────
def play_audio(filepath):
    if not filepath or not os.path.exists(filepath):
        print("❌ Audio file not found")
        return

    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        print("▶️  Playing story audio...")
        print("   Press Enter to stop\n")

        # Play until done or user stops
        input_thread = threading.Thread(target=input, args=("",))
        input_thread.daemon = True
        input_thread.start()

        while pygame.mixer.music.get_busy():
            if not input_thread.is_alive():
                break
            time.sleep(0.5)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("⏹️  Audio stopped\n")

    except Exception as e:
        print(f"❌ Playback error: {e}")


# ─────────────────────────────────────────
# PLAY STORY WITH CHUNKS
# splits long stories into chunks for
# smoother TTS experience
# ─────────────────────────────────────────
def play_story_chunked(text, language, story_id=None):
    if not check_dependencies():
        return

    from gtts import gTTS
    import pygame

    lang_code  = "hi" if language == "hindi" else "en"
    clean_text = text.replace("<s>", "").replace("</s>", "")
    clean_text = clean_text.replace("<2hi>", "").strip()

    # Split into paragraphs
    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]

    if not paragraphs:
        paragraphs = [clean_text]

    print(f"\n🎙️  Preparing audio for {len(paragraphs)} paragraphs...")

    pygame.mixer.init()
    chunk_files = []

    # Generate audio for each paragraph
    for i, para in enumerate(paragraphs):
        if len(para.split()) < 3:
            continue

        chunk_file = os.path.join(TTS_OUTPUT_DIR, f"chunk_{story_id or 'latest'}_{i}.mp3")

        try:
            tts = gTTS(text=para, lang=lang_code, tld="co.in" if language == "hindi" else "com")
            tts.save(chunk_file)
            chunk_files.append(chunk_file)
        except Exception as e:
            print(f"⚠️  Chunk {i} failed: {e}")
            continue

    if not chunk_files:
        print("❌ No audio chunks generated")
        return

    print(f"✅ Generated {len(chunk_files)} audio chunks")
    print("▶️  Playing story... Press Ctrl+C to stop\n")

    try:
        for i, chunk_file in enumerate(chunk_files):
            print(f"   📢 Paragraph {i+1}/{len(chunk_files)}")
            pygame.mixer.music.load(chunk_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.3)

            time.sleep(0.5)   # pause between paragraphs

    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        print("\n⏹️  Stopped by user\n")

    finally:
        pygame.mixer.quit()
        # Cleanup chunk files
        for f in chunk_files:
            try:
                os.remove(f)
            except:
                pass


# ─────────────────────────────────────────
# SAVE AUDIO ONLY (no playback)
# ─────────────────────────────────────────
def save_audio_only(text, language, story_id):
    filepath = text_to_speech(text, language, story_id)
    if filepath:
        print(f"💾 Audio file saved: {filepath}")
        print(f"   You can play it with any media player\n")
    return filepath


# ─────────────────────────────────────────
# TTS MENU
# ─────────────────────────────────────────
def tts_menu(story_text, language, story_id=None):
    print("\n" + "="*60)
    print("🎙️  TEXT TO SPEECH OPTIONS")
    print("="*60)
    print("  1. Play story aloud now")
    print("  2. Save as MP3 file only")
    print("  3. Skip")
    print("="*60)

    choice = input("\n  Choose option (1/2/3): ").strip()

    if choice == "1":
        play_story_chunked(story_text, language, story_id)

    elif choice == "2":
        save_audio_only(story_text, language, story_id)

    elif choice == "3":
        print("⏭️  Skipping audio\n")


# ─────────────────────────────────────────
# MAIN — for testing
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n🎙️  Testing TTS Engine\n")

    test_hindi = "रात के अंधेरे में जब सारा गाँव सो गया था तब राम को उस पुरानी हवेली से अजीब आवाज़ें सुनाई दीं।"
    test_english = "It was past midnight when Daniel heard the first knock. He had been living alone for months."

    print("Testing Hindi TTS...")
    filepath = text_to_speech(test_hindi, "hindi", story_id="test")
    if filepath:
        play_audio(filepath)

    print("Testing English TTS...")
    filepath = text_to_speech(test_english, "english", story_id="test_eng")
    if filepath:
        play_audio(filepath)