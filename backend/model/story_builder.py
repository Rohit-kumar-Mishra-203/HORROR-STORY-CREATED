import random

# HINDI CHARACTER NAMES
HINDI_NAMES = {
    "male": [
        "राहुल", "विकास", "अर्जुन", "सुरेश", "रमेश",
        "अनिल", "मनोज", "दीपक", "संजय", "अमित",
        "रोहन", "विनोद", "प्रकाश", "महेश", "नरेश"
    ],
    "female": [
        "प्रिया", "नेहा", "सीमा", "शालिनी", "मीना",
        "कविता", "सुमित्रा", "रीया", "अनीता", "पूजा",
        "श्रेया", "निशा", "रेखा", "सुनीता", "ममता"
    ]
}

ENGLISH_NAMES = {
    "male": [
        "Daniel", "Marcus", "Victor", "Adrian", "Nathan",
        "Lucas", "Owen", "Julian", "Ethan", "Sebastian",
        "Ryan", "Derek", "Cole", "Blake", "Elliot"
    ],
    "female": [
        "Sarah", "Maya", "Clara", "Elena", "Nora",
        "Lydia", "Vivian", "Diana", "Rachel", "Iris",
        "Evelyn", "Aurora", "Celeste", "Mira", "Helena"
    ]
}

# CHARACTER BACKSTORIES
BACKSTORIES = {
    "hindi": [
        "जो पाँच साल से शहर में अकेला रह रहा था",
        "जिसकी माँ हाल ही में गुज़र गई थीं",
        "जो एक रहस्यमयी दुर्घटना से उबर रहा था",
        "जिसे बचपन से अजीब सपने आते थे",
        "जो एक पुरानी हवेली का नया मालिक बना था",
        "जो उस रात पहली बार उस गाँव में आया था",
        "जिसके परिवार में पीढ़ियों से एक राज़ था",
        "जो एक अधूरी कहानी की तलाश में निकला था"
    ],
    "english": [
        "who had been living alone for five years",
        "whose mother had just passed away",
        "who was recovering from a mysterious accident",
        "who had been having strange dreams since childhood",
        "who had just inherited the old estate",
        "who was visiting the town for the very first time",
        "whose family had kept a dark secret for generations",
        "who was searching for answers to an unfinished story"
    ]
}

# ATMOSPHERES
ATMOSPHERES = {
    "hindi": {
        "weather": [
            "आधी रात को जब घनघोर बारिश हो रही थी",
            "अमावस्या की काली रात में जब हवा बंद थी",
            "तूफान की रात जब बिजली चमक रही थी",
            "घने कोहरे में जब कुछ भी दिखाई नहीं देता था",
            "ठंडी सर्दी की रात जब साँस भी धुएँ की तरह निकलती थी",
            "बरसात की रात जब सड़कें सुनसान थीं"
        ],
        "location": [
            "उस वीरान गाँव के आखिरी घर में",
            "जंगल के बीचोबीच एक पुरानी हवेली में",
            "शहर से दूर एक टूटे हुए मंदिर के पास",
            "कब्रिस्तान की दीवार से लगे उस पुराने घर में",
            "पहाड़ी के ऊपर उस अकेले बंगले में",
            "नदी किनारे उस वीरान खंडहर में"
        ]
    },
    "english": {
        "weather": [
            "on a night when the rain hammered the windows without mercy",
            "on the darkest night of the new moon when no stars were visible",
            "during a thunderstorm that had knocked out the power for miles",
            "in a thick fog that swallowed everything beyond arm's reach",
            "on a freezing winter night when even the wind had gone silent",
            "when the storm had emptied the streets of every living soul"
        ],
        "location": [
            "in the last house at the edge of the abandoned village",
            "in an old mansion deep in the middle of the forest",
            "near a crumbling temple far from the nearest town",
            "in the old house that backed directly onto the cemetery",
            "in the lonely bungalow at the top of the hill",
            "in the ruins by the river that nobody visited anymore"
        ]
    }
}

