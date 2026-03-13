import os
import time
import threading
import urllib.request

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
MUSIC_DIR = "backend/features/horror_music"
os.makedirs(MUSIC_DIR, exist_ok=True)

# ─────────────────────────────────────────
# FREE HORROR MUSIC URLS
# These are public domain/creative commons
# horror ambient sounds from freesound.org
# ─────────────────────────────────────────
HORROR_MUSIC_URLS = {
    "dark_ambient": {
        "name"  : "Dark Ambient Horror",
        "url"   : "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3",
        "file"  : "dark_ambient.mp3"
    },
    "horror_wind": {
        "name"  : "Horror Wind",
        "url"   : "https://www.soundjay.com/nature/sounds/wind-02.mp3",
        "file"  : "horror_wind.mp3"
    },
    "night_ambience": {
        "name"  : "Night Ambience",
        "url"   : "https://www.soundjay.com/nature/sounds/crickets-1.mp3",
        "file"  : "night_ambience.mp3"
    }
}

# Category to music mood mapping
CATEGORY_MUSIC = {
    "ghost"         : "dark_ambient",
    "witch"         : "dark_ambient",
    "haunted_house" : "horror_wind",
    "graveyard"     : "dark_ambient",
    "demon"         : "dark_ambient",
    "vampire"       : "dark_ambient",
    "cursed_object" : "horror_wind",
    "possessed"     : "dark_ambient",
    "general_horror": "night_ambience"
}

# Global music state
_music_playing  = False
_music_thread   = None
_stop_music     = False


# ─────────────────────────────────────────
# CHECK PYGAME
# ─────────────────────────────────────────
def check_pygame():
    try:
        import pygame
        return True
    except ImportError:
        print("❌ pygame not installed")
        print("   Run: pip install pygame==2.5.2")
        return False


# ─────────────────────────────────────────
# DOWNLOAD MUSIC FILE
# ─────────────────────────────────────────
def download_music(music_key):
    if music_key not in HORROR_MUSIC_URLS:
        return None

    music_info = HORROR_MUSIC_URLS[music_key]
    filepath   = os.path.join(MUSIC_DIR, music_info["file"])

    if os.path.exists(filepath):
        return filepath

    print(f"📥 Downloading {music_info['name']}...")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        req     = urllib.request.Request(music_info["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(filepath, "wb") as f:
                f.write(response.read())
        print(f"✅ Downloaded → {filepath}")
        return filepath
    except Exception as e:
        print(f"⚠️  Download failed: {e}")
        print("   You can manually add .mp3 files to:")
        print(f"   {MUSIC_DIR}/")
        return None


# ─────────────────────────────────────────
# GET LOCAL MUSIC FILES
# ─────────────────────────────────────────
def get_local_music():
    files = [
        f for f in os.listdir(MUSIC_DIR)
        if f.endswith(".mp3") or f.endswith(".wav") or f.endswith(".ogg")
    ]
    return files


# ─────────────────────────────────────────
# PLAY BACKGROUND MUSIC
# ─────────────────────────────────────────
def play_background_music(category="general_horror", volume=0.3):
    global _music_playing, _stop_music

    if not check_pygame():
        return False

    import pygame

    # Get music key for category
    music_key = CATEGORY_MUSIC.get(category, "night_ambience")

    # Try to get music file
    filepath = None

    # First check local files
    local_files = get_local_music()
    if local_files:
        filepath = os.path.join(MUSIC_DIR, local_files[0])

    # Try download if no local files
    if not filepath:
        filepath = download_music(music_key)

    if not filepath or not os.path.exists(filepath):
        print("⚠️  No music file available")
        print(f"   Add .mp3 files to: {MUSIC_DIR}/")
        print("   Music will be skipped\n")
        return False

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=-1)    # loop forever

        _music_playing = True
        _stop_music    = False

        print(f"🎵 Background horror music playing (volume: {int(volume*100)}%)")
        print("   Music will stop when story ends\n")
        return True

    except Exception as e:
        print(f"⚠️  Music error: {e}\n")
        return False


# ─────────────────────────────────────────
# STOP BACKGROUND MUSIC
# ─────────────────────────────────────────
def stop_background_music():
    global _music_playing

    if not check_pygame():
        return

    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.fadeout(2000)   # 2 second fadeout
            time.sleep(2)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            _music_playing = False
            print("🎵 Music stopped\n")
    except Exception as e:
        print(f"⚠️  Stop music error: {e}")


# ─────────────────────────────────────────
# FADE OUT MUSIC
# ─────────────────────────────────────────
def fadeout_music(duration_ms=3000):
    try:
        import pygame
        if pygame.mixer.get_init() and _music_playing:
            pygame.mixer.music.fadeout(duration_ms)
            time.sleep(duration_ms / 1000)
    except:
        pass


# ─────────────────────────────────────────
# SET VOLUME
# ─────────────────────────────────────────
def set_volume(volume):
    try:
        import pygame
        volume = max(0.0, min(1.0, volume))
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(volume)
            print(f"🔊 Volume set to {int(volume*100)}%")
    except Exception as e:
        print(f"⚠️  Volume error: {e}")


# ─────────────────────────────────────────
# MUSIC MENU
# ─────────────────────────────────────────
def music_menu(category="general_horror"):
    print("\n" + "="*60)
    print("🎵 BACKGROUND MUSIC OPTIONS")
    print("="*60)
    print("  1. Play horror music while reading (low volume)")
    print("  2. Play horror music while reading (medium volume)")
    print("  3. No background music")
    print("="*60)

    choice = input("\n  Choose option (1/2/3): ").strip()

    if choice == "1":
        return play_background_music(category, volume=0.2)
    elif choice == "2":
        return play_background_music(category, volume=0.4)
    else:
        print("🔇 No background music\n")
        return False


# ─────────────────────────────────────────
# ADD YOUR OWN MUSIC INSTRUCTIONS
# ─────────────────────────────────────────
def show_music_instructions():
    print("\n" + "="*60)
    print("🎵 HOW TO ADD YOUR OWN HORROR MUSIC")
    print("="*60)
    print(f"  Add .mp3 or .wav files to:")
    print(f"  {MUSIC_DIR}/")
    print()
    print("  Free horror music sources:")
    print("  → freesound.org (search: horror ambient)")
    print("  → pixabay.com/music (search: dark horror)")
    print("  → mixkit.co/free-music (horror section)")
    print("  → zapsplat.com (horror ambience)")
    print()
    print("  Recommended files to download:")
    print("  → dark_ambient.mp3")
    print("  → horror_wind.mp3")
    print("  → creepy_music_box.mp3")
    print("  → haunted_house.mp3")
    print("="*60 + "\n")


# ─────────────────────────────────────────
# MAIN — for testing
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n🎵 Testing Music Player\n")

    show_music_instructions()

    local = get_local_music()
    if local:
        print(f"✅ Found {len(local)} local music files:")
        for f in local:
            print(f"   → {f}")

        print("\nPlaying music for 5 seconds...")
        play_background_music("ghost", volume=0.3)
        time.sleep(5)
        stop_background_music()
    else:
        print(f"⚠️  No music files found in {MUSIC_DIR}/")
        print("   Add .mp3 files there to enable music!")
        show_music_instructions()