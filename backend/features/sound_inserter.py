import os
import re
import random

# ─────────────────────────────────────────
# SOUND DISPLAY NAMES
# Hindi and English labels for each sound
# ─────────────────────────────────────────
SOUND_LABELS = {
    "thunder": {
        "hindi"  : "*बादल गरजते हैं*",
        "english": "*thunder rumbles*"
    },
    "wind_howling": {
        "hindi"  : "*हवा सनसनाती है*",
        "english": "*wind howls*"
    },
    "door_creaking": {
        "hindi"  : "*दरवाज़ा चरमराता है*",
        "english": "*door creaks*"
    },
    "footsteps": {
        "hindi"  : "*कदमों की आवाज़*",
        "english": "*footsteps approach*"
    },
    "wolf_howling": {
        "hindi"  : "*भेड़िया रोता है*",
        "english": "*wolf howls in distance*"
    },
    "clock_ticking": {
        "hindi"  : "*घड़ी टिकटिक करती है*",
        "english": "*clock ticks slowly*"
    },
    "glass_breaking": {
        "hindi"  : "*शीशा टूटता है*",
        "english": "*glass shatters*"
    },
    "chains_rattling": {
        "hindi"  : "*जंजीरें खड़खड़ाती हैं*",
        "english": "*chains rattle*"
    },
    "evil_laugh": {
        "hindi"  : "*दुष्ट हँसी गूँजती है*",
        "english": "*evil laughter echoes*"
    },
    "ghost_whisper": {
        "hindi"  : "*भूतिया फुसफुसाहट*",
        "english": "*ghostly whisper*"
    },
    "heartbeat": {
        "hindi"  : "*दिल तेज़ धड़कता है*",
        "english": "*heartbeat quickens*"
    },
    "owl_hooting": {
        "hindi"  : "*उल्लू बोलता है*",
        "english": "*owl hoots*"
    },
    "fire_crackling": {
        "hindi"  : "*आग चटचटाती है*",
        "english": "*fire crackles*"
    },
    "screaming_distance": {
        "hindi"  : "*दूर से चीख सुनाई देती है*",
        "english": "*screaming in the distance*"
    },
    "crow_cawing": {
        "hindi"  : "*कौआ काँव काँव करता है*",
        "english": "*crow caws*"
    },
    "rain_pouring": {
        "hindi"  : "*मूसलाधार बारिश होती है*",
        "english": "*rain pours heavily*"
    },
    "church_bell": {
        "hindi"  : "*चर्च की घंटी बजती है*",
        "english": "*church bell tolls*"
    },
    "dog_barking": {
        "hindi"  : "*कुत्ता भौंकता है*",
        "english": "*dog barks frantically*"
    },
    "water_dripping": {
        "hindi"  : "*पानी टपकता है*",
        "english": "*water drips slowly*"
    },
    "knife_scraping": {
        "hindi"  : "*चाकू रगड़ने की आवाज़*",
        "english": "*knife scrapes metal*"
    },
}

# ─────────────────────────────────────────
# CATEGORY → SOUND MAPPING
# which sounds fit which story type
# ─────────────────────────────────────────
CATEGORY_SOUND_MAP = {
    "ghost": [
        "ghost_whisper", "footsteps", "door_creaking",
        "chains_rattling", "heartbeat", "wind_howling",
        "clock_ticking", "water_dripping"
    ],
    "witch": [
        "owl_hooting", "crow_cawing", "fire_crackling",
        "thunder", "wind_howling", "evil_laugh",
        "rain_pouring", "wolf_howling"
    ],
    "haunted_house": [
        "door_creaking", "footsteps", "chains_rattling",
        "glass_breaking", "wind_howling", "clock_ticking",
        "water_dripping", "dog_barking"
    ],
    "graveyard": [
        "crow_cawing", "owl_hooting", "wolf_howling",
        "church_bell", "wind_howling", "chains_rattling",
        "thunder", "dog_barking"
    ],
    "demon": [
        "evil_laugh", "chains_rattling", "thunder",
        "screaming_distance", "heartbeat", "fire_crackling",
        "glass_breaking", "knife_scraping"
    ],
    "vampire": [
        "heartbeat", "footsteps", "owl_hooting",
        "crow_cawing", "wind_howling", "door_creaking",
        "wolf_howling", "clock_ticking"
    ],
    "monster": [
        "wolf_howling", "footsteps", "dog_barking",
        "screaming_distance", "thunder", "glass_breaking",
        "evil_laugh", "heartbeat"
    ],
    "cursed_object": [
        "clock_ticking", "glass_breaking", "ghost_whisper",
        "water_dripping", "chains_rattling", "heartbeat",
        "knife_scraping", "evil_laugh"
    ],
    "possessed": [
        "heartbeat", "ghost_whisper", "evil_laugh",
        "chains_rattling", "screaming_distance", "thunder",
        "dog_barking", "church_bell"
    ],
    "general_horror": [
        "thunder", "wind_howling", "footsteps",
        "heartbeat", "door_creaking", "owl_hooting",
        "rain_pouring", "ghost_whisper"
    ],
}

