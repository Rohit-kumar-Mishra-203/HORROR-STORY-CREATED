import random

# ─────────────────────────────────────────
# TENSION LEVELS
# ─────────────────────────────────────────
# Level 1 - Unease (something feels wrong)
# Level 2 - Dread (something is definitely wrong)
# Level 3 - Terror (direct confrontation)
# Level 4 - Horror (climax)
# Level 5 - Aftermath (resolution + twist setup)

TENSION_PHRASES = {
    "hindi": {
        1: [  # Unease
            "कुछ तो था उस जगह में जो सही नहीं लग रहा था।",
            "हवा में एक अजीब सी खुशबू थी। जली हुई लकड़ी और कुछ और।",
            "घर में एक अजीब सी खामोशी थी जो कानों को चुभती थी।",
            "उसके रोंगटे खड़े हो गए पर उसे समझ नहीं आया क्यों।",
            "कहीं न कहीं से एक धीमी आवाज़ आ रही थी। इतनी धीमी कि यकीन नहीं होता था।",
            "पालतू कुत्ता एक कोने में सिकुड़ गया था और हिलने से मना कर रहा था।"
        ],
        2: [  # Dread
            "तभी उसने देखा। दीवार पर एक काला धब्बा था जो धीरे धीरे हिल रहा था।",
            "आईने में उसका अक्स था। पर वो उसकी तरह नहीं हिल रहा था।",
            "दरवाज़ा अपने आप खुल गया। बाहर कोई नहीं था। पर ठंडी हवा का झोंका आया।",
            "उसके फोन की बैटरी अचानक खत्म हो गई। अंधेरे में वो अकेला था।",
            "छत पर कदमों की आवाज़ आई। धीमी। भारी। एक कदम। फिर दूसरा।",
            "बच्चे के रोने की आवाज़ आई। पर यहाँ कोई बच्चा नहीं था।"
        ],
        3: [  # Terror
            "और फिर उसने देखा। कमरे के कोने में कुछ खड़ा था। काला। लंबा। बिना चेहरे के।",
            "वो आवाज़ अब उसके बिल्कुल करीब थी। उसके कान के पास। ठंडी साँस।",
            "दरवाज़ा बंद हो गया। खिड़कियाँ बंद हो गईं। वो अकेला था उसके साथ।",
            "उसने चीखना चाहा। पर आवाज़ नहीं निकली। जैसे गले में कुछ अटक गया हो।",
            "वो साया उसकी तरफ बढ़ रहा था। हर कदम पर फर्श चरमराता था।",
            "तभी बत्ती बुझ गई। पूरा घर अंधेरे में डूब गया। और फिर एक आवाज़।"
        ],
        4: [  # Horror climax
            "वो चेहरा। वो भयानक चेहरा। उसे ज़िंदगी भर याद रहेगा।",
            "उसने जो देखा उसके बाद वो कभी सामान्य नहीं हो सका।",
            "सच्चाई इतनी भयानक थी कि दिमाग मानने से इनकार कर रहा था।",
            "वो पल जब सब कुछ सामने आया। वो पल जिसे वो भूलना चाहता था।",
            "चीख उसके गले में ही रह गई जब उसने देखा कि सामने क्या था।"
        ],
        5: [  # Aftermath
            "उस रात के बाद से वो कभी उस जगह नहीं गया।",
            "लोग कहते हैं वो ठीक है। पर उसकी आँखें कुछ और कहती हैं।",
            "वो अब भी रात को उठकर बैठ जाता है। जब वो आवाज़ें वापस आती हैं।",
            "घटना के बाद किसी को भी पूरी सच्चाई नहीं पता। सिर्फ उसे पता है।",
            "और सबसे डरावनी बात? उसे यकीन है कि वो अभी भी देख रहा है।"
        ]
    },

    "english": {
        1: [  # Unease
            "Something about the place felt deeply wrong, though he could not say exactly what.",
            "There was a smell in the air. Burnt wood and something else he could not identify.",
            "A strange silence filled the house, the kind that pressed against your ears.",
            "The hairs on the back of his neck rose for no reason he could explain.",
            "Somewhere deep in the house a sound was coming. So faint he almost missed it.",
            "The dog had retreated to the corner and refused to move no matter what."
        ],
        2: [  # Dread
            "That was when he saw it. A dark shape on the wall that was slowly moving.",
            "His reflection was in the mirror. But it was not moving the way he was moving.",
            "The door swung open by itself. Nobody was there. Just a rush of cold air.",
            "His phone died suddenly. He was alone in the dark with no way to call for help.",
            "Footsteps crossed the ceiling above him. Slow. Heavy. One step. Then another.",
            "He heard a child crying. But there were no children anywhere in this house."
        ],
        3: [  # Terror
            "And then he saw it. Standing in the corner of the room. Tall. Dark. Without a face.",
            "The voice was right next to his ear now. Cold breath on the side of his neck.",
            "The door slammed shut. The windows sealed. He was alone in here with it.",
            "He tried to scream. Nothing came out. His throat had closed completely.",
            "The shadow was moving toward him. The floorboards creaked with every step.",
            "The lights went out. The whole house plunged into darkness. And then a sound."
        ],
        4: [  # Horror climax
            "That face. That terrible face. It would stay with him for the rest of his life.",
            "What he saw in that moment broke something inside him that never fully healed.",
            "The truth was so horrifying that his mind simply refused to accept it.",
            "The moment when everything was revealed. The moment he would spend years trying to forget.",
            "The scream stayed locked in his throat when he finally saw what was standing there."
        ],
        5: [  # Aftermath
            "He never went back to that place after that night.",
            "People say he is fine now. But his eyes tell a different story.",
            "He still wakes up at night and sits in the dark when the sounds come back.",
            "Nobody ever knew the full truth of what happened. Only he knew.",
            "And the most terrifying part? He is certain that whatever it was is still watching."
        ]
    }
}


