import os
import re
import random
from pydub import AudioSegment
# Tell pydub where ffmpeg is
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"  # type: ignore
AudioSegment.ffmpeg    = r"C:\ffmpeg\bin\ffmpeg.exe"  # type: ignore

# Set ffprobe via pydub utils
from pydub.utils import which
import pydub.utils as pydub_utils
pydub_utils.get_prober_name = lambda: r"C:\ffmpeg\bin\ffprobe.exe"  # type: ignore
# CONFIG
SOUNDS_DIR = "backend/features/horror_sounds"
os.makedirs(SOUNDS_DIR, exist_ok=True)

# Volume boost for loud and scary (+8 to +12 dB)
SOUND_VOLUME_BOOST = 10

# ALL AVAILABLE SOUNDS
SOUND_FILES = {
    "glass_breaking"    : "glass_breaking.mp3",
    "chains_rattling"   : "chains_rattling.mp3",
    "ghost_whisper"     : "ghost_whisper.mp3",
    "owl_hooting"       : "owl_hooting.mp3",
    "heartbeat"         : "heartbeat.mp3",
    "fire_crackling"    : "fire_crackling.mp3",
    "screaming_distance": "screaming_distance.mp3",
    "crow_cawing"       : "crow_cawing.mp3",
}

# CATEGORY → SOUNDS MAPPING
# which sounds play for which story type
CATEGORY_SOUNDS = {
    "ghost": {
        "intro"  : ["heartbeat", "ghost_whisper"],
        "middle" : ["chains_rattling", "ghost_whisper", "screaming_distance"],
        "climax" : ["screaming_distance", "heartbeat", "chains_rattling"],
        "outro"  : ["ghost_whisper", "owl_hooting"]
    },
    "witch": {
        "intro"  : ["owl_hooting", "crow_cawing"],
        "middle" : ["fire_crackling", "crow_cawing", "ghost_whisper"],
        "climax" : ["screaming_distance", "glass_breaking", "crow_cawing"],
        "outro"  : ["owl_hooting", "fire_crackling"]
    },
    "haunted_house": {
        "intro"  : ["heartbeat", "owl_hooting"],
        "middle" : ["glass_breaking", "chains_rattling", "ghost_whisper"],
        "climax" : ["glass_breaking", "screaming_distance", "heartbeat"],
        "outro"  : ["chains_rattling", "ghost_whisper"]
    },
    "graveyard": {
        "intro"  : ["owl_hooting", "crow_cawing"],
        "middle" : ["chains_rattling", "ghost_whisper", "heartbeat"],
        "climax" : ["screaming_distance", "chains_rattling", "crow_cawing"],
        "outro"  : ["owl_hooting", "crow_cawing"]
    },
    "demon": {
        "intro"  : ["heartbeat", "chains_rattling"],
        "middle" : ["screaming_distance", "ghost_whisper", "chains_rattling"],
        "climax" : ["screaming_distance", "glass_breaking", "heartbeat"],
        "outro"  : ["ghost_whisper", "chains_rattling"]
    },
    "vampire": {
        "intro"  : ["heartbeat", "owl_hooting"],
        "middle" : ["ghost_whisper", "heartbeat", "crow_cawing"],
        "climax" : ["screaming_distance", "heartbeat", "glass_breaking"],
        "outro"  : ["owl_hooting", "crow_cawing"]
    },
    "cursed_object": {
        "intro"  : ["heartbeat", "ghost_whisper"],
        "middle" : ["glass_breaking", "chains_rattling", "ghost_whisper"],
        "climax" : ["glass_breaking", "screaming_distance", "heartbeat"],
        "outro"  : ["ghost_whisper", "chains_rattling"]
    },
    "possessed": {
        "intro"  : ["heartbeat", "ghost_whisper"],
        "middle" : ["screaming_distance", "chains_rattling", "ghost_whisper"],
        "climax" : ["screaming_distance", "glass_breaking", "heartbeat"],
        "outro"  : ["ghost_whisper", "owl_hooting"]
    },
    "general_horror": {
        "intro"  : ["heartbeat", "owl_hooting"],
        "middle" : ["ghost_whisper", "chains_rattling", "crow_cawing"],
        "climax" : ["screaming_distance", "heartbeat", "glass_breaking"],
        "outro"  : ["owl_hooting", "ghost_whisper"]
    }
}

