import random

# TWIST ENDINGS

TWISTS = {
    "hindi": {

        "ghost": [
            "और तभी उसे एहसास हुआ। वो खुद तीन साल पहले मर चुका था। वो जिस घर में था वो उसका अपना घर था। और जिन्हें वो भूत समझ रहा था वो असल में उसके परिवार के जीवित लोग थे जो उससे डर रहे थे।",
            "अगले दिन पड़ोसियों ने पुलिस को बुलाया। पुलिस ने घर की तलाशी ली। घर में कोई नहीं था। पर दीवार पर एक तस्वीर थी। पुरानी। काली सफेद। उसमें वही चेहरा था। तारीख थी पचास साल पुरानी।",
            "जब उसने आईने में देखा तो उसे समझ आया। उसकी परछाईं नहीं थी। कब से नहीं थी? शायद उस रात से जब वो पहली बार उस घर में आया था।"
        ],

        "witch": [
            "वो बूढ़ी औरत जो उसे रास्ता दिखाने आई थी। वो औरत जिसने उसे उस घर तक पहुँचाया था। अगले दिन गाँव वालों ने बताया कि उस औरत की मौत बीस साल पहले हो गई थी। उसी घर में।",
            "जादू का असर उस पर नहीं हुआ था। या शायद हो चुका था। और उसे पता भी नहीं था। क्योंकि जो इंसान जादू की चपेट में आता है उसे कभी पता नहीं चलता।",
            "उसने सोचा था कि उसने चुड़ैल को हरा दिया। पर जब उसने घर पहुँचकर आईने में देखा तो उसकी आँखें बदल चुकी थीं। वही आँखें जो उस चुड़ैल की थीं।"
        ],

        "haunted_house": [
            "मकान मालिक ने अगले दिन फोन किया। उसने कहा कि वो फ्लैट तीन साल से खाली है। कोई किरायेदार नहीं रहा उसमें। पर फिर वो रात कहाँ बिताई थी उसने?",
            "जब वो सुबह बाहर निकला तो घर की दीवारें काली थीं। जली हुई। पड़ोसियों ने बताया कि ये घर पंद्रह साल पहले आग में जल गया था। पर वो एक पूरी रात उसमें रहा था।",
            "उसे बाद में पता चला। इस घर में जो भी रुकता है वो उस घर का हिस्सा बन जाता है। और अब अगले किरायेदार को भी रात को वही आवाज़ें आएँगी जो उसे आई थीं।"
        ],

        "graveyard": [
            "सुबह जब वो कब्रिस्तान से निकला तो गेट पर एक पत्थर था। उस पर उसका अपना नाम लिखा था। और तारीख? आज की तारीख।",
            "उसने जो कब्र खोली थी वो खाली थी। हमेशा से खाली थी। पर उसके अंदर एक चीज़ थी। एक पुरानी डायरी। और उसमें वो सब लिखा था जो उस रात होने वाला था। शब्द दर शब्द।",
            "घर पहुँचकर उसकी माँ ने दरवाज़ा खोला और चीख पड़ी। क्योंकि उसके पीछे वो सब खड़े थे जिनकी कब्रें उसने उस रात देखी थीं।"
        ],

        "demon": [
            "ओझा ने कहा था कि राक्षस को भगा दिया। पर ओझा झूठ बोल रहा था। राक्षस गया नहीं था। वो बस एक जगह से दूसरी जगह गया था। ओझा के अंदर।",
            "जब उसने वो मंत्र पढ़ा तो राक्षस चला गया। पर एक शर्त थी जो उसे बाद में पता चली। हर बार जब कोई उसे वो मंत्र सुनाएगा राक्षस उसके पास वापस आएगा।",
            "राक्षस का असली नाम जानने के बाद उसने सोचा वो जीत गया। पर राक्षस मुस्कुराया और बोला तुमने मेरा नाम जाना। अब मैं तुम्हारा नाम जानता हूँ। और अब तुम कभी नहीं छुड़ा सकते मुझे।"
        ],

        "vampire": [
            "डॉक्टर ने अगले दिन रिपोर्ट दी। उसके खून में कुछ नहीं बचा था। पर वो ज़िंदा था। कैसे? डॉक्टर भी नहीं जानता था। पर सूरज की रोशनी में उसकी आँखें अब जलती थीं।",
            "उसे बाद में समझ आया। उस रात जो हुआ था उससे वो बदल गया था। वो अब इंसान नहीं था। और भूख। वो भूख जो हर रात बढ़ती थी। खून की भूख।",
            "पिशाच मर गया था। पर उसका अभिशाप नहीं मरा। जिसने भी उसका खून देखा था वो अब उस अभिशाप का हिस्सा था। और उस रात वहाँ तीन लोग थे।"
        ],

        "cursed_object": [
            "उसने वो चीज़ फेंक दी। जला दी। दफना दी। पर हर बार सुबह वो उसके तकिए के नीचे होती। और हर बार थोड़ी और करीब होती। जैसे घर कर रही हो।",
            "दुकानदार ने बताया कि वो चीज़ बिकती नहीं है। वो खुद चुनती है अपना मालिक। और एक बार चुन लिया तो छोड़ती नहीं।",
            "सबसे डरावनी बात ये थी कि जब उसने उस चीज़ को ध्यान से देखा तो उसमें उसका अपना चेहरा था। पर वो चेहरा मुस्कुरा नहीं रहा था। वो चेहरा डरा हुआ था। फँसा हुआ था।"
        ],

        "possessed": [
            "झाड़ फूँक के बाद सबने सोचा वो ठीक हो गया। पर उसकी माँ जानती थी। आँखें वही थीं पर मुस्कुराहट बदल गई थी। उसका बेटा वापस नहीं आया था।",
            "आत्मा निकल गई थी। पर वो कहाँ गई? ओझा ने बाद में बताया। आत्मा उसके सबसे करीबी इंसान में चली गई। और वो इंसान था उसकी पत्नी।",
            "उसे याद नहीं था उन तीन दिनों का कुछ भी। पर उसके हाथों पर खून के धब्बे थे। सूखे हुए। और अगले दिन अखबार में खबर थी। तीन लोग गायब।"
        ],

        "general_horror": [
            "और सबसे डरावनी बात? जो उसने उस रात देखा था वो कोई भूत नहीं था। कोई आत्मा नहीं थी। वो एक इंसान था। और वो इंसान अभी भी वहाँ है।",
            "उसने सोचा था यह सब खत्म हो गया। पर खत्म कुछ नहीं हुआ था। बस शुरुआत हुई थी। और अगला नंबर उसका नहीं था। अगला नंबर उसके सबसे प्यारे इंसान का था।",
            "वो रात जब वो घर से निकला तो उसने एक बार पीछे मुड़कर देखा। खिड़की में एक चेहरा था। उसका अपना चेहरा। घर के अंदर से बाहर देख रहा था।"
        ]
    },



    "english": {

        "ghost": [
            "And that was when he understood. He had died three years ago. The house he was standing in was his own. The people he had been calling ghosts were his living family members who had been terrified of him all along.",
            "The next morning the neighbors called the police. They searched the house. It was empty. But on the wall was a photograph. Old. Black and white. His face. The date was fifty years ago.",
            "When he looked in the mirror he finally understood. He had no reflection. How long had that been true? Perhaps since the very first night he walked into that house."
        ],

        "witch": [
            "The old woman who had shown him the way. The one who had guided him to that house. The next day the villagers told him she had died twenty years ago. In that very house.",
            "He thought the spell had not affected him. Or perhaps it already had and he simply could not tell. Because those who fall under the spell never know it has happened.",
            "He thought he had defeated the witch. But when he got home and looked in the mirror his eyes had changed. They were her eyes now. Exactly her eyes."
        ],

        "haunted_house": [
            "The landlord called the next morning. He said the apartment had been empty for three years. No tenant had lived there. But then where had he spent the night?",
            "When he stepped outside in the morning the walls of the house were black and charred. The neighbors told him the house had burned down fifteen years ago. But he had spent an entire night inside it.",
            "He learned the truth later. Everyone who stays in that house becomes part of it. And now the next tenant would hear the same sounds he had heard. Every single night."
        ],

        "graveyard": [
            "In the morning when he walked out of the cemetery there was a stone by the gate. His name was carved on it. And the date? Today's date.",
            "The grave he had opened was empty. It had always been empty. But inside it was an old diary. And in that diary was written everything that was going to happen that night. Word for word.",
            "When he got home his mother opened the door and screamed. Because standing behind him were all the figures whose graves he had passed that night."
        ],

        "demon": [
            "The priest said the demon had been driven out. But the priest was lying. The demon had not left. It had simply moved. Into the priest.",
            "When he spoke the incantation the demon left. But there was a condition nobody had told him. Every time someone recited those same words the demon would return to him.",
            "After learning the demon's true name he thought he had won. But the demon smiled and said now you know my name. And now I know yours. And you can never be free of me."
        ],

        "vampire": [
            "The doctor gave him the results the next day. There was almost nothing left in his blood. But he was alive. How? The doctor had no explanation. But sunlight made his eyes burn now in a way they never had before.",
            "He understood later what had happened that night. He had been changed. He was no longer human. And the hunger that grew every night was a hunger he recognized now. A hunger for blood.",
            "The vampire was dead. But its curse was not. Everyone who had witnessed its blood that night was now part of the curse. And there had been three people present."
        ],

        "cursed_object": [
            "He threw it away. Burned it. Buried it. But every morning it was under his pillow again. And every morning it was a little closer. As if it were making itself at home.",
            "The shopkeeper told him later that the object does not get sold. It chooses its owner. And once it has chosen you it does not let go.",
            "The most terrifying thing was what he saw when he looked closely at the object. His own face was inside it. But the face was not smiling. The face looked terrified. Trapped."
        ],

        "possessed": [
            "After the exorcism everyone thought he was cured. But his mother knew. The eyes were the same but the smile was different. Her son had not come back.",
            "The spirit had left his body. But where had it gone? The priest told him later. It had moved into the person closest to him. And that person was his wife.",
            "He remembered nothing of those three days. But there was dried blood on his hands. And the next morning the newspaper reported three people missing."
        ],

        "general_horror": [
            "And the most terrifying part? What he had seen that night was not a ghost. Not a spirit. It was a human being. And that person was still out there.",
            "He thought it was over. But nothing was over. It had only just begun. And the next target was not him. It was the person he loved most in the world.",
            "As he left that night he turned and looked back one last time. There was a face in the window. His own face. Looking out from inside the house."
        ]
    }
}


# GET TWIST ENDING
def get_twist(language, category):
    twists   = TWISTS[language]
    category = category if category in twists else "general_horror"
    twist    = random.choice(twists[category])
    return twist


# FORMAT TWIST WITH SEPARATOR
def format_twist(twist, language):
    if language == "hindi":
        separator = "\n\nपर असली सच्चाई तो ये थी।\n\n"
    else:
        separator = "\n\nBut here was the real truth.\n\n"
    return separator + twist


# MAIN — for testing
if __name__ == "__main__":
    print("\n Testing Twist Generator\n")
    print("="*60)

    print("HINDI GHOST TWIST:")
    twist = get_twist("hindi", "ghost")
    print(format_twist(twist, "hindi"))

    print()
    print("ENGLISH WITCH TWIST:")
    twist = get_twist("english", "witch")
    print(format_twist(twist, "english"))

    print()
    print("HINDI VAMPIRE TWIST:")
    twist = get_twist("hindi", "vampire")
    print(format_twist(twist, "hindi"))
    print("="*60)