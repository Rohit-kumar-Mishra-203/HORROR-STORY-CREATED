import os
import re
import time
import random
from pydub import AudioSegment
from pydub.effects import speedup
from gtts import gTTS

os.environ["PATH"]     += os.pathsep + r"C:\ffmpeg\bin"
AudioSegment.converter  = r"C:\ffmpeg\bin\ffmpeg.exe"  # type: ignore
AudioSegment.ffprobe    = r"C:\ffmpeg\bin\ffprobe.exe"  # type: ignore

# ─────────────────────────────────────────
# CONFIG — DAAR STYLE
# ─────────────────────────────────────────
AUDIO_DIR  = "audio_output"
SOUNDS_DIR = "backend/features/horror_sounds"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Volume settings (dB)
NARRATOR_VOLUME     =  2     # narrator boost
BG_MUSIC_VOLUME     = -18    # background music — very low
SOUND_EFFECT_VOLUME =  6     # sound effects — audible but not jarring
CLIMAX_BG_VOLUME    = -12    # bg music louder at climax

# Pause durations (milliseconds)
PAUSE_BETWEEN_SENTENCES = 600    # 0.6s between sentences
PAUSE_BETWEEN_PARAS     = 1400   # 1.4s between paragraphs
PAUSE_BEFORE_SOUND      = 300    # brief pause before sound effect
PAUSE_AFTER_SOUND       = 500    # brief pause after sound effect
PAUSE_AT_CLIMAX         = 2000   # 2s dramatic pause at climax

# Narration speed
NARRATOR_SPEED = 0.92   # slightly slower than normal for drama


# ─────────────────────────────────────────
# SENTENCE SPLITTER
# splits story into individual sentences
# ─────────────────────────────────────────
def split_into_sentences(text, language):
    # Remove sound cue markers first
    text = re.sub(r'\*[^*]+\*', '', text)
    text = re.sub(r'\[[^\]]+\]', '', text)
    text = text.strip()

    if language == "hindi":
        # Split on Hindi punctuation
        sentences = re.split(r'[।!?]+', text)
    else:
        sentences = re.split(r'[.!?]+', text)

    cleaned = []
    for s in sentences:
        s = s.strip()
        if len(s.split()) >= 3:
            cleaned.append(s)
    return cleaned


# ─────────────────────────────────────────
# SPLIT INTO PARAGRAPHS
# ─────────────────────────────────────────
def split_into_paragraphs(text):
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paras


# ─────────────────────────────────────────
# DETECT STORY SECTION
# intro / rising / climax / outro
# ─────────────────────────────────────────
def detect_section(para_index, total_paras):
    ratio = para_index / max(total_paras, 1)
    if ratio < 0.2:
        return "intro"
    elif ratio < 0.6:
        return "rising"
    elif ratio < 0.85:
        return "climax"
    else:
        return "outro"