# ─────────────────────────────────────────
# KEYWORD → SOUND TRIGGERS
# automatic sound based on story text
# ─────────────────────────────────────────
KEYWORD_TRIGGERS = {
    "english": {
        "thunder"           : ["thunder", "lightning", "storm", "thunder crashed"],
        "wind_howling"      : ["wind", "howling", "gust", "breeze", "air"],
        "door_creaking"     : ["door", "creaked", "hinges", "opened", "swung"],
        "footsteps"         : ["footsteps", "walked", "steps", "approaching", "paced"],
        "wolf_howling"      : ["wolf", "howl", "forest", "night creature"],
        "clock_ticking"     : ["clock", "midnight", "ticked", "time", "hour"],
        "glass_breaking"    : ["glass", "shattered", "broke", "mirror", "window"],
        "chains_rattling"   : ["chains", "rattling", "metal", "bound", "shackles"],
        "evil_laugh"        : ["laughed", "cackled", "chuckled", "evil laugh"],
        "ghost_whisper"     : ["whispered", "whisper", "voice", "breath", "murmured"],
        "heartbeat"         : ["heart", "pulse", "fear", "terrified", "froze"],
        "owl_hooting"       : ["owl", "night", "darkness", "tree", "branch"],
        "fire_crackling"    : ["fire", "flame", "candle", "torch", "burning"],
        "screaming_distance": ["screamed", "scream", "shrieked", "cried out", "shriek"],
        "crow_cawing"       : ["crow", "raven", "bird", "black bird", "cawed"],
        "rain_pouring"      : ["rain", "poured", "downpour", "raining", "wet"],
        "church_bell"       : ["bell", "church", "toll", "midnight bell", "rang"],
        "dog_barking"       : ["dog", "barked", "howled", "growled", "animal"],
        "water_dripping"    : ["drip", "water", "drops", "wet", "puddle"],
        "knife_scraping"    : ["knife", "blade", "scraped", "sharp", "metal sound"],
    },
    "hindi": {
        "thunder"           : ["बादल", "बिजली", "तूफान", "गरज", "आँधी"],
        "wind_howling"      : ["हवा", "आँधी", "सनसनाहट", "झोंका", "बयार"],
        "door_creaking"     : ["दरवाज़ा", "चरमराया", "खुला", "बंद", "किवाड़"],
        "footsteps"         : ["कदम", "पैर", "चलने", "आहट", "क़दमों"],
        "wolf_howling"      : ["भेड़िया", "जंगल", "रात", "चीख", "हुआँ"],
        "clock_ticking"     : ["घड़ी", "बारह", "रात", "टिकटिक", "समय"],
        "glass_breaking"    : ["शीशा", "टूटा", "काँच", "आईना", "खिड़की"],
        "chains_rattling"   : ["जंजीर", "बेड़ी", "खड़खड़", "धातु", "ज़ंजीर"],
        "evil_laugh"        : ["हँसी", "हँसा", "ठहाका", "दुष्ट", "खिलखिलाया"],
        "ghost_whisper"     : ["फुसफुसाया", "आवाज़", "साँस", "धीमे", "कानों"],
        "heartbeat"         : ["दिल", "धड़कन", "डर", "काँपा", "रुक"],
        "owl_hooting"       : ["उल्लू", "रात", "पेड़", "अंधेरा", "जंगल"],
        "fire_crackling"    : ["आग", "लौ", "मोमबत्ती", "जल", "चिंगारी"],
        "screaming_distance": ["चीख", "चिल्लाया", "चीखा", "रोया", "आवाज़"],
        "crow_cawing"       : ["कौआ", "काँव", "पंछी", "काला", "डाली"],
        "rain_pouring"      : ["बारिश", "पानी", "बरसात", "भीगा", "बूँदें"],
        "church_bell"       : ["घंटी", "घंटा", "बजी", "मंदिर", "आवाज़"],
        "dog_barking"       : ["कुत्ता", "भौंका", "रोया", "जानवर", "भेड़िया"],
        "water_dripping"    : ["पानी", "टपका", "बूँद", "गीला", "रिसना"],
        "knife_scraping"    : ["चाकू", "ब्लेड", "तेज़", "धार", "रगड़"],
    }
}