# STORY STRUCTURE TEMPLATES
STRUCTURES = {
    "hindi": {
        "beginning": [
            "{character} {backstory}। {weather}, {character} को {location} जाना पड़ा।",
            "{weather}, {character} {backstory} अकेला था। उसे नहीं पता था कि {location} में उसका क्या इंतज़ार है।",
            "{character} {backstory}। आज रात {weather} वो {location} पहुँचा और उसे तुरंत एहसास हो गया कि कुछ गलत है।"
        ],
        "middle_transition": [
            "पर जैसे ही उसने अंदर कदम रखा",
            "तभी उसे पहली बार एहसास हुआ",
            "पहली रात सब ठीक लगा। पर दूसरी रात को",
            "उसने सोचा सब ठीक हो जाएगा। पर तभी",
            "जो हुआ उसके लिए वो बिल्कुल तैयार नहीं था"
        ],
        "ending_setup": [
            "और उस रात के बाद से",
            "जो सच्चाई सामने आई वो",
            "आखिरकार जब सब पता चला तो",
            "उस रात की सबसे डरावनी बात ये थी कि"
        ]
    },
    "english": {
        "beginning": [
            "{character} {backstory}. {weather}, {character} found himself at {location}.",
            "{weather}, {character} {backstory} was completely alone. He had no idea what was waiting at {location}.",
            "{character} {backstory}. Tonight, {weather}, he arrived at {location} and immediately knew something was wrong."
        ],
        "middle_transition": [
            "But the moment he stepped inside",
            "That was when he first realized",
            "The first night seemed fine. But on the second night",
            "He told himself everything would be alright. And then",
            "Nothing could have prepared him for what happened next"
        ],
        "ending_setup": [
            "And from that night onwards",
            "The truth that emerged was",
            "When everything was finally revealed",
            "The most terrifying part of that night was"
        ]
    }
}


# BUILD COMPLETE STORY PROMPT
def build_story_prompt(language, category):

    # Pick random character
    gender    = random.choice(["male", "female"])
    names     = HINDI_NAMES if language == "hindi" else ENGLISH_NAMES
    character = random.choice(names[gender])

    # Pick random backstory
    backstory = random.choice(BACKSTORIES[language])

    # Pick random atmosphere
    atm       = ATMOSPHERES[language]
    weather   = random.choice(atm["weather"])
    location  = random.choice(atm["location"])

    # Pick random structure
    struct    = STRUCTURES[language]
    beginning = random.choice(struct["beginning"])
    transition= random.choice(struct["middle_transition"])

    # Fill in template
    prompt = beginning.format(
        character = character,
        backstory = backstory,
        weather   = weather,
        location  = location
    )

    # Add transition hint
    full_prompt = f"{prompt} {transition}"

    return full_prompt, character, category


# GET STORY METADATA
def get_story_metadata(language, category):
    character_gender = random.choice(["male", "female"])
    names            = HINDI_NAMES if language == "hindi" else ENGLISH_NAMES
    character_name   = random.choice(names[character_gender])
    backstory        = random.choice(BACKSTORIES[language])
    weather          = random.choice(ATMOSPHERES[language]["weather"])
    location         = random.choice(ATMOSPHERES[language]["location"])

    return {
        "character" : character_name,
        "gender"    : character_gender,
        "backstory" : backstory,
        "weather"   : weather,
        "location"  : location,
        "language"  : language,
        "category"  : category
    }


# MAIN — for testing
if __name__ == "__main__":
    print("\n Testing Story Builder\n")
    print("="*60)

    print("HINDI PROMPT:")
    prompt, char, cat = build_story_prompt("hindi", "ghost")
    print(f"Character : {char}")
    print(f"Prompt    : {prompt}")
    print()

    print("ENGLISH PROMPT:")
    prompt, char, cat = build_story_prompt("english", "witch")
    print(f"Character : {char}")
    print(f"Prompt    : {prompt}")
    print("="*60)