# TENSION KEYWORDS
# these trigger specific sounds mid-story
TRIGGER_KEYWORDS = {
    "english": {
        "glass_breaking"    : ["shattered", "broke", "crashed", "smashed",
                               "glass", "mirror", "window broke"],
        "chains_rattling"   : ["chains", "rattling", "bound", "shackles",
                               "dragging", "metal sound"],
        "ghost_whisper"     : ["whispered", "whisper", "voice", "heard something",
                               "cold breath", "behind him", "behind her"],
        "heartbeat"         : ["heart", "pulse", "fear", "terrified",
                               "froze", "could not move", "paralyzed"],
        "screaming_distance": ["screamed", "scream", "shrieked", "cried out",
                               "help", "no one came", "nobody heard"],
        "owl_hooting"       : ["night", "darkness", "midnight", "forest",
                               "outside", "window"],
        "fire_crackling"    : ["fire", "flame", "candle", "torch",
                               "burning", "smoke"],
        "crow_cawing"       : ["crow", "bird", "tree", "branch",
                               "graveyard", "cemetery", "dawn"]
    },
    "hindi": {
        "glass_breaking"    : ["टूट", "शीशा", "दर्पण", "खिड़की",
                               "चकनाचूर", "गिर"],
        "chains_rattling"   : ["जंजीर", "बेड़ी", "खड़खड़", "धातु",
                               "बंधा", "खिंचाव"],
        "ghost_whisper"     : ["फुसफुसाया", "आवाज़", "साँस", "कानों में",
                               "पीछे से", "ठंडी हवा"],
        "heartbeat"         : ["दिल", "धड़कन", "डर", "काँप",
                               "रुक गया", "साँस रुकी"],
        "screaming_distance": ["चीख", "चिल्लाया", "मदद", "बचाओ",
                               "कोई नहीं सुना", "दूर से"],
        "owl_hooting"       : ["रात", "अंधेरा", "जंगल", "बाहर",
                               "खिड़की", "आधी रात"],
        "fire_crackling"    : ["आग", "लौ", "मोमबत्ती", "धुआँ",
                               "जल रहा", "चिंगारी"],
        "crow_cawing"       : ["कौआ", "पेड़", "कब्रिस्तान", "सुबह",
                               "डाली", "पंछी"]
    }
}


# LOAD SOUND FILE
def load_sound(sound_key):
    filename = SOUND_FILES.get(sound_key)
    if not filename:
        return None

    filepath = os.path.join(SOUNDS_DIR, filename)
    if not os.path.exists(filepath):
        return None

    try:
        audio = AudioSegment.from_file(filepath)
        # Boost volume — loud and scary
        audio = audio + SOUND_VOLUME_BOOST
        return audio
    except Exception as e:
        print(f"    Could not load sound '{sound_key}': {e}")
        return None


