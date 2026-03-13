import os
import shutil
import numpy as np
import soundfile as sf
import librosa

# CONFIG
VOICE_PROFILES_DIR = "backend/features/voice_profiles"

VOICE_SLOTS = {
    "narrator"        : "Narrator (scary deep storyteller)",
    "male_character"  : "Male Character",
    "female_character": "Female Character",
    "old_person"      : "Old Person (trembling aged voice)",
    "ghost"           : "Ghost/Demon (eerie distorted voice)"
}

# Effects applied on top of your uploaded voice
VOICE_EFFECTS = {
    "narrator": {
        "pitch_shift" : -3,      # semitones lower
        "speed"       : 0.88,    # slower delivery
        "reverb"      : True,    # adds echo
        "description" : "Deep, slow, scary storyteller"
    },
    "male_character": {
        "pitch_shift" : -1,
        "speed"       : 1.0,
        "reverb"      : False,
        "description" : "Normal male character voice"
    },
    "female_character": {
        "pitch_shift" : 3,
        "speed"       : 1.05,
        "reverb"      : False,
        "description" : "Higher pitched female voice"
    },
    "old_person": {
        "pitch_shift" : -2,
        "speed"       : 0.78,    # very slow and trembling
        "reverb"      : False,
        "tremolo"     : True,    # adds trembling effect
        "description" : "Slow trembling aged voice"
    },
    "ghost": {
        "pitch_shift" : -7,      # very deep
        "speed"       : 0.72,    # very slow
        "reverb"      : True,    # strong echo
        "echo"        : True,    # double echo
        "description" : "Deep eerie supernatural whisper"
    }
}

# SAVE UPLOADED VOICE
def save_voice(source_path, voice_slot):
    if voice_slot not in VOICE_SLOTS:
        print(f" Unknown voice slot: {voice_slot}")
        return False

    slot_dir = os.path.join(VOICE_PROFILES_DIR, voice_slot)
    os.makedirs(slot_dir, exist_ok=True)

    # Save original
    ext       = os.path.splitext(source_path)[1]
    orig_path = os.path.join(slot_dir, f"original{ext}")
    shutil.copy2(source_path, orig_path)

    print(f" Voice saved for slot: {VOICE_SLOTS[voice_slot]}")
    print(f"   Saved to: {orig_path}")

    # Process and save with effects
    processed_path = process_voice(orig_path, voice_slot)
    if processed_path:
        print(f" Processed voice saved: {processed_path}")
        return True

    return False

# PROCESS VOICE WITH EFFECTS
def process_voice(audio_path, voice_slot):
    effects = VOICE_EFFECTS.get(voice_slot, {})
    slot_dir= os.path.join(VOICE_PROFILES_DIR, voice_slot)

    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=22050)

        print(f"\n  Applying effects for [{voice_slot}]:")
        print(f"   {effects.get('description', '')}")

        # ── Pitch shift ──
        pitch = effects.get("pitch_shift", 0)
        if pitch != 0:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch)
            print(f"   ✓ Pitch shifted: {pitch} semitones")

        # ── Speed change ──
        speed = effects.get("speed", 1.0)
        if speed != 1.0:
            y = librosa.effects.time_stretch(y, rate=speed)
            print(f"   ✓ Speed changed: {speed}x")

        # ── Tremolo (for old person) ──
        if effects.get("tremolo"):
            y = apply_tremolo(y, sr, rate=5.0, depth=0.4)
            print(f"   ✓ Tremolo applied (aged voice)")

        # ── Reverb (for narrator and ghost) ──
        if effects.get("reverb"):
            y = apply_reverb(y, sr, decay=0.4)
            print(f"   ✓ Reverb applied (echo effect)")

        # ── Echo (for ghost only) ──
        if effects.get("echo"):
            y = apply_echo(y, sr, delay=0.3, decay=0.5)
            print(f"   ✓ Echo applied (ghostly effect)")

        # Normalize audio
        y = librosa.util.normalize(y)

        # Save processed audio
        processed_path = os.path.join(slot_dir, "processed.wav")
        sf.write(processed_path, y, sr)

        return processed_path

    except Exception as e:
        print(f" Voice processing error: {e}")
        return None

