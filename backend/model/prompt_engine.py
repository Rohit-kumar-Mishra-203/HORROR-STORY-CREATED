import re

# CATEGORY KEYWORDS


CATEGORIES = {

    "witch": {
        "keywords_english": [
            "witch", "witches", "witchcraft", "spell", "coven",
            "cauldron", "hex", "curse", "broomstick", "sorcery"
        ],
        "keywords_hindi": [
            "चुड़ैल", "डायन", "जादूगरनी", "टोना", "टोटका",
            "जादू", "मंत्र", "तंत्र", "जादुई"
        ],
        "hindi_starter": "घने जंगल में एक बूढ़ी चुड़ैल रहती थी जिसके बारे में गाँव वाले कानाफूसी करते थे।",
        "english_starter": "Deep in the forest lived an old witch whose name was never spoken aloud after dark."
    },

    "ghost": {
        "keywords_english": [
            "ghost", "spirit", "haunted", "apparition", "phantom",
            "specter", "poltergeist", "supernatural", "spooky", "haunt"
        ],
        "keywords_hindi": [
            "भूत", "प्रेत", "आत्मा", "भूतिया", "प्रेतात्मा",
            "भटकती", "मुर्दा", "मृत आत्मा", "भूत प्रेत"
        ],
        "hindi_starter": "रात के अंधेरे में उस पुराने घर से भूत की आवाज़ें आती थीं जिन्हें सुनकर सब काँप जाते थे।",
        "english_starter": "The ghost had been haunting the old house for decades and no one who entered after midnight ever came back the same."
    },

    "haunted_house": {
        "keywords_english": [
            "haunted house", "haunted mansion", "old house", "abandoned house",
            "haunted building", "haunted room", "haunted place", "haunted mansion"
        ],
        "keywords_hindi": [
            "हवेली", "पुराना घर", "भूतिया घर", "वीरान घर",
            "खंडहर", "पुरानी इमारत", "बंद घर", "सूना घर"
        ],
        "hindi_starter": "उस पुरानी हवेली में सालों से कोई नहीं रहता था पर हर रात उसकी खिड़कियों में रोशनी दिखती थी।",
        "english_starter": "The old mansion at the end of the road had been empty for thirty years but every night lights could be seen moving behind its dusty windows."
    },

    "graveyard": {
        "keywords_english": [
            "graveyard", "cemetery", "grave", "tomb", "burial",
            "coffin", "dead", "corpse", "skull", "bones", "crypt"
        ],
        "keywords_hindi": [
            "कब्रिस्तान", "कब्र", "मुर्दाघर", "शमशान", "चिता",
            "मृत", "लाश", "कंकाल", "हड्डियाँ", "दफन"
        ],
        "hindi_starter": "कब्रिस्तान की काली रात में जब सब सो जाते थे तब कब्रों से अजीब आवाज़ें आने लगती थीं।",
        "english_starter": "The old graveyard at the edge of town was the kind of place where the dead did not always stay dead."
    },

    "demon": {
        "keywords_english": [
            "demon", "devil", "satan", "evil spirit", "hellish",
            "possessed", "dark entity", "evil force", "demonic", "beast"
        ],
        "keywords_hindi": [
            "राक्षस", "शैतान", "असुर", "दैत्य", "दानव",
            "बुरी आत्मा", "अदृश्य शक्ति", "काली शक्ति", "भूत प्रेत"
        ],
        "hindi_starter": "वो राक्षस सदियों से उस जगह का इंतज़ार कर रहा था जब कोई बेवकूफ उसे जगाने की गलती करे।",
        "english_starter": "The demon had been sealed beneath the ancient stone for a thousand years waiting for the one who would be foolish enough to break the seal."
    },

    "vampire": {
        "keywords_english": [
            "vampire", "vampires", "blood", "fangs", "undead",
            "immortal", "night creature", "bloodsucker", "dracula"
        ],
        "keywords_hindi": [
            "पिशाच", "रक्तपिपासु", "खून पीने वाला", "अमर प्राणी",
            "रात का राक्षस", "वैम्पायर", "खून", "नुकीले दाँत"
        ],
        "hindi_starter": "वो पिशाच सैकड़ों सालों से उस कस्बे में छुपा था और हर पूर्णिमा की रात किसी न किसी का खून पीता था।",
        "english_starter": "The vampire had lived among them for centuries feeding only when the hunger became too great to ignore and always moving on before anyone could suspect."
    },

    "cursed_object": {
        "keywords_english": [
            "cursed", "curse", "cursed object", "ancient artifact",
            "haunted object", "evil doll", "cursed ring", "dark relic",
            "possessed object", "haunted painting", "cursed mirror"
        ],
        "keywords_hindi": [
            "श्राप", "शापित", "呪われた वस्तु", "पुरानी चीज़",
            "शापित अंगूठी", "शापित तस्वीर", "भूतिया गुड़िया",
            "शापित आईना", "काली वस्तु", "शाप"
        ],
        "hindi_starter": "वो पुरानी चीज़ बाज़ार में मिली थी पर जब से घर में आई थी तब से सब कुछ बदल गया था।",
        "english_starter": "The moment she brought the antique home she knew something was wrong but by then it was already too late to get rid of it."
    },

    "possessed": {
        "keywords_english": [
            "possessed", "possession", "taken over", "evil inside",
            "body snatched", "not themselves", "something inside",
            "controlled", "invaded", "overtaken"
        ],
        "keywords_hindi": [
            "भूत चढ़ना", "आवेश", "ऊपरी हवा", "भूत सवार",
            "शरीर में घुसना", "काबू करना", "बस में होना",
            "जिन्न", "ओझा", "झाड़ फूँक"
        ],
        "hindi_starter": "जब से उसके शरीर में वो आत्मा घुसी थी तब से वो बिल्कुल बदल गया था और उसकी आँखों में एक अजीब चमक आ गई थी।",
        "english_starter": "Everyone noticed the change in him the morning after he visited the abandoned church but nobody wanted to say what they were all thinking."
    },

    "general_horror": {
        "keywords_english": [
            "horror", "scary", "terrifying", "frightening", "creepy",
            "disturbing", "nightmare", "dark", "evil", "fear",
            "story", "tale", "haunted", "spooky"
        ],
        "keywords_hindi": [
            "डरावनी", "भयानक", "खौफनाक", "रोंगटे", "डर",
            "कहानी", "कहो", "सुनाओ", "बताओ", "लिखो",
            "horror", "scary"
        ],
        "hindi_starter": "रात के अंधेरे में जो हुआ उसे याद करके आज भी रोंगटे खड़े हो जाते हैं।",
        "english_starter": "It was the kind of night when something feels wrong before anything has actually happened."
    }
}

