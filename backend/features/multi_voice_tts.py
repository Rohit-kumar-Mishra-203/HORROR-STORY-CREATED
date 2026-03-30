import os
import re
import time
import numpy as np
from gtts import gTTS
from pydub import AudioSegment
#  Tell pydub where ffmpeg is
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"  # type: ignore
AudioSegment.ffmpeg    = r"C:\ffmpeg\bin\ffmpeg.exe"  # type: ignore

# Set ffprobe via pydub utils
from pydub.utils import which
import pydub.utils as pydub_utils
pydub_utils.get_prober_name = lambda: r"C:\ffmpeg\bin\ffprobe.exe"  # type: ignore
from pydub.effects import speedup
import pygame
from backend.features.sound_inserter import ( extract_sound_positions, get_sound_path, SOUND_LABELS)

# CONFIG

AUDIO_DIR = "audio_output"
os.makedirs(AUDIO_DIR, exist_ok=True)

# VOICE PROFILES (gTTS fallback settings)

VOICE_PROFILES = {
    "narrator_scary": {
        "speed"  : 1.35,
        "pitch"  : -4,
        "volume" : 3,
        "tld_en" : "co.uk",
        "tld_hi" : "co.in",
        "pause"  : 0.9
    },
    "old_person": {
        "speed"  : 1.35,
        "pitch"  : -2,
        "volume" : -2,
        "tld_en" : "com.au",
        "tld_hi" : "co.in",
        "pause"  : 0.9
    },
    "male_character": {
        "speed"  : 1.3,
        "pitch"  : -2,
        "volume" : 0,
        "tld_en" : "com",
        "tld_hi" : "co.in",
        "pause"  : 0.8
    },
    "female_character": {
        "speed"  : 1.0,
        "pitch"  : 2,
        "volume" : 0,
        "tld_en" : "co.uk",
        "tld_hi" : "co.in",
        "pause"  : 0.8
    },
    "ghost": {
        "speed"  : 0.8,
        "pitch"  : -6,
        "volume" : -4,
        "tld_en" : "co.uk",
        "tld_hi" : "co.in",
        "pause"  : 1.5
    }
}

# Voice slot mapping
SLOT_MAP = {
    "narrator_scary"   : "narrator",
    "old_person"       : "old_person",
    "male_character"   : "male_character",
    "female_character" : "female_character",
    "ghost"            : "ghost"
}

# PARSE STORY INTO SEGMENTS

def parse_story_segments(story_text, language):
    segments = []
    lines    = story_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        dialogue_pattern = r'["\u201c\u201d]([^"\u201c\u201d]+)["\u201c\u201d]'
        dialogues        = re.findall(dialogue_pattern, line)

        if dialogues:
            parts = re.split(dialogue_pattern, line)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if part in dialogues:
                    voice = detect_speaker_voice(line, part, language)
                    segments.append({
                        "text" : part,
                        "voice": voice,
                        "type" : "dialogue"
                    })
                else:
                    segments.append({
                        "text" : part,
                        "voice": "narrator_scary",
                        "type" : "narration"
                    })
        else:
            segments.append({
                "text" : line,
                "voice": "narrator_scary",
                "type" : "narration"
            })

    return segments

# DETECT SPEAKER VOICE

def detect_speaker_voice(full_line, dialogue, language):
    line_lower = full_line.lower()

    ghost_kw  = ["ghost","spirit","demon","shadow","whisper",
                 "भूत","आत्मा","राक्षस","साया","फुसफुसाया"]
    old_kw    = ["old","elder","grandma","grandpa","ancient",
                 "बूढ़ा","बूढ़ी","दादा","दादी","बुज़ुर्ग"]
    female_kw = ["she","her","woman","girl","lady","mother",
                 "औरत","लड़की","माँ","बहन","दादी"]

    if any(kw in line_lower for kw in ghost_kw):
        return "ghost"
    if any(kw in line_lower for kw in old_kw):
        return "old_person"
    if any(kw in line_lower for kw in female_kw):
        return "female_character"

    return "male_character"

