from backend.model.story_templates.ghost_templates          import GHOST_HINDI, GHOST_ENGLISH
from backend.model.story_templates.haunted_house_templates  import HAUNTED_HOUSE_HINDI, HAUNTED_HOUSE_ENGLISH
from backend.model.story_templates.graveyard_templates      import GRAVEYARD_HINDI, GRAVEYARD_ENGLISH
from backend.model.story_templates.demon_templates          import DEMON_HINDI, DEMON_ENGLISH
from backend.model.story_templates.vampire_templates        import VAMPIRE_HINDI, VAMPIRE_ENGLISH
from backend.model.story_templates.monster_templates        import MONSTER_HINDI, MONSTER_ENGLISH
from backend.model.story_templates.cursed_object_templates  import CURSED_OBJECT_HINDI, CURSED_OBJECT_ENGLISH
from backend.model.story_templates.possessed_templates      import POSSESSED_HINDI, POSSESSED_ENGLISH
from backend.model.story_templates.general_horror_templates import GENERAL_HORROR_HINDI, GENERAL_HORROR_ENGLISH

# ─────────────────────────────────────────
# ALL TEMPLATES
# ─────────────────────────────────────────
HINDI_TEMPLATES = {
    "ghost"         : GHOST_HINDI,
    "haunted_house" : HAUNTED_HOUSE_HINDI,
    "graveyard"     : GRAVEYARD_HINDI,
    "demon"         : DEMON_HINDI,
    "vampire"       : VAMPIRE_HINDI,
    "monster"       : MONSTER_HINDI,
    "cursed_object" : CURSED_OBJECT_HINDI,
    "possessed"     : POSSESSED_HINDI,
    "general_horror": GENERAL_HORROR_HINDI,
}

ENGLISH_TEMPLATES = {
    "ghost"         : GHOST_ENGLISH,
    "haunted_house" : HAUNTED_HOUSE_ENGLISH,
    "graveyard"     : GRAVEYARD_ENGLISH,
    "demon"         : DEMON_ENGLISH,
    "vampire"       : VAMPIRE_ENGLISH,
    "monster"       : MONSTER_ENGLISH,
    "cursed_object" : CURSED_OBJECT_ENGLISH,
    "possessed"     : POSSESSED_ENGLISH,
    "general_horror": GENERAL_HORROR_ENGLISH,
}


def get_template(language, category):
    import random
    templates = (
        HINDI_TEMPLATES if language == "hindi"
        else ENGLISH_TEMPLATES
    )
    category_templates = templates.get(
        category,
        GENERAL_HORROR_HINDI if language == "hindi"
        else GENERAL_HORROR_ENGLISH
    )
    return random.choice(category_templates)


def get_all_categories():
    return list(HINDI_TEMPLATES.keys())


def get_template_count(language, category):
    templates = (
        HINDI_TEMPLATES if language == "hindi"
        else ENGLISH_TEMPLATES
    )
    return len(templates.get(category, []))