import os
import json
import random
from datetime import datetime

# CONFIG

LIBRARY_DIR  = "story_library"
LIBRARY_FILE = "story_library/stories.json"

# INITIALIZE LIBRARY

def init_library():
    os.makedirs(LIBRARY_DIR, exist_ok=True)
    if not os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    return load_library()

# LOAD LIBRARY

def load_library():
    if not os.path.exists(LIBRARY_FILE):
        return []
    with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# SAVE LIBRARY

def save_library(stories):
    os.makedirs(LIBRARY_DIR, exist_ok=True)
    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

# ADD STORY

def add_story(prompt, story, language, category, rating=None):
    stories  = load_library()
    story_id = len(stories) + 1

    new_story = {
        "id"        : story_id,
        "prompt"    : prompt,
        "story"     : story,
        "language"  : language,
        "category"  : category,
        "rating"    : rating,
        "date"      : datetime.now().strftime("%Y-%m-%d %H:%M"),
        "favorite"  : False,
        "word_count": len(story.split())
    }

    stories.append(new_story)
    save_library(stories)

    print(f"\n Story saved to library! ID: #{story_id}")
    return story_id

# RATE STORY

def rate_story(story_id, rating):
    if rating < 1 or rating > 5:
        print("  Rating must be between 1 and 5")
        return False

    stories = load_library()
    for story in stories:
        if story["id"] == story_id:
            story["rating"] = rating
            save_library(stories)
            stars = "⭐" * rating
            print(f"\n Story #{story_id} rated {stars}")
            return True

    print(f" Story #{story_id} not found")
    return False

# MARK AS FAVORITE

def toggle_favorite(story_id):
    stories = load_library()
    for story in stories:
        if story["id"] == story_id:
            story["favorite"] = not story["favorite"]
            save_library(stories)
            status = "  Added to" if story["favorite"] else " Removed from"
            print(f"\n{status} favorites! Story #{story_id}")
            return True

    print(f" Story #{story_id} not found")
    return False

# VIEW ALL STORIES

def view_all_stories():
    stories = load_library()

    if not stories:
        print("\n Library is empty. Generate some stories first!\n")
        return

    print("\n" + "="*60)
    print(" YOUR STORY LIBRARY")
    print("="*60)

    for s in stories:
        stars    = "⭐" * s["rating"] if s["rating"] else "not rated"
        fav      = " " if s["favorite"] else "   "
        lang     = "🇮🇳" if s["language"] == "hindi" else "🇬🇧"
        category = s["category"].replace("_", " ").title()

        print(f"\n{fav}#{s['id']} {lang} [{category}]")
        print(f"    {s['date']}  |   {s['word_count']} words  |  {stars}")
        print(f"    {s['prompt'][:60]}...")

    print("\n" + "="*60)
    print(f"Total stories: {len(stories)}")
    rated     = [s for s in stories if s["rating"]]
    if rated:
        avg = sum(s["rating"] for s in rated) / len(rated)
        print(f"Average rating: {avg:.1f} ⭐")
    print("="*60 + "\n")

# VIEW SINGLE STORY

def view_story(story_id):
    stories = load_library()

    for s in stories:
        if s["id"] == story_id:
            lang     = "🇮🇳 Hindi" if s["language"] == "hindi" else "🇬🇧 English"
            stars    = "" * s["rating"] if s["rating"] else "Not rated"
            category = s["category"].replace("_", " ").title()
            fav      = "  Favorite" if s["favorite"] else ""

            print("\n" + "="*60)
            print(f" STORY #{s['id']} {fav}")
            print("="*60)
            print(f"Language  : {lang}")
            print(f"Category  : {category}")
            print(f"Date      : {s['date']}")
            print(f"Words     : {s['word_count']}")
            print(f"Rating    : {stars}")
            print(f"Prompt    : {s['prompt']}")
            print("-"*60)
            print(f"\n{s['story']}\n")
            print("="*60)
            return True

    print(f" Story #{story_id} not found")
    return False

# VIEW FAVORITES

def view_favorites():
    stories   = load_library()
    favorites = [s for s in stories if s["favorite"]]

    if not favorites:
        print("\n  No favorites yet! Mark stories as favorite to see them here.\n")
        return

    print("\n" + "="*60)
    print("  YOUR FAVORITE STORIES")
    print("="*60)

    for s in favorites:
        stars    = "⭐" * s["rating"] if s["rating"] else "not rated"
        lang     = "🇮🇳" if s["language"] == "hindi" else "🇬🇧"
        category = s["category"].replace("_", " ").title()
        print(f"\n#{s['id']} {lang} [{category}] — {stars}")
        print(f"    {s['prompt'][:60]}...")

    print(f"\nTotal favorites: {len(favorites)}")
    print("="*60 + "\n")

# SEARCH STORIES

def search_stories(keyword):
    stories = load_library()
    results = [
        s for s in stories
        if keyword.lower() in s["prompt"].lower()
        or keyword.lower() in s["story"].lower()
        or keyword.lower() in s["category"].lower()
    ]

    if not results:
        print(f"\n No stories found for '{keyword}'\n")
        return

    print(f"\n Found {len(results)} stories for '{keyword}':\n")
    for s in results:
        lang     = "🇮🇳" if s["language"] == "hindi" else "🇬🇧"
        category = s["category"].replace("_", " ").title()
        stars    = "⭐" * s["rating"] if s["rating"] else "not rated"
        print(f"#{s['id']} {lang} [{category}] — {stars}")
        print(f"    {s['prompt'][:60]}...\n")

# FILTER BY CATEGORY

