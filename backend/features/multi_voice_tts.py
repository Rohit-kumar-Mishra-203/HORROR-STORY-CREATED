import os
import re
import time
import numpy as np
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import pygame

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
AUDIO_DIR = "audio_output"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ─────────────────────────────────────────
# VOICE PROFILES
# ─────────────────────────────────────────
# Each voice has:
# speed     → playback speed (>1 faster, <1 slower)
# pitch     → semitone shift (negative = deeper)
# volume    → volume in dB
# tld       → gTTS accent (com=US, co.uk=British,
#              co.in=Indian, com.au=Australian)

VOICE_PROFILES = {
    "narrator_scary": {
        "speed"   : 0.85,      # slow and deliberate
        "pitch"   : -4,        # very deep
        "volume"  : 3,         # slightly louder
        "tld_en"  : "co.uk",   # British accent = scarier
        "tld_hi"  : "co.in",
        "pause"   : 0.8        # longer pauses
    },
    "old_person": {
        "speed"   : 0.80,      # slow and trembling
        "pitch"   : -2,        # lower pitch
        "volume"  : -2,        # slightly quieter
        "tld_en"  : "com.au",  # Australian = aged feel
        "tld_hi"  : "co.in",
        "pause"   : 1.0        # very slow pauses
    },
    "male_character": {
        "speed"   : 1.0,
        "pitch"   : -2,
        "volume"  : 0,
        "tld_en"  : "com",
        "tld_hi"  : "co.in",
        "pause"   : 0.5
    },
    "female_character": {
        "speed"   : 1.1,
        "pitch"   : 2,
        "volume"  : 0,
        "tld_en"  : "co.uk",
        "tld_hi"  : "co.in",
        "pause"   : 0.5
    },
    "ghost": {
        "speed"   : 0.75,      # very slow
        "pitch"   : -6,        # very deep
        "volume"  : -4,        # distant/quiet
        "tld_en"  : "co.uk",
        "tld_hi"  : "co.in",
        "pause"   : 1.5        # long eerie pauses
    }
}


# ─────────────────────────────────────────
# PARSE STORY INTO SEGMENTS
# splits story into narrator and dialogue parts
# ─────────────────────────────────────────
def parse_story_segments(story_text, language):
    segments = []
    lines    = story_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect dialogue — text inside quotes
        # Hindi quotes: " " or " "
        # English quotes: " "
        dialogue_pattern = r'["""]([^"""]+)["""]'
        dialogues        = re.findall(dialogue_pattern, line)

        if dialogues:
            # Split line into narrator + dialogue parts
            parts    = re.split(dialogue_pattern, line)
            in_quote = False

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                if part in dialogues:
                    # This is dialogue — detect speaker
                    voice = detect_speaker_voice(line, part, language)
                    segments.append({
                        "text"  : part,
                        "voice" : voice,
                        "type"  : "dialogue"
                    })
                else:
                    # This is narration
                    segments.append({
                        "text"  : part,
                        "voice" : "narrator_scary",
                        "type"  : "narration"
                    })
        else:
            # Pure narration line
            segments.append({
                "text"  : line,
                "voice" : "narrator_scary",
                "type"  : "narration"
            })

    return segments


# ─────────────────────────────────────────
# DETECT SPEAKER VOICE
# tries to figure out who is speaking
# ─────────────────────────────────────────
def detect_speaker_voice(full_line, dialogue, language):
    line_lower = full_line.lower()

    # Ghost/spirit/demon dialogue
    ghost_keywords_en = ["ghost", "spirit", "demon", "shadow", "voice", "whisper"]
    ghost_keywords_hi = ["भूत", "आत्मा", "राक्षस", "साया", "आवाज़", "फुसफुसाया"]

    old_keywords_en   = ["old", "elder", "grandma", "grandpa", "ancient", "aged"]
    old_keywords_hi   = ["बूढ़ा", "बूढ़ी", "दादा", "दादी", "बुज़ुर्ग", "पुराना"]

    female_keywords_en= ["she", "her", "woman", "girl", "lady", "mother", "sister"]
    female_keywords_hi= ["वो", "उसने", "औरत", "लड़की", "माँ", "बहन", "दादी"]

    keywords = ghost_keywords_en + ghost_keywords_hi
    if any(kw in line_lower for kw in keywords):
        return "ghost"

    keywords = old_keywords_en + old_keywords_hi
    if any(kw in line_lower for kw in keywords):
        return "old_person"

    keywords = female_keywords_en + female_keywords_hi
    if any(kw in line_lower for kw in keywords):
        return "female_character"

    return "male_character"


