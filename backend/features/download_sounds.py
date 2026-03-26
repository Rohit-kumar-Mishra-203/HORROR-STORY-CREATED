import os
import urllib.request

SOUNDS_DIR = "backend/features/horror_sounds"
os.makedirs(SOUNDS_DIR, exist_ok=True)

# ─────────────────────────────────────────
# FREE HORROR SOUND URLS
# All from freesound.org / pixabay (public domain)
# ─────────────────────────────────────────
SOUND_URLS = {
    "thunder"           : "https://www.soundjay.com/nature/sounds/thunder-01.mp3",
    "wind_howling"      : "https://www.soundjay.com/nature/sounds/wind-02.mp3",
    "door_creaking"     : "https://www.soundjay.com/door/sounds/door-creaking-1.mp3",
    "footsteps"         : "https://www.soundjay.com/human/sounds/footsteps-1.mp3",
    "wolf_howling"      : "https://pixabay.com/sound-effects/search/wolf%20howling/",
    "clock_ticking"     : "https://www.soundjay.com/clock/sounds/clock-ticking-1.mp3",
    "glass_breaking"    : "https://www.soundjay.com/misc/sounds/glass-breaking-1.mp3",
    "chains_rattling"   : "https://www.soundjay.com/misc/sounds/chains-1.mp3",
    "evil_laugh"        : "https://www.soundjay.com/human/sounds/evil-laugh-1.mp3",
    "ghost_whisper"     : "https://www.soundjay.com/human/sounds/whisper-1.mp3",
    "heartbeat"         : "https://www.soundjay.com/human/sounds/heartbeat-1.mp3",
    "owl_hooting"       : "https://www.soundjay.com/animals/sounds/owl-1.mp3",
    "fire_crackling"    : "https://www.soundjay.com/nature/sounds/fire-1.mp3",
    "screaming_distance": "https://www.soundjay.com/human/sounds/scream-1.mp3",
    "crow_cawing"       : "https://www.soundjay.com/animals/sounds/crow-1.mp3",
    "rain_pouring"      : "https://www.soundjay.com/nature/sounds/rain-1.mp3",
    "church_bell"       : "https://www.soundjay.com/misc/sounds/bell-1.mp3",
    "dog_barking"       : "https://www.soundjay.com/animals/sounds/dog-barking-1.mp3",
    "water_dripping"    : "https://www.soundjay.com/nature/sounds/water-dripping-1.mp3",
    "knife_scraping"    : "https://www.soundjay.com/misc/sounds/knife-1.mp3",
}


def download_all():
    print("\n" + "="*60)
    print("📥 DOWNLOADING HORROR SOUNDS")
    print("="*60)

    success = 0
    failed  = []

    for name, url in SOUND_URLS.items():
        filepath = os.path.join(SOUNDS_DIR, f"{name}.mp3")

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  ✅ Already exists: {name}.mp3")
            success += 1
            continue

        try:
            print(f"  📥 Downloading: {name}.mp3 ...")
            headers = {"User-Agent": "Mozilla/5.0"}
            req     = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            with open(filepath, "wb") as f:
                f.write(data)
            size = os.path.getsize(filepath) / 1024
            print(f"  ✅ Downloaded : {name}.mp3 ({size:.1f} KB)")
            success += 1
        except Exception as e:
            print(f"  ❌ Failed     : {name}.mp3 — {e}")
            failed.append(name)

    print("\n" + "="*60)
    print(f"  ✅ Downloaded : {success}/{len(SOUND_URLS)}")
    if failed:
        print(f"  ❌ Failed     : {', '.join(failed)}")
        print(f"\n  For failed sounds manually download from:")
        print(f"  https://pixabay.com/sound-effects/")
        print(f"  Save to: {SOUNDS_DIR}/")
    print("="*60 + "\n")


if __name__ == "__main__":
    download_all()