# ─────────────────────────────────────────
# SUSPENSE BUILDERS
# ─────────────────────────────────────────
SUSPENSE_BUILDERS = {
    "hindi": [
        "उसने एक कदम आगे बढ़ाया।",
        "उसने धीरे से दरवाज़ा खोला।",
        "उसने साँस रोककर इंतज़ार किया।",
        "वो रुका। सुना। कुछ नहीं।",
        "उसका दिल इतनी तेज़ धड़क रहा था कि उसे खुद सुनाई दे रहा था।",
        "हर कदम के साथ ठंड बढ़ती जा रही थी।",
        "उसने पीछे मुड़कर देखा।",
        "और फिर। खामोशी।"
    ],
    "english": [
        "He took one step forward.",
        "He slowly pushed the door open.",
        "He held his breath and waited.",
        "He stopped. Listened. Nothing.",
        "His heart was beating so hard he could hear it.",
        "With every step the cold grew worse.",
        "He turned around slowly.",
        "And then. Silence."
    ]
}


# ─────────────────────────────────────────
# BUILD TENSION ARC
# ─────────────────────────────────────────
def build_tension_arc(language, num_levels=5):
    phrases   = TENSION_PHRASES[language]
    suspense  = SUSPENSE_BUILDERS[language]
    arc       = []

    for level in range(1, num_levels + 1):
        # Add tension phrase for this level
        phrase = random.choice(phrases[level])
        arc.append(phrase)

        # Add suspense builder between levels 1-4
        if level < num_levels:
            builder = random.choice(suspense)
            arc.append(builder)

    return arc


# ─────────────────────────────────────────
# GET TENSION SUFFIX
# adds tension to end of generated story
# ─────────────────────────────────────────
def get_tension_suffix(language, intensity="high"):
    phrases = TENSION_PHRASES[language]

    if intensity == "low":
        levels = [1, 2]
    elif intensity == "medium":
        levels = [2, 3]
    else:  # high
        levels = [3, 4, 5]

    suffix_parts = []
    for level in levels:
        suffix_parts.append(random.choice(phrases[level]))

    return " ".join(suffix_parts)


# ─────────────────────────────────────────
# MAIN — for testing
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n🎃 Testing Tension Engine\n")
    print("="*60)

    print("HINDI TENSION ARC:")
    arc = build_tension_arc("hindi")
    for i, phrase in enumerate(arc):
        print(f"  {i+1}. {phrase}")

    print()
    print("ENGLISH TENSION SUFFIX (high intensity):")
    suffix = get_tension_suffix("english", "high")
    print(f"  {suffix}")
    print("="*60)