def filter_by_category(category):
    stories = load_library()
    results = [s for s in stories if s["category"] == category]

    if not results:
        print(f"\n No stories found in category: {category}\n")
        return

    print(f"\n Stories in '{category}':\n")
    for s in results:
        lang  = "🇮🇳" if s["language"] == "hindi" else "🇬🇧"
        stars = "⭐" * s["rating"] if s["rating"] else "not rated"
        print(f"#{s['id']} {lang} — {stars}")
        print(f"    {s['prompt'][:60]}...\n")

# FILTER BY LANGUAGE

def filter_by_language(language):
    stories = load_library()
    results = [s for s in stories if s["language"] == language]

    if not results:
        print(f"\n No {language} stories found\n")
        return

    print(f"\n{'🇮🇳' if language == 'hindi' else '🇬🇧'} {language.title()} Stories:\n")
    for s in results:
        category = s["category"].replace("_", " ").title()
        stars    = "⭐" * s["rating"] if s["rating"] else "not rated"
        print(f"#{s['id']} [{category}] — {stars}")
        print(f"    {s['prompt'][:60]}...\n")

# GET TOP RATED

def get_top_rated(limit=5):
    stories = load_library()
    rated   = [s for s in stories if s["rating"]]

    if not rated:
        print("\n No rated stories yet!\n")
        return

    top = sorted(rated, key=lambda x: x["rating"], reverse=True)[:limit]

    print(f"\n TOP {limit} RATED STORIES\n")
    print("="*60)
    for i, s in enumerate(top):
        stars    = "⭐" * s["rating"]
        lang     = "🇮🇳" if s["language"] == "hindi" else "🇬🇧"
        category = s["category"].replace("_", " ").title()
        print(f"{i+1}. #{s['id']} {lang} {stars} [{category}]")
        print(f"    {s['prompt'][:60]}...")
    print("="*60 + "\n")

# DELETE STORY

def delete_story(story_id):
    stories  = load_library()
    filtered = [s for s in stories if s["id"] != story_id]

    if len(filtered) == len(stories):
        print(f" Story #{story_id} not found")
        return False

    save_library(filtered)
    print(f"  Story #{story_id} deleted from library")
    return True

# LIBRARY STATS

def show_stats():
    stories = load_library()

    if not stories:
        print("\n Library is empty\n")
        return

    total      = len(stories)
    hindi      = len([s for s in stories if s["language"] == "hindi"])
    english    = len([s for s in stories if s["language"] == "english"])
    favorites  = len([s for s in stories if s["favorite"]])
    rated      = [s for s in stories if s["rating"]]
    avg_rating = sum(s["rating"] for s in rated) / len(rated) if rated else 0
    total_words= sum(s["word_count"] for s in stories)

    categories = {}
    for s in stories:
        cat = s["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\n" + "="*60)
    print(" LIBRARY STATISTICS")
    print("="*60)
    print(f"  Total stories    : {total}")
    print(f"  🇮🇳 Hindi stories : {hindi}")
    print(f"  🇬🇧 English stories: {english}")
    print(f"    Favorites      : {favorites}")
    print(f"  ⭐ Avg rating     : {avg_rating:.1f}")
    print(f"   Total words    : {total_words:,}")
    print(f"\n   By Category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        cat_name = cat.replace("_", " ").title()
        print(f"     {cat_name}: {count}")
    print("="*60 + "\n")

# INTERACTIVE LIBRARY MENU

def library_menu():
    init_library()

    while True:
        print("\n" + "="*60)
        print(" STORY LIBRARY")
        print("="*60)
        print("  1. View all stories")
        print("  2. View a story")
        print("  3. Rate a story")
        print("  4. Mark as favorite")
        print("  5. View favorites")
        print("  6. Search stories")
        print("  7. Filter by category")
        print("  8. Filter by language")
        print("  9. Top rated stories")
        print("  10. Library statistics")
        print("  11. Delete a story")
        print("  0. Back to main menu")
        print("="*60)

        choice = input("\n  Choose option: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            view_all_stories()

        elif choice == "2":
            story_id = input("  Enter story ID: ").strip()
            if story_id.isdigit():
                view_story(int(story_id))

        elif choice == "3":
            story_id = input("  Enter story ID: ").strip()
            rating   = input("  Enter rating (1-5): ").strip()
            if story_id.isdigit() and rating.isdigit():
                rate_story(int(story_id), int(rating))

        elif choice == "4":
            story_id = input("  Enter story ID: ").strip()
            if story_id.isdigit():
                toggle_favorite(int(story_id))

        elif choice == "5":
            view_favorites()

        elif choice == "6":
            keyword = input("  Enter search keyword: ").strip()
            search_stories(keyword)

        elif choice == "7":
            print("  Categories: ghost, witch, haunted_house,")
            print("              graveyard, demon, vampire,")
            print("              cursed_object, possessed, general_horror")
            category = input("  Enter category: ").strip()
            filter_by_category(category)

        elif choice == "8":
            print("  1. Hindi  2. English")
            lang_choice = input("  Choose: ").strip()
            lang        = "hindi" if lang_choice == "1" else "english"
            filter_by_language(lang)

        elif choice == "9":
            get_top_rated()

        elif choice == "10":
            show_stats()

        elif choice == "11":
            story_id = input("  Enter story ID to delete: ").strip()
            if story_id.isdigit():
                confirm = input(f"  Delete story #{story_id}? (y/n): ").strip().lower()
                if confirm == "y":
                    delete_story(int(story_id))
        else:
            print("  Invalid option")

# MAIN — for testing

if __name__ == "__main__":
    library_menu()