# ─────────────────────────────────────────
# APPLY VOICE EFFECTS
# modifies audio pitch and speed
# ─────────────────────────────────────────
def apply_voice_effects(audio_segment, profile):
    # Apply speed change
    speed = profile.get("speed", 1.0)
    if speed != 1.0:
        if speed > 1.0:
            audio_segment = speedup(audio_segment, playback_speed=speed)
        else:
            # Slow down by changing frame rate
            new_frame_rate = int(audio_segment.frame_rate * speed)
            audio_segment  = audio_segment._spawn(
                audio_segment.raw_data,
                overrides={"frame_rate": new_frame_rate}
            )
            audio_segment = audio_segment.set_frame_rate(44100)

    # Apply pitch shift (semitones)
    pitch = profile.get("pitch", 0)
    if pitch != 0:
        new_sample_rate = int(audio_segment.frame_rate * (2 ** (pitch / 12.0)))
        audio_segment   = audio_segment._spawn(
            audio_segment.raw_data,
            overrides={"frame_rate": new_sample_rate}
        )
        audio_segment = audio_segment.set_frame_rate(44100)

    # Apply volume change
    volume = profile.get("volume", 0)
    if volume != 0:
        audio_segment = audio_segment + volume

    return audio_segment


# ─────────────────────────────────────────
# GENERATE VOICE SEGMENT
# converts one text segment to audio
# ─────────────────────────────────────────
def generate_voice_segment(text, voice_key, language, segment_index):
    if not text.strip():
        return None

    profile   = VOICE_PROFILES.get(voice_key, VOICE_PROFILES["narrator_scary"])
    lang_code = "hi" if language == "hindi" else "en"
    tld       = profile["tld_hi"] if language == "hindi" else profile["tld_en"]

    # Temp file for this segment
    temp_file = os.path.join(AUDIO_DIR, f"temp_seg_{segment_index}.mp3")
    out_file  = os.path.join(AUDIO_DIR, f"seg_{segment_index}_{voice_key}.mp3")

    try:
        # Generate base TTS
        tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
        tts.save(temp_file)

        # Load and apply effects
        audio   = AudioSegment.from_mp3(temp_file)
        audio   = apply_voice_effects(audio, profile)

        # Export processed audio
        audio.export(out_file, format="mp3")

        # Cleanup temp
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return out_file

    except Exception as e:
        print(f"⚠️  Segment {segment_index} failed: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return None


# ─────────────────────────────────────────
# ADD PAUSE BETWEEN SEGMENTS
# ─────────────────────────────────────────
def create_pause(duration_ms=500):
    return AudioSegment.silent(duration=duration_ms)


# ─────────────────────────────────────────
# COMBINE ALL SEGMENTS INTO ONE AUDIO
# ─────────────────────────────────────────
def combine_segments(segment_files, language):
    print("\n🎬 Combining all voice segments...")

    combined  = AudioSegment.empty()
    prev_voice= None

    for i, (filepath, voice_key, seg_type) in enumerate(segment_files):
        if not filepath or not os.path.exists(filepath):
            continue

        audio   = AudioSegment.from_mp3(filepath)
        profile = VOICE_PROFILES.get(voice_key, VOICE_PROFILES["narrator_scary"])

        # Add pause before dialogue (more dramatic)
        if seg_type == "dialogue":
            pause_ms = int(profile["pause"] * 1200)
            combined += create_pause(pause_ms)
        elif prev_voice != voice_key:
            # Small pause when voice changes
            combined += create_pause(400)

        combined   += audio
        prev_voice  = voice_key

    return combined


# ─────────────────────────────────────────
# MAIN FUNCTION — Generate Multi Voice Audio
# ─────────────────────────────────────────
def generate_multi_voice_audio(story_text, language, story_id="latest"):
    print("\n" + "="*60)
    print("🎙️  MULTI-VOICE AUDIO GENERATION")
    print("="*60)
    print("  Voices:")
    print("  🎭 Narrator    → Deep scary voice")
    print("  👴 Old person  → Slow trembling voice")
    print("  👻 Ghost       → Deep eerie whisper")
    print("  👩 Female      → Higher pitch voice")
    print("  👨 Male        → Normal male voice")
    print("="*60 + "\n")

    # Parse story into segments
    print("📖 Parsing story segments...")
    segments = parse_story_segments(story_text, language)

    narration_count = sum(1 for s in segments if s["type"] == "narration")
    dialogue_count  = sum(1 for s in segments if s["type"] == "dialogue")

    print(f"✅ Found {len(segments)} segments:")
    print(f"   📖 Narration : {narration_count} parts")
    print(f"   💬 Dialogue  : {dialogue_count} parts\n")

    # Generate audio for each segment
    segment_files = []
    for i, segment in enumerate(segments):
        text      = segment["text"]
        voice_key = segment["voice"]
        seg_type  = segment["type"]

        voice_emoji = {
            "narrator_scary"   : "🎭",
            "old_person"       : "👴",
            "ghost"            : "👻",
            "female_character" : "👩",
            "male_character"   : "👨"
        }.get(voice_key, "🎭")

        print(f"  {voice_emoji} [{voice_key}] {text[:50]}...")

        filepath = generate_voice_segment(text, voice_key, language, i)
        segment_files.append((filepath, voice_key, seg_type))

    # Combine all segments
    combined_audio = combine_segments(segment_files, language)

    # Save final audio
    output_file = os.path.join(AUDIO_DIR, f"story_{story_id}_multivoice.mp3")
    combined_audio.export(output_file, format="mp3")

    # Cleanup segment files
    print("\n🧹 Cleaning up temp files...")
    for filepath, _, _ in segment_files:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

    print(f"\n✅ Multi-voice audio saved → {output_file}")
    print(f"   Duration : {len(combined_audio)/1000:.1f} seconds")
    print(f"   Size     : {os.path.getsize(output_file)/1024:.1f} KB\n")

    return output_file


# ─────────────────────────────────────────
# PLAY FINAL AUDIO
# ─────────────────────────────────────────
def play_multivoice_audio(filepath):
    if not filepath or not os.path.exists(filepath):
        print("❌ Audio file not found")
        return

    print("▶️  Playing multi-voice story audio...")
    print("   Press Ctrl+C to stop\n")

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

        pygame.mixer.quit()
        print("\n✅ Playback complete!\n")

    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("\n⏹️  Stopped by user\n")

    except Exception as e:
        print(f"❌ Playback error: {e}")


# ─────────────────────────────────────────
# MULTI VOICE MENU
# ─────────────────────────────────────────
def multivoice_menu(story_text, language, story_id="latest"):
    print("\n" + "="*60)
    print("🎙️  AUDIO OPTIONS")
    print("="*60)
    print("  1. Generate and play multi-voice audio")
    print("  2. Generate and save audio only (MP3)")
    print("  3. Skip audio")
    print("="*60)

    choice = input("\n  Choose (1/2/3): ").strip()

    if choice == "1":
        filepath = generate_multi_voice_audio(story_text, language, story_id)
        if filepath:
            play_multivoice_audio(filepath)

    elif choice == "2":
        filepath = generate_multi_voice_audio(story_text, language, story_id)
        if filepath:
            print(f"💾 Audio saved: {filepath}\n")

    else:
        print("⏭️  Skipping audio\n")


# ─────────────────────────────────────────
# MAIN — for testing
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n🎙️  Testing Multi-Voice TTS\n")

    test_story_hindi = """
रात के अंधेरे में राहुल उस पुरानी हवेली के पास पहुँचा।

दरवाज़ा अपने आप खुल गया। अंदर से एक बूढ़ी आवाज़ आई।

"अंदर आ जाओ बेटा। मैं कब से इंतज़ार कर रहा हूँ।"

राहुल काँप गया। उसने पूछा "कौन हो तुम?"

एक ठंडी फुसफुसाहट आई। "मैं इस घर का आखिरी मालिक।"

राहुल भागना चाहता था पर उसके पैर नहीं उठे।
"""

    test_story_english = """
Daniel walked toward the old mansion at midnight.

The door creaked open on its own. An old trembling voice called out.

"Come inside boy. I have been waiting for so very long."

Daniel froze. He whispered "Who is there?"

A cold ghostly voice replied from the darkness. "I am the last owner of this house."

Daniel wanted to run but his legs would not move.
"""

    print("Testing Hindi multi-voice...")
    multivoice_menu(test_story_hindi, "hindi", "test_hindi")

    print("Testing English multi-voice...")
    multivoice_menu(test_story_english, "english", "test_english")