# ─────────────────────────────────────────
# INSERT SOUND CUES INTO STORY TEXT
# ─────────────────────────────────────────
def insert_sound_cues(story_text, language, category):
    import time
    random.seed(time.time_ns())

    paragraphs   = story_text.split('\n\n')
    result       = []
    sounds_used  = CATEGORY_SOUND_MAP.get(
        category,
        CATEGORY_SOUND_MAP["general_horror"]
    )
    total_paras  = len(paragraphs)

    for i, para in enumerate(paragraphs):
        if not para.strip():
            result.append(para)
            continue

        # Detect keyword triggers
        triggered_sounds = detect_triggers(para, language)

        # Add category sounds at intervals
        # every 2-3 paragraphs add a category sound
        interval_sound = None
        if i % 2 == 0 and sounds_used:
            interval_sound = random.choice(sounds_used)

        # Combine triggered + interval sounds
        all_sounds = list(set(triggered_sounds))
        if interval_sound and interval_sound not in all_sounds:
            all_sounds.append(interval_sound)

        # Add sound cue before paragraph
        sound_cues = []
        for sound in all_sounds[:2]:   # max 2 sounds per para
            label = SOUND_LABELS.get(sound, {}).get(language, "")
            if label:
                sound_cues.append(label)

        if sound_cues:
            cue_text = "  ".join(sound_cues)
            result.append(f"{cue_text}\n{para}")
        else:
            result.append(para)

    return '\n\n'.join(result)


# ─────────────────────────────────────────
# DETECT KEYWORD TRIGGERS
# ─────────────────────────────────────────
def detect_triggers(text, language):
    text_lower = text.lower()
    triggers   = KEYWORD_TRIGGERS.get(language, KEYWORD_TRIGGERS["english"])
    found      = []

    for sound, keywords in triggers.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                found.append(sound)
                break

    return found


# ─────────────────────────────────────────
# EXTRACT SOUND CUES FROM TEXT
# returns list of (position, sound_name)
# for audio mixing
# ─────────────────────────────────────────
def extract_sound_positions(story_with_cues, language):
    positions  = []
    lines      = story_with_cues.split('\n')
    char_pos   = 0

    for line in lines:
        # Check if line has sound cues
        for sound_key, labels in SOUND_LABELS.items():
            label = labels.get(language, "")
            if label and label in line:
                positions.append({
                    "sound"   : sound_key,
                    "position": char_pos,
                    "label"   : label
                })
        char_pos += len(line) + 1

    return positions


# ─────────────────────────────────────────
# GET SOUND FILE PATH
# ─────────────────────────────────────────
def get_sound_path(sound_key):
    sounds_dir = "backend/features/horror_sounds"
    filepath   = os.path.join(sounds_dir, f"{sound_key}.mp3")
    if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
        return filepath
    return None


# ─────────────────────────────────────────
# LIST ALL AVAILABLE SOUNDS
# ─────────────────────────────────────────
def check_all_sounds():
    print("\n" + "="*60)
    print("🔊 ALL HORROR SOUNDS STATUS")
    print("="*60)

    sounds_dir = "backend/features/horror_sounds"
    available  = []
    missing    = []

    for sound_key in SOUND_LABELS.keys():
        path = get_sound_path(sound_key)
        if path:
            size = os.path.getsize(path) / 1024
            print(f"  ✅ {sound_key:25s} ({size:.1f} KB)")
            available.append(sound_key)
        else:
            print(f"  ❌ {sound_key:25s} MISSING")
            missing.append(sound_key)

    print("="*60)
    print(f"  Available : {len(available)}/{len(SOUND_LABELS)}")
    if missing:
        print(f"  Missing   : {len(missing)} sounds")
        print(f"  Run: python backend/features/download_sounds.py")
    print("="*60 + "\n")
    return available


if __name__ == "__main__":
    check_all_sounds()

    # Test sound insertion
    test_story = """It was a dark stormy night. Thunder crashed outside.

The door creaked open slowly. Footsteps approached.

She whispered something in the darkness. Her heartbeat quickened.

Glass shattered somewhere above. A wolf howled in the distance.

The clock struck midnight. She screamed."""

    print("\n🔊 ENGLISH STORY WITH SOUND CUES:\n")
    result = insert_sound_cues(test_story, "english", "ghost")
    print(result)

    print("\n" + "="*60)

    test_hindi = """रात के अंधेरे में बादल गरज रहे थे।

दरवाज़ा चरमराकर खुला। कदमों की आहट आई।

उसने धीमे से फुसफुसाया। उसका दिल तेज़ धड़क रहा था।

ऊपर से शीशा टूटने की आवाज़ आई। जंगल में भेड़िया रोया।

घड़ी ने बारह बजाए। वो चीख पड़ी।"""

    print("\n🔊 HINDI STORY WITH SOUND CUES:\n")
    result = insert_sound_cues(test_hindi, "hindi", "ghost")
    print(result)