# CHECK AVAILABLE SOUNDS
def check_sounds():
    print("\n" + "="*60)
    print(" HORROR SOUNDS STATUS")
    print("="*60)

    available = []
    missing   = []

    for key, filename in SOUND_FILES.items():
        filepath = os.path.join(SOUNDS_DIR, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024
            print(f"   {key:25s} → {filename} ({size:.1f} KB)")
            available.append(key)
        else:
            print(f"   {key:25s} → {filename} MISSING")
            missing.append(key)

    print("="*60)
    print(f"  Available : {len(available)}/{len(SOUND_FILES)}")
    if missing:
        print(f"  Missing   : {', '.join(missing)}")
        print(f"\n  Download from: pixabay.com/sound-effects")
        print(f"  Save to: {SOUNDS_DIR}/")
    print("="*60 + "\n")

    return available


# DETECT SOUND TRIGGERS IN TEXT
# finds keywords and maps to sounds
def detect_sound_triggers(text, language):
    triggers  = []
    keywords  = TRIGGER_KEYWORDS.get(language, TRIGGER_KEYWORDS["english"])
    text_lower= text.lower()

    for sound_key, kw_list in keywords.items():
        for kw in kw_list:
            if kw.lower() in text_lower:
                triggers.append(sound_key)
                break   # one match per sound per segment

    return triggers


# SPLIT STORY INTO SECTIONS
# intro / middle / climax / outro
def split_story_sections(story_text):
    paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]
    total      = len(paragraphs)

    if total <= 2:
        return {
            "intro" : paragraphs,
            "middle": [],
            "climax": [],
            "outro" : []
        }

    intro_end  = max(1, total // 4)
    climax_start = max(intro_end + 1, int(total * 0.7))
    outro_start  = max(climax_start + 1, total - 1)

    return {
        "intro" : paragraphs[:intro_end],
        "middle": paragraphs[intro_end:climax_start],
        "climax": paragraphs[climax_start:outro_start],
        "outro" : paragraphs[outro_start:]
    }


# CREATE SILENT PAUSE
def silence(ms):
    return AudioSegment.silent(duration=ms)


# MIX SOUND INTO AUDIO
# overlays sound effect on top of narration
def mix_sound_into_audio(base_audio, sound_key, position_ms=0):
    sound = load_sound(sound_key)
    if not sound:
        return base_audio

    # Trim sound to max 4 seconds
    sound = sound[:4000]

    # Fade in and out for natural feel
    sound = sound.fade_in(200).fade_out(300)

    # Make sure position is valid
    position_ms = min(position_ms, max(0, len(base_audio) - len(sound)))

    # Overlay sound on base audio
    try:
        mixed = base_audio.overlay(sound, position=position_ms)
        return mixed
    except Exception as e:
        print(f"    Mix error for '{sound_key}': {e}")
        return base_audio


# ADD SOUNDS BETWEEN PARAGRAPHS
def add_sound_between_segments(segment_audio_list, story_text,
                                language, category):
    print("\n Adding horror sounds to audio...")

    cat_sounds = CATEGORY_SOUNDS.get(category, CATEGORY_SOUNDS["general_horror"])
    sections   = split_story_sections(story_text)

    # Map section names to segment indices
    total_segs  = len(segment_audio_list)
    intro_end   = max(1, total_segs // 4)
    climax_start= max(intro_end + 1, int(total_segs * 0.7))
    outro_start = max(climax_start + 1, total_segs - 1)

    final_audio  = AudioSegment.empty()
    sounds_added = 0

    for i, seg_audio in enumerate(segment_audio_list):
        if seg_audio is None:
            continue

        # Determine section
        if i < intro_end:
            section = "intro"
        elif i < climax_start:
            section = "middle"
        elif i < outro_start:
            section = "climax"
        else:
            section = "outro"

        # Get sounds for this section
        section_sounds = cat_sounds.get(section, [])

        # Also check keyword triggers in segment text
        seg_text    = ""
        paragraphs  = [p.strip() for p in story_text.split('\n\n') if p.strip()]
        if i < len(paragraphs):
            seg_text = paragraphs[i]

        keyword_sounds = detect_sound_triggers(seg_text, language)

        # Combine section sounds + keyword sounds
        all_sounds = list(set(section_sounds + keyword_sounds))

        # Add segment audio
        final_audio += seg_audio

        # Add 1-2 sounds after segment
        if all_sounds and random.random() > 0.3:   # 70% chance
            # Pick 1 sound (2 at climax)
            num_sounds = 2 if section == "climax" else 1
            picked     = random.sample(
                all_sounds,
                min(num_sounds, len(all_sounds))
            )

            for sound_key in picked:
                sound = load_sound(sound_key)
                if sound:
                    # Trim to 3 seconds
                    sound       = sound[:3000]
                    sound       = sound.fade_in(100).fade_out(200)
                    # Add small pause before sound
                    final_audio += silence(200)
                    final_audio += sound
                    final_audio += silence(300)
                    sounds_added+= 1
                    print(f"   [{section:6s}] Added: {sound_key}")

    print(f"   Total sounds added: {sounds_added}")
    return final_audio


# MAIN BUILD FUNCTION
# called from multi_voice_tts.py
def build_horror_audio_with_sounds(
    segment_audio_files, story_text,
    language, category, output_path
):
    print("\n" + "="*60)
    print(" BUILDING HORROR AUDIO WITH SOUNDS")
    print(f"   Category : {category}")
    print(f"   Language : {language}")
    print("="*60)

    # Check which sounds are available
    available_sounds = check_sounds()
    if not available_sounds:
        print("  No sound files found!")
        print(f"   Add .mp3 files to: {SOUNDS_DIR}/")
        print("   Building audio without sounds...\n")

    # Load all segment audios
    segment_audios = []
    for filepath, voice_key, seg_type in segment_audio_files:
        if filepath and os.path.exists(filepath):
            try:
                audio = AudioSegment.from_mp3(filepath)
                segment_audios.append(audio)
            except:
                segment_audios.append(None)
        else:
            segment_audios.append(None)

    # Add sounds between segments
    if available_sounds:
        final_audio = add_sound_between_segments(
            segment_audios, story_text, language, category
        )
    else:
        # Just combine without sounds
        final_audio = AudioSegment.empty()
        for audio in segment_audios:
            if audio:
                final_audio += audio

    # Export final audio
    final_audio.export(output_path, format="mp3", bitrate="192k")

    duration = len(final_audio) / 1000
    size_kb  = os.path.getsize(output_path) / 1024

    print(f"\n Horror audio complete!")
    print(f"   Duration : {duration:.1f} seconds")
    print(f"   Size     : {size_kb:.1f} KB")
    print(f"   File     : {output_path}\n")

    return output_path


# MAIN — for testing
if __name__ == "__main__":
    check_sounds()