# DETECT LANGUAGE

def detect_language(text):
    hindi_chars = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    total_chars = len(text.replace(" ", ""))
    if total_chars == 0:
        return "english"
    ratio = hindi_chars / total_chars
    return "hindi" if ratio > 0.3 else "english"

# DETECT CATEGORY

def detect_category(text, language):
    text_lower = text.lower()

    for category, data in CATEGORIES.items():
        if category == "general_horror":
            continue

        keywords = (
            data["keywords_hindi"]
            if language == "hindi"
            else data["keywords_english"]
        )

        for keyword in keywords:
            if keyword.lower() in text_lower:
                return category

    # Check general horror keywords
    general = CATEGORIES["general_horror"]
    keywords = (
        general["keywords_hindi"]
        if language == "hindi"
        else general["keywords_english"]
    )
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return "general_horror"

    return "general_horror"

# BUILD SMART PROMPT

def build_prompt(user_input, language, category):
    data    = CATEGORIES[category]
    starter = data["hindi_starter"] if language == "hindi" else data["english_starter"]

    # If user gave a very short/vague prompt like
    # "give me a witch story" → use category starter directly
    word_count = len(user_input.split())

    if word_count <= 8:
        # Short vague prompt → use predefined starter
        final_prompt = starter
    else:
        # Detailed prompt → use as is
        final_prompt = user_input

    return final_prompt, category

# MAIN FUNCTION — called from generate.py

def process_user_input(user_input):
    language          = detect_language(user_input)
    category          = detect_category(user_input, language)
    prompt, category  = build_prompt(user_input, language, category)

    category_names = {
        "witch"         : " Witch Story",
        "ghost"         : " Ghost Story",
        "haunted_house" : " Haunted House",
        "graveyard"     : " Graveyard Story",
        "demon"         : " Demon Story",
        "vampire"       : " Vampire Story",
        "cursed_object" : " Cursed Object",
        "possessed"     : " Possessed Person",
        "general_horror": " Horror Story",
    }

    print(f"\n Detected Language : {language.upper()}")
    print(f" Detected Category : {category_names.get(category, category)}")
    print(f" Using Prompt      : {prompt[:80]}...\n")

    return prompt, language, category