# ─────────────────────────────────────────
# LOAD BACKGROUND MUSIC
# ─────────────────────────────────────────
def load_background_music(category):
    # Category → best background music file
    category_music = {
        "ghost"         : ["ghost_whisper.mp3", "heartbeat.mp3"],
        "witch"         : ["fire_crackling.mp3", "owl_hooting.mp3"],
        "haunted_house" : ["wind_howling.mp3", "door_creaking.mp3"],
        "graveyard"     : ["crow_cawing.mp3", "owl_hooting.mp3"],
        "demon"         : ["chains_rattling.mp3", "heartbeat.mp3"],
        "vampire"       : ["heartbeat.mp3", "wolf_howling.mp3"],
        "monster"       : ["wolf_howling.mp3", "screaming_distance.mp3"],
        "cursed_object" : ["clock_ticking.mp3", "water_dripping.mp3"],
        "possessed"     : ["heartbeat.mp3", "ghost_whisper.mp3"],
        "general_horror": ["rain_pouring.mp3", "wind_howling.mp3"],
    }

    preferred = category_music.get(category, ["rain_pouring.mp3"])

    for filename in preferred:
        filepath = os.path.join(SOUNDS_DIR, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            try:
                music = AudioSegment.from_file(filepath)
                return music
            except:
                continue
    return None


# ─────────────────────────────────────────
# LOAD SOUND EFFECT
# ─────────────────────────────────────────
def load_sound_effect(sound_name):
    filepath = os.path.join(SOUNDS_DIR, f"{sound_name}.mp3")
    if not os.path.exists(filepath):
        return None
    if os.path.getsize(filepath) < 100:
        return None
    try:
        sound = AudioSegment.from_file(filepath)
        return sound
    except:
        return None


# ─────────────────────────────────────────
# CATEGORY → SOUND EFFECTS MAP
# which sounds play for which category
# ─────────────────────────────────────────
CATEGORY_SOUNDS = {
    "ghost"         : ["ghost_whisper", "chains_rattling", "door_creaking", "footsteps", "heartbeat"],
    "witch"         : ["owl_hooting", "crow_cawing", "fire_crackling", "evil_laugh", "thunder"],
    "haunted_house" : ["door_creaking", "glass_breaking", "footsteps", "chains_rattling", "wind_howling"],
    "graveyard"     : ["owl_hooting", "crow_cawing", "church_bell", "chains_rattling", "wolf_howling"],
    "demon"         : ["evil_laugh", "chains_rattling", "screaming_distance", "thunder", "heartbeat"],
    "vampire"       : ["heartbeat", "wolf_howling", "door_creaking", "crow_cawing", "footsteps"],
    "monster"       : ["wolf_howling", "screaming_distance", "dog_barking", "thunder", "footsteps"],
    "cursed_object" : ["glass_breaking", "clock_ticking", "ghost_whisper", "water_dripping", "chains_rattling"],
    "possessed"     : ["evil_laugh", "screaming_distance", "heartbeat", "ghost_whisper", "chains_rattling"],
    "general_horror": ["thunder", "wind_howling", "heartbeat", "door_creaking", "owl_hooting"],
}

# ─────────────────────────────────────────
# KEYWORD → SOUND TRIGGER
# ─────────────────────────────────────────
KEYWORD_SOUNDS = {
    "english": {
        "door"      : "door_creaking",
        "footstep"  : "footsteps",
        "scream"    : "screaming_distance",
        "laugh"     : "evil_laugh",
        "whisper"   : "ghost_whisper",
        "heart"     : "heartbeat",
        "chain"     : "chains_rattling",
        "glass"     : "glass_breaking",
        "thunder"   : "thunder",
        "rain"      : "rain_pouring",
        "wolf"      : "wolf_howling",
        "crow"      : "crow_cawing",
        "owl"       : "owl_hooting",
        "fire"      : "fire_crackling",
        "clock"     : "clock_ticking",
        "drip"      : "water_dripping",
        "knife"     : "knife_scraping",
        "dog"       : "dog_barking",
        "bell"      : "church_bell",
        "wind"      : "wind_howling",
    },
    "hindi": {
        "दरवाज़ा"    : "door_creaking",
        "कदम"       : "footsteps",
        "चीख"       : "screaming_distance",
        "हँसी"      : "evil_laugh",
        "फुसफुस"    : "ghost_whisper",
        "दिल"       : "heartbeat",
        "जंजीर"     : "chains_rattling",
        "शीशा"      : "glass_breaking",
        "बिजली"     : "thunder",
        "बारिश"     : "rain_pouring",
        "भेड़िया"   : "wolf_howling",
        "कौआ"       : "crow_cawing",
        "उल्लू"     : "owl_hooting",
        "आग"        : "fire_crackling",
        "घड़ी"      : "clock_ticking",
        "पानी"      : "water_dripping",
        "चाकू"      : "knife_scraping",
        "कुत्ता"    : "dog_barking",
        "घंटी"      : "church_bell",
        "हवा"       : "wind_howling",
    }
}


# ─────────────────────────────────────────
# GENERATE NARRATOR AUDIO FOR ONE SENTENCE
# ─────────────────────────────────────────
def generate_sentence_audio(sentence, language, temp_path):
    if not sentence.strip():
        return None

    lang_code = "hi" if language == "hindi" else "en"
    tld       = "co.in" if language == "hindi" else "co.uk"

    try:
        tts = gTTS(
            text = sentence,
            lang = lang_code,
            tld  = tld,
            slow = False
        )
        tts.save(temp_path)

        audio = AudioSegment.from_mp3(temp_path)

        # Slow down slightly for dramatic effect
        if NARRATOR_SPEED != 1.0:
            new_rate = int(audio.frame_rate * NARRATOR_SPEED)
            audio    = audio._spawn(
                audio.raw_data,
                overrides={"frame_rate": new_rate}
            )
            audio = audio.set_frame_rate(44100)

        # Boost narrator volume
        audio = audio + NARRATOR_VOLUME
        return audio

    except Exception as e:
        print(f"    ⚠️  TTS failed: {e}")
        return None


# ─────────────────────────────────────────
# DETECT SOUND FOR SENTENCE
# ─────────────────────────────────────────
def detect_sound_for_sentence(sentence, language, category, section):
    sentence_lower = sentence.lower()
    keywords       = KEYWORD_SOUNDS.get(language, KEYWORD_SOUNDS["english"])

    # Check keyword triggers first
    for keyword, sound_name in keywords.items():
        if keyword.lower() in sentence_lower:
            return sound_name

    # Use category sound based on section
    cat_sounds = CATEGORY_SOUNDS.get(category, CATEGORY_SOUNDS["general_horror"])
    if not cat_sounds:
        return None

    # Play sound every 3-4 sentences based on section
    if section == "climax":
        # More frequent sounds at climax
        return random.choice(cat_sounds)
    elif section == "intro":
        # Fewer sounds at intro
        return cat_sounds[0] if random.random() > 0.7 else None
    else:
        # Medium frequency
        return random.choice(cat_sounds) if random.random() > 0.5 else None


# ─────────────────────────────────────────
# CREATE SILENCE
# ─────────────────────────────────────────
def silence(ms):
    return AudioSegment.silent(duration=int(ms))


# ─────────────────────────────────────────
# EXTEND BACKGROUND MUSIC TO LENGTH
# ─────────────────────────────────────────
def extend_music(music, target_ms):
    if music is None:
        return None
    while len(music) < target_ms:
        music = music + music
    return music[:target_ms]


# ─────────────────────────────────────────
# MAIN PRODUCER — DAAR STYLE
# ─────────────────────────────────────────
def produce_horror_audio(
    story_text, language, category,
    story_id="latest", output_path=None
):
    random.seed(time.time_ns())

    print("\n" + "="*60)
    print("🎙️  PRODUCING HORROR AUDIO — DAAR STYLE")
    print(f"   Language : {language}")
    print(f"   Category : {category}")
    print("="*60 + "\n")

    if output_path is None:
        output_path = os.path.join(
            AUDIO_DIR, f"story_{story_id}_horror.mp3"
        )

    # Split story into paragraphs
    paragraphs  = split_into_paragraphs(story_text)
    total_paras = len(paragraphs)

    print(f"  📖 Paragraphs    : {total_paras}")

    # ── Build narration track ──
    print("  🎙️  Building narration...\n")

    narration   = AudioSegment.empty()
    sound_timeline = []   # [(position_ms, sound_name)]
    current_ms  = 0

    for para_idx, paragraph in enumerate(paragraphs):
        section   = detect_section(para_idx, total_paras)
        sentences = split_into_sentences(paragraph, language)

        if not sentences:
            continue

        print(f"  📝 Para {para_idx+1}/{total_paras} [{section}] — {len(sentences)} sentences")

        for sent_idx, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            # Generate sentence audio
            temp_path = os.path.join(AUDIO_DIR, f"temp_sent_{para_idx}_{sent_idx}.mp3")
            sent_audio = generate_sentence_audio(sentence, language, temp_path)

            if sent_audio is None:
                continue

            # Detect sound for this sentence
            sound_name = detect_sound_for_sentence(
                sentence, language, category, section
            )

            # Add sound BEFORE sentence if triggered
            if sound_name:
                sound_effect = load_sound_effect(sound_name)
                if sound_effect:
                    # Trim sound to 2-3 seconds
                    sound_effect = sound_effect[:2500]
                    sound_effect = sound_effect.fade_in(100).fade_out(200)
                    sound_effect = sound_effect + SOUND_EFFECT_VOLUME

                    # Brief pause → sound → pause → sentence
                    narration   += silence(PAUSE_BEFORE_SOUND)
                    narration   += sound_effect
                    narration   += silence(PAUSE_AFTER_SOUND)
                    current_ms  += PAUSE_BEFORE_SOUND + len(sound_effect) + PAUSE_AFTER_SOUND
                    print(f"    🔊 [{sound_name}]")

            # Add sentence audio
            narration  += sent_audio
            current_ms += len(sent_audio)

            # Pause between sentences
            if sent_idx < len(sentences) - 1:
                # Longer pause at sentence end
                pause_ms   = PAUSE_BETWEEN_SENTENCES
                if section == "climax":
                    pause_ms = int(pause_ms * 1.5)
                narration  += silence(pause_ms)
                current_ms += pause_ms

            # Cleanup temp
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Longer pause between paragraphs
        para_pause = PAUSE_BETWEEN_PARAS
        if section == "climax":
            para_pause = PAUSE_AT_CLIMAX
        narration  += silence(para_pause)
        current_ms += para_pause

    total_duration = len(narration)
    print(f"\n  ✅ Narration built : {total_duration/1000:.1f}s")

    # ── Add background music ──
    print("  🎵 Adding background music...")

    bg_music = load_background_music(category)
    final_audio = narration
    if bg_music is not None:
        try:
            # Extend music to full story length
            bg_music = extend_music(bg_music, total_duration)
        
            if bg_music is None:
                # Lower background music volume
                bg_music = bg_music + BG_MUSIC_VOLUME # type: ignore

                # Fade in at start and fade out at end
                fade_dur = min(3000, total_duration // 10)
                bg_music = bg_music.fade_in(fade_dur).fade_out(fade_dur)

                # Mix narration over background music
                # Narration is louder so it stays clear
                final_audio = bg_music.overlay(narration)
                print("  ✅ Background music mixed")
            else:
                print("could not extend music") 
        except Exception as e:
            print(f" music mixing failed: {e}")
            final_audio = narration
    else:
        print("  ⚠️  No background music file found")
        print(f"     Add .mp3 files to {SOUNDS_DIR}/")

    # ── Export final audio ──
    print(f"\n  💾 Exporting to {output_path}...")
    final_audio.export(output_path, format="mp3", bitrate="128k")

    size_kb  = os.path.getsize(output_path) / 1024
    duration = len(final_audio) / 1000

    print(f"\n" + "="*60)
    print(f"  ✅ HORROR AUDIO COMPLETE!")
    print(f"  Duration  : {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"  Size      : {size_kb:.1f} KB")
    print(f"  File      : {output_path}")
    print("="*60 + "\n")

    return output_path


# ─────────────────────────────────────────
# MENU
# ─────────────────────────────────────────
def horror_audio_menu(story_text, language, category, story_id="latest"):
    print("\n" + "="*60)
    print("🎙️  AUDIO OPTIONS")
    print("="*60)
    print("  1. Generate DAAR-style horror audio")
    print("  2. Skip audio")
    print("="*60)

    choice = input("\n  Choose (1/2): ").strip()

    if choice == "1":
        output_path = os.path.join(
            AUDIO_DIR, f"story_{story_id}_horror.mp3"
        )
        filepath = produce_horror_audio(
            story_text, language, category,
            story_id, output_path
        )
        if filepath:
            play = input("  ▶️  Play now? (y/n): ").strip().lower()
            if play == "y":
                play_audio(filepath)
        return filepath
    else:
        print("  ⏭️  Skipping audio\n")
        return None


# ─────────────────────────────────────────
# PLAY AUDIO
# ─────────────────────────────────────────
def play_audio(filepath):
    if not filepath or not os.path.exists(filepath):
        print("  ❌ File not found")
        return
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        print("  ▶️  Playing... Press Ctrl+C to stop\n")
        import time as t
        while pygame.mixer.music.get_busy():
            t.sleep(0.5)
        pygame.mixer.quit()
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("\n  ⏹️  Stopped\n")
    except Exception as e:
        print(f"  ❌ Playback error: {e}")


# ─────────────────────────────────────────
# MAIN — for testing
# ─────────────────────────────────────────
if __name__ == "__main__":
    test_story = """रात के अंधेरे में राहुल उस पुरानी हवेली के पास पहुँचा।

दरवाज़ा अपने आप खुल गया। अंदर से ठंडी हवा आई।

कहीं से कदमों की आवाज़ आई। धीमी। भारी। ऊपर से।

राहुल ने चीखना चाहा। पर आवाज़ नहीं निकली।

और फिर। अँधेरे में। एक चेहरा दिखा।

वो चेहरा राहुल का अपना था।"""

    produce_horror_audio(test_story, "hindi", "haunted_house", "test")