# APPLY VOICE EFFECTS (gTTS fallback)

def apply_voice_effects(audio_segment, profile):
    speed = profile.get("speed", 1.0)
    if speed != 1.0:
        if speed > 1.0:
            audio_segment = speedup(audio_segment, playback_speed=speed)
        else:
            new_frame_rate = int(audio_segment.frame_rate * speed)
            audio_segment  = audio_segment._spawn(
                audio_segment.raw_data,
                overrides={"frame_rate": new_frame_rate}
            )
            audio_segment = audio_segment.set_frame_rate(44100)

    pitch = profile.get("pitch", 0)
    if pitch != 0:
        new_sample_rate = int(audio_segment.frame_rate * (2 ** (pitch / 12.0)))
        audio_segment   = audio_segment._spawn(
            audio_segment.raw_data,
            overrides={"frame_rate": new_sample_rate}
        )
        audio_segment = audio_segment.set_frame_rate(44100)

    volume = profile.get("volume", 0)
    if volume != 0:
        audio_segment = audio_segment + volume

    return audio_segment

# GENERATE SINGLE VOICE SEGMENT
# uses your uploaded voice OR gTTS fallback

def generate_voice_segment(text, voice_key, language, segment_index):
    if not text.strip():
        return None

    profile   = VOICE_PROFILES.get(voice_key, VOICE_PROFILES["narrator_scary"])
    lang_code = "hi" if language == "hindi" else "en"
    tld       = profile["tld_hi"] if language == "hindi" else profile["tld_en"]

    temp_file = os.path.join(AUDIO_DIR, f"temp_seg_{segment_index}.mp3")
    out_file  = os.path.join(AUDIO_DIR, f"seg_{segment_index}_{voice_key}.mp3")

    try:
        # ── Try user uploaded voice first ──
        from backend.features.voice_manager import get_voice_path
        slot       = SLOT_MAP.get(voice_key, "narrator")
        voice_path = get_voice_path(slot)

        if voice_path and os.path.exists(voice_path):
            # Generate gTTS for timing reference
            tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
            tts.save(temp_file)
            ref_audio    = AudioSegment.from_mp3(temp_file)
            target_ms    = len(ref_audio)

            # Load user voice
            ext = os.path.splitext(voice_path)[1].lower()
            if ext == ".wav":
                user_audio = AudioSegment.from_wav(voice_path)
            elif ext == ".mp3":
                user_audio = AudioSegment.from_mp3(voice_path)
            else:
                user_audio = AudioSegment.from_file(voice_path)

            # Loop user voice to match target duration
            while len(user_audio) < target_ms:
                user_audio = user_audio + user_audio
            user_audio = user_audio[:target_ms]

            # Apply effects on top of user voice
            user_audio = apply_voice_effects(user_audio, profile)
            user_audio.export(out_file, format="mp3")

            print(f"  [{voice_key}] Using YOUR voice → {text[:40]}...")

            if os.path.exists(temp_file):
                os.remove(temp_file)

        else:
            # ── Fallback to gTTS ──
            tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
            tts.save(temp_file)
            audio = AudioSegment.from_mp3(temp_file)
            audio = apply_voice_effects(audio, profile)
            audio.export(out_file, format="mp3")

            print(f"  [{voice_key}] Using gTTS → {text[:40]}...")

            if os.path.exists(temp_file):
                os.remove(temp_file)

        return out_file

    except Exception as e:
        print(f"    Segment {segment_index} failed: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return None

# ADD PAUSE

def create_pause(duration_ms=500):
    return AudioSegment.silent(duration=duration_ms)

# COMBINE ALL SEGMENTS

def combine_segments(segment_files):
    print("\n Combining all voice segments...")

    combined   = AudioSegment.empty()
    prev_voice = None

    for filepath, voice_key, seg_type in segment_files:
        if not filepath or not os.path.exists(filepath):
            continue

        audio   = AudioSegment.from_mp3(filepath)
        profile = VOICE_PROFILES.get(voice_key, VOICE_PROFILES["narrator_scary"])

        if seg_type == "dialogue":
            pause_ms  = int(profile["pause"] * 1200)
            combined += create_pause(pause_ms)
        elif prev_voice != voice_key:
            combined += create_pause(400)

        combined  += audio
        prev_voice = voice_key

    return combined

# ─────────────────────────────────────────
# MIX SOUNDS AT EXACT TEXT POSITIONS
# ─────────────────────────────────────────
def mix_sounds_at_positions(base_audio, story_with_cues, language):
    from pydub import AudioSegment as AS

    positions = extract_sound_positions(story_with_cues, language)

    if not positions:
        return base_audio

    total_chars  = max(1, len(story_with_cues))
    total_ms     = len(base_audio)
    mixed_audio  = base_audio

    print(f"\n🔊 Mixing {len(positions)} sounds at exact positions...")

    for pos_data in positions:
        sound_key = pos_data["sound"]
        char_pos  = pos_data["position"]
        label     = pos_data["label"]

        # Calculate time position proportionally
        time_ratio = char_pos / total_chars
        mix_pos_ms = int(time_ratio * total_ms)
        mix_pos_ms = max(0, min(mix_pos_ms, total_ms - 1000))

        # Load sound file
        sound_path = get_sound_path(sound_key)
        if not sound_path:
            print(f"  ⚠️  Sound missing: {sound_key}")
            continue

        try:
            sound = AS.from_file(sound_path)
            sound = sound[:3000]              # max 3 seconds
            sound = sound + 8                 # boost volume
            sound = sound.fade_in(100).fade_out(200)

            # Overlay sound at calculated position
            mixed_audio = mixed_audio.overlay(
                sound,
                position=mix_pos_ms
            )
            print(f"  🔊 Mixed [{sound_key}] at {mix_pos_ms/1000:.1f}s → {label}")

        except Exception as e:
            print(f"  ⚠️  Mix error for {sound_key}: {e}")

    return mixed_audio

# GENERATE FULL MULTI VOICE AUDIO

def generate_multi_voice_audio(story_text, language, story_id="latest", category="general_horror"):
    # Store story data for sound mixer
    generate_multi_voice_audio._current_story = {
        "text"     : story_text,
        "language" : language,
        "category" : category
    }
    print("\n" + "="*60)
    print("  MULTI-VOICE AUDIO GENERATION")
    print("="*60)
    print("   Narrator    → Your voice (deep scary)")
    print("   Old person  → Your voice (slow trembling)")
    print("   Ghost       → Your voice (deep eerie)")
    print("   Female      → Your voice (higher pitch)")
    print("   Male        → Your voice (normal male)")
    print("="*60 + "\n")

    # Parse segments
    print(" Parsing story into voice segments...")
    segments = parse_story_segments(story_text, language)

    narration_count = sum(1 for s in segments if s["type"] == "narration")
    dialogue_count  = sum(1 for s in segments if s["type"] == "dialogue")

    print(f" Found {len(segments)} segments:")
    print(f"    Narration : {narration_count}")
    print(f"    Dialogue  : {dialogue_count}\n")

    # Generate each segment
    segment_files = []
    for i, seg in enumerate(segments):
        filepath = generate_voice_segment(
            seg["text"], seg["voice"], language, i
        )
        segment_files.append((filepath, seg["voice"], seg["type"]))

    # Build audio with sounds at exact positions
    try:
        from backend.features.sound_mixer import build_horror_audio_with_sounds
        from backend.features.sound_inserter import insert_sound_cues

        # Get story data
        story_data  = getattr(
            generate_multi_voice_audio,
            '_current_story',
            {}
        )
        story_text  = story_data.get("text", story_text)
        category    = story_data.get("category", category)

        output_file = os.path.join(
            AUDIO_DIR,
            f"story_{story_id}_multivoice.mp3"
        )

        build_horror_audio_with_sounds(
            segment_audio_files = segment_files,
            story_text          = story_text,
            language            = language,
            category            = category,
            output_path         = output_file
        )

        # Now mix sounds at exact positions
        from pydub import AudioSegment
        base_audio  = AudioSegment.from_mp3(output_file)
        final_audio = mix_sounds_at_positions(
            base_audio, story_text, language
        )
        final_audio.export(output_file, format="mp3", bitrate="192k")
        print("✅ Sounds mixed at exact positions!")

    except Exception as e:
        print(f"⚠️  Sound mixing failed: {e}")
        combined = combine_segments(segment_files)
        combined.export(output_file, format="mp3")

    # Get duration info
    try:
        from pydub import AudioSegment
        combined     = AudioSegment.from_mp3(output_file)
        duration     = len(combined) / 1000
        size_kb      = os.path.getsize(output_file) / 1024
        print(f"\n Audio ready!")
        print(f"   Duration : {duration:.1f} seconds")
        print(f"   Size     : {size_kb:.1f} KB")
        print(f"   File     : {output_file}\n")
    except Exception as e:
        print(f"  Could not read audio info: {e}")

    # Cleanup
    print("\n Cleaning temp files...")
    for filepath, _, _ in segment_files:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

    duration = len(combined) / 1000
    size_kb  = os.path.getsize(output_file) / 1024
    print(f"\n Audio ready!")
    print(f"   Duration : {duration:.1f} seconds")
    print(f"   Size     : {size_kb:.1f} KB")
    print(f"   File     : {output_file}\n")

    return output_file

# PLAY AUDIO

def play_multivoice_audio(filepath):
    if not filepath or not os.path.exists(filepath):
        print(" Audio file not found")
        return

    print("  Playing multi-voice story...")
    print("   Press Ctrl+C to stop\n")

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

        pygame.mixer.quit()
        print(" Playback complete!\n")

    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("\n  Stopped\n")

    except Exception as e:
        print(f" Playback error: {e}")

# MULTI VOICE MENU
# returns audio filepath for saving

def multivoice_menu(story_text, language, story_id="latest", category="general_horror"):
    print("\n" + "="*60)
    print("  AUDIO OPTIONS")
    print("="*60)
    print("  1. Generate and play multi-voice audio")
    print("  2. Generate and save audio only (MP3)")
    print("  3. Skip audio")
    print("="*60)

    choice = input("\n  Choose (1/2/3): ").strip()

    if choice == "1":
        filepath = generate_multi_voice_audio(story_text, language, story_id, category)
        if filepath:
            play_multivoice_audio(filepath)
        return filepath

    elif choice == "2":
        filepath = generate_multi_voice_audio(story_text, language, story_id, category)
        if filepath:
            print(f" Audio ready for saving: {filepath}\n")
        return filepath

    else:
        print("  Skipping audio\n")
        return None

# MAIN — for testing

if __name__ == "__main__":
    print("\n  Testing Multi-Voice TTS\n")

    test_hindi = """रात के अंधेरे में राहुल उस पुरानी हवेली के पास पहुँचा।

दरवाज़ा अपने आप खुल गया। अंदर से एक बूढ़ी आवाज़ आई।

"अंदर आ जाओ बेटा। मैं कब से इंतज़ार कर रहा हूँ।"

राहुल काँप गया। उसने पूछा "कौन हो तुम?"

एक ठंडी फुसफुसाहट आई। "मैं इस घर का आखिरी मालिक।"
"""

    test_english = """Daniel walked toward the old mansion at midnight.

The door creaked open on its own. An old trembling voice called out.

"Come inside boy. I have been waiting for so very long."

Daniel froze. He whispered "Who is there?"

A cold ghostly voice replied. "I am the last owner of this house."
"""

    print("1. Test Hindi")
    print("2. Test English")
    choice = input("Choose: ").strip()

    if choice == "1":
        multivoice_menu(test_hindi, "hindi", "test_hindi")
    else:
        multivoice_menu(test_english, "english", "test_english")