# AUDIO EFFECTS
def apply_tremolo(y, sr, rate=5.0, depth=0.4):
    t       = np.linspace(0, len(y)/sr, len(y))
    tremolo = 1.0 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    return y * tremolo


def apply_reverb(y, sr, decay=0.4, num_echoes=4):
    result     = y.copy().astype(np.float64)
    delay_samp = int(sr * 0.05)   # 50ms delay

    for i in range(1, num_echoes + 1):
        delay  = delay_samp * i
        scaled = (y * (decay ** i)).astype(np.float64)
        if delay < len(result):
            result[delay:] += scaled[:len(result)-delay]

    return librosa.util.normalize(result).astype(np.float32)


def apply_echo(y, sr, delay=0.3, decay=0.5):
    delay_samp = int(sr * delay)
    result     = y.copy().astype(np.float64)
    if delay_samp < len(y):
        result[delay_samp:] += (y[:len(y)-delay_samp] * decay).astype(np.float64)
    return librosa.util.normalize(result).astype(np.float32)

# GET PROCESSED VOICE PATH
def get_voice_path(voice_slot):
    slot_dir       = os.path.join(VOICE_PROFILES_DIR, voice_slot)
    processed_path = os.path.join(slot_dir, "processed.wav")
    original_paths = [
        os.path.join(slot_dir, f"original{ext}")
        for ext in [".mp3", ".wav", ".ogg", ".m4a"]
    ]

    if os.path.exists(processed_path):
        return processed_path

    for path in original_paths:
        if os.path.exists(path):
            return path

    return None


# CHECK ALL VOICES
def check_voices():
    print("\n" + "="*60)
    print("🎙️  VOICE PROFILES STATUS")
    print("="*60)

    all_ready = True
    for slot, description in VOICE_SLOTS.items():
        path = get_voice_path(slot)
        if path:
            size = os.path.getsize(path) / 1024
            print(f"   {description}")
            print(f"     → {path} ({size:.1f} KB)")
        else:
            print(f"   {description}")
            print(f"     → Not uploaded yet")
            all_ready = False

    print("="*60)
    if all_ready:
        print(" All voices ready!\n")
    else:
        print("  Some voices missing — gTTS will be used as fallback\n")

    return all_ready

# VOICE UPLOAD MENU
def voice_upload_menu():
    print("\n" + "="*60)
    print("  UPLOAD YOUR VOICE PROFILES")
    print("="*60)
    print("  Upload audio files for each voice role.")
    print("  Supported formats: .mp3 .wav .ogg .m4a")
    print("  Recommended: 5-30 seconds of clear speech")
    print("="*60)

    for i, (slot, description) in enumerate(VOICE_SLOTS.items(), 1):
        current = get_voice_path(slot)
        status  = " uploaded" if current else " not uploaded"
        print(f"\n  {i}. {description} [{status}]")

    print("\n  0. Back")
    print("="*60)

    choice = input("\n  Which voice to upload? (1-5): ").strip()
    slots  = list(VOICE_SLOTS.keys())

    if choice == "0":
        return

    if not choice.isdigit() or int(choice) < 1 or int(choice) > 5:
        print("  Invalid choice")
        return

    slot        = slots[int(choice) - 1]
    description = VOICE_SLOTS[slot]

    print(f"\n  Uploading for: {description}")
    print(f"  Enter the FULL path to your audio file:")
    print(f"  Example: C:\\Users\\mishr\\Downloads\\my_voice.mp3")

    file_path = input("\n  File path: ").strip().strip('"')

    if not os.path.exists(file_path):
        print(f" File not found: {file_path}")
        return

    print(f"\n  Processing your voice with effects...")
    success = save_voice(file_path, slot)

    if success:
        print(f"\n Voice profile saved for: {description}")
        print(f"   Effects applied: {VOICE_EFFECTS[slot]['description']}")

# MAIN — for testing
if __name__ == "__main__":
    check_voices()
    voice_upload_menu()