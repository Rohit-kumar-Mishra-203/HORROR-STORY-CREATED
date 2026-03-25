import os
import sys

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
HINDI_BASE_DIR   = "data/raw"
ENGLISH_BASE_DIR = "data/raw_english"

CATEGORIES = [
    "witch", "ghost", "haunted_house", "graveyard",
    "demon", "vampire", "monster", "cursed_object",
    "possessed", "general_horror"
]

# ─────────────────────────────────────────
# IMPORT ALL TEMPLATES
# ─────────────────────────────────────────
from backend.model.story_templates.ghost_templates          import GHOST_HINDI, GHOST_ENGLISH
from backend.model.story_templates.haunted_house_templates  import HAUNTED_HOUSE_HINDI, HAUNTED_HOUSE_ENGLISH
from backend.model.story_templates.graveyard_templates      import GRAVEYARD_HINDI, GRAVEYARD_ENGLISH
from backend.model.story_templates.demon_templates          import DEMON_HINDI, DEMON_ENGLISH
from backend.model.story_templates.vampire_templates        import VAMPIRE_HINDI, VAMPIRE_ENGLISH
from backend.model.story_templates.monster_templates        import MONSTER_HINDI, MONSTER_ENGLISH
from backend.model.story_templates.cursed_object_templates  import CURSED_OBJECT_HINDI, CURSED_OBJECT_ENGLISH
from backend.model.story_templates.possessed_templates      import POSSESSED_HINDI, POSSESSED_ENGLISH
from backend.model.story_templates.general_horror_templates import GENERAL_HORROR_HINDI, GENERAL_HORROR_ENGLISH

# Witch templates (we will add these below)
WITCH_HINDI = [
    """गाँव के बाहर एक घना जंगल था। उस जंगल में एक बूढ़ी चुड़ैल रहती थी जिसका नाम कोई नहीं जानता था। गाँव वाले उसके बारे में फुसफुसाते थे पर कभी ज़ोर से नहीं बोलते थे।

रमेश उस गाँव में नया आया था। उसे इन बातों पर यकीन नहीं था। एक रात जब बारिश हो रही थी वो जंगल के पास से गुज़रा।

तभी उसने देखा। एक बूढ़ी औरत पेड़ के नीचे खड़ी थी। उसके बाल सफेद थे और आँखें पीली।

उसने रमेश को देखा और मुस्कुराई। वो मुस्कुराहट इंसानी नहीं थी।

रमेश भागा। पर जितना भागा जंगल उतना घना होता गया। पीछे से हँसने की आवाज़ आ रही थी।

सुबह गाँव वालों ने रमेश को जंगल के बाहर बेहोश पाया। उसके बालों का रंग रातोंरात सफेद हो गया था। और उसकी आँखें पीली थीं।""",

    """सुनीता को बचपन से बताया गया था कि जंगल के पार मत जाना। पर उस रात उसकी दोस्त की आवाज़ जंगल से आ रही थी।

जंगल के अंदर एक रोशनी थी। नीली। काँपती हुई। सुनीता उसके पीछे चलती रही।

तभी रोशनी रुक गई और एक बूढ़ी औरत सामने आई।

चुड़ैल की उँगलियाँ लंबी थीं। नाखून काले थे। उसने कहा बेटी तू यहाँ क्यों आई।

सुनीता ने कहा मेरी दोस्त कहाँ है।

चुड़ैल ने हँसकर कहा तेरी दोस्त अब मेरे पास है। और अब तू भी।

सुनीता चीखी पर जंगल ने उसकी चीख को निगल लिया।""",

    """डायन का घर पहाड़ की चोटी पर था। रात को वहाँ से रोशनी दिखती थी। लोग कहते थे वो मंत्र पढ़ती है।

विकास पत्रकार था। उसने सच जानना चाहा।

वो रात को चोटी पर गया। घर का दरवाज़ा खुला था।

अंदर एक बड़ा सा कड़ाही था। उसमें कुछ उबल रहा था। काला।

एक बुढ़िया पीठ करके बैठी थी। वो कुछ बुदबुदा रही थी।

विकास ने कदम रखा। फर्श चरमराया।

बुढ़िया ने पीछे देखा।

उसका चेहरा नहीं था।

विकास चीखा। पर आवाज़ नहीं निकली। जैसे किसी ने उसकी आवाज़ ले ली हो।

वो कभी उस पहाड़ से नहीं उतरा।""",

    """तंत्र मंत्र की किताब पुरानी दुकान में मिली। अर्जुन ने खरीदी। उसे लगा यह सब बकवास है।

घर आकर उसने एक मंत्र पढ़ा। मज़ाक में।

उस रात कुछ आया।

दरवाज़े पर। तीन बार। धीमी दस्तक।

अर्जुन ने खोला।

एक बूढ़ी औरत थी। लंबी। झुकी हुई। उसके हाथ में एक किताब थी।

उसने कहा तुमने बुलाया।

अर्जुन ने कहा मैंने नहीं बुलाया।

उसने कहा जिसने यह मंत्र पढ़ा वो मुझे बुलाता है। हमेशा।

उसके बाद से अर्जुन के घर में रात को आवाज़ें आती हैं।

किताब अपने आप खुलती है।

और हर रात वो बूढ़ी औरत दरवाज़े पर होती है।""",

    """काली माया गाँव की सबसे खूबसूरत औरत थी। पर कोई उससे दोस्ती नहीं करता था।

एक दिन एक नया आदमी आया। उसे काली माया से प्यार हो गया।

गाँव वालों ने मना किया। उसने नहीं माना।

शादी हो गई।

पहली रात आदमी को पता चला। काली माया रात को बदल जाती है।

उसके नाखून बड़े हो जाते हैं। उसकी आँखें लाल हो जाती हैं। उसके बाल उड़ते हैं।

वो जंगल जाती है। और सुबह वापस आती है।

आदमी ने पूछा तुम क्या हो।

उसने कहा जो मैं हूँ वो तुम नहीं जानना चाहते।

आदमी गाँव से भाग गया।

काली माया अभी भी वहाँ है। हर रात जंगल जाती है।

और जो भी नया आता है। उसे प्यार हो जाता है।""",

    """तीन लड़कियाँ थीं। उन्होंने एक खेल खेला। रात को आईने के सामने मोमबत्ती जलाई।

चुड़ैल को बुलाया।

दो लड़कियाँ डर गईं। भाग गईं।

तीसरी रुकी।

आईने में कुछ हिला।

धीरे धीरे एक आकृति बनी। बूढ़ी। झुकी हुई।

लड़की ने कहा तुम कौन हो।

आकृति ने कहा जिसे तुमने बुलाया।

लड़की ने कहा मैं मज़ाक कर रही थी।

आकृति ने कहा मैं नहीं।

मोमबत्ती बुझ गई।

दोनों लड़कियाँ अगले दिन अपनी दोस्त को ढूँढने गईं।

घर में कोई नहीं था।

बस आईने में एक धुंधली आकृति थी। जो उनकी तरफ देख रही थी।""",

    """जादूगरनी का श्राप पीढ़ियों से चला आ रहा था। परिवार की हर तीसरी बेटी।

नीलम तीसरी बेटी थी।

उसे पता था। पर उसने सोचा यह बस कहानी है।

अठारह साल की होने पर एक रात उसके सपने में एक बूढ़ी औरत आई।

उसने कहा अब तुम्हारी बारी है।

नीलम जागी। उसके हाथ काँप रहे थे।

सुबह उसने देखा। उसके बालों में एक सफेद लट आ गई थी। रातोंरात।

माँ ने देखा और रो पड़ी।

उसने कहा श्राप सच है।

नीलम ने पूछा इसे तोड़ा कैसे जाता है।

माँ ने कहा अब तक कोई नहीं तोड़ सका।""",

    """जंगल में एक झोपड़ी थी। उसमें एक बुढ़िया रहती थी। लोग कहते थे वो सौ साल से ज़्यादा की है।

एक बच्चा खेलते खेलते वहाँ पहुँच गया।

बुढ़िया ने उसे देखा। मुस्कुराई।

उसने कहा आओ बेटा। मिठाई खाओगे।

बच्चे ने कहा माँ ने मना किया है।

बुढ़िया ने कहा माँ को क्या पता।

बच्चा अंदर गया।

शाम को वो घर नहीं आया।

माँ ढूँढने गई। झोपड़ी खाली थी।

बस एक छोटा सा जूता था। बच्चे का।

और दीवार पर एक निशान था। काला। हाथ का।

बच्चे जैसा।""",

    """पहाड़ी गाँव में एक रिवाज़ था। हर साल एक बकरी चुड़ैल को दी जाती थी।

एक साल युवा सरपंच ने कहा यह अंधविश्वास है। नहीं देंगे।

गाँव वाले डरे। पर सरपंच ने नहीं माना।

उस रात जंगल से आवाज़ें आईं। पर किसी ने दरवाज़ा नहीं खोला।

सुबह सरपंच के घर के बाहर कुछ था।

उसकी बकरी। पर उसकी आँखें सफेद थीं।

और उसके गले पर एक निशान था। उँगलियों का।

सरपंच काँप गया।

उस शाम उसने खुद जंगल में बकरी छोड़ी।

तब से उसने कभी अंधविश्वास नहीं कहा।""",

    """बाज़ार में एक औरत मिली। उसने एक लड्डू दिया। कहा मुफ्त में।

माँ ने बच्चे को दे दिया।

रात को बच्चा बीमार पड़ा।

डॉक्टर ने कहा कोई बीमारी नहीं। पर बच्चा कमज़ोर होता जा रहा था।

एक पड़ोसिन ने बुढ़िया को देखा था। उसने कहा वो चुड़ैल है।

ओझा आया। उसने पूजा की।

बच्चे के मुँह से काला धुआँ निकला।

बच्चा ठीक हो गया।

ओझा ने कहा देर हो जाती तो बच्चा नहीं बचता।

माँ ने पूछा वो औरत कौन थी।

ओझा ने कहा बहुत पुरानी। बहुत भूखी। बच्चों की ऊर्जा चाहिए थी उसे।""",
]

WITCH_ENGLISH = [
    """The old woman at the edge of the forest had no name that anyone dared to speak. She had lived there for as long as the oldest villager could remember.

Marcus did not believe in old stories. He was twenty three and practical. That changed on a Tuesday night in October.

He was taking the short road home through the woods when he saw the fire. Small and blue and perfectly still despite the wind. He walked toward it.

She was standing beside it. Ancient. Bent. Her eyes caught the blue flame and reflected it back at him like two pale moons.

She said nothing. She only smiled.

Marcus ran. He ran until his lungs burned and he collapsed at the edge of the road. When he looked back the fire was gone.

In the morning his neighbor found him on the road. He was alive. But every mirror in his house showed a different reflection. An old woman. Smiling.""",

    """The village had not had a witch in three generations. The old families remembered the signs. The new families did not.

When the woman moved into the house at the crossroads nobody thought anything of it. She was quiet. She kept a garden. She smiled when spoken to.

The first child went missing in October. The second in November. Both found unharmed but changed. Quieter. Their eyes sometimes going to places nobody else could see.

An old woman from one of the original families went to the house at the crossroads alone.

She was inside for an hour. When she came out she said simply leave this village tonight. All of you.

Half the village left. The other half stayed.

Only the half that left was ever heard from again.""",

    """She had been casting spells since before your grandmother was born. That was what the note said. The note that came with the inheritance.

Sarah had inherited the house from an aunt she had never met. The note said the house came with a responsibility. It said the previous occupant had maintained a balance. It said the balance needed maintaining.

Sarah did not understand what this meant until the first night.

Something came to the door at midnight. Old. Patient. It had been coming to this house for two hundred years and it expected what it had always received.

Sarah did not know what to give it. She stood at the door and felt its attention like pressure against her face.

She said I do not know what you want.

It said you will learn. It said your aunt learned. It said they all learn eventually.

It left. It came back the next night. And the night after.

Sarah is still learning.""",

    """The coven met on the hill every new moon. The town below pretended not to know.

For three hundred years the arrangement had held. The coven kept to the hill. The town kept to the valley. Neither interfered with the other.

Then a developer bought the hill.

The coven sent a representative to the town council. An old woman. Older than anyone could account for. She said simply that the hill was not for sale and that the consequences of selling it would fall on the town not the developer.

The council voted to proceed with the sale.

The developer broke ground on a Monday.

On Tuesday the machinery stopped working. On Wednesday the workers refused to return. On Thursday the developer himself drove to the site and stood looking at the hill for a long time before driving away and never coming back.

The hill remains undeveloped. The coven still meets there.

The town council has new members now. The old ones retired suddenly and unanimously in the same week. None of them will explain why.""",

    """The book of spells had been in her family for seven generations. Each generation added to it. Each generation warned the next.

Do not read page forty seven aloud.

Anna was the first in seven generations to read page forty seven aloud.

She did it on a dare. At a party. In front of people who laughed.

The laughter stopped when the lights went out.

When they came back on Anna was standing in the center of the room with her eyes closed and her arms at her sides and her lips moving.

Her friends said her name. She did not respond.

The words she was speaking were not English. They were not any language anyone present recognized.

She stood like that for eleven minutes. Then she opened her eyes.

She looked at each of her friends in turn.

She said we have a guest now. She said please be polite.""",

    """The herbalist in the market had no sign above her stall. She did not need one. People found her when they needed her.

For ordinary ailments she charged ordinary prices. For extraordinary requests she named a different kind of price.

A young man came to her with an extraordinary request. He wanted someone to love him who did not love him.

She looked at him for a long time. She said I can do this. She named her price.

He paid it without fully understanding what he was paying.

The woman he wanted did fall in love with him. Completely. Utterly. In a way that left no room for anything else.

He had not understood that the price was the same thing happening to him.

They are together still. Neither can think of anything but the other. Neither can sleep. Neither can eat properly. Neither is unhappy exactly.

But neither is free.""",

    """Three hundred years ago a woman was accused. The trial lasted one day. The sentence was carried out the same evening.

She said nothing during the trial. She said nothing at the sentence. She said one thing at the end.

She said I will remember each of your names.

The families of those who accused her have lived in that town ever since. They have never been able to leave. Those who try find themselves turning around without meaning to. Finding reasons to stay. Feeling an unease outside the town borders that fades only when they return.

They do not talk about this.

They know what it is. They have always known.

They are still being remembered.""",

    """The scarecrow in the field was too realistic. That was the first thing visitors noticed. The proportions were wrong in a way that was hard to specify. The posture was too deliberate. The face, though it was only cloth and buttons, seemed to be looking at something specific.

The farmer who owned the field had not put it there.

He found it one morning. He tried to take it down. The pole would not move.

He tried to cut it at the base. The blade turned.

He left it. He planted around it. He tried not to look at it.

Twice a year without fail he woke to find it had moved. Slightly. Facing a different direction. As if checking on something.

His daughter asked him once who made the scarecrow.

He said he did not know.

She said it looks like it's waiting for something.

He said he knew.

He never told her what he thought it was waiting for.""",

    """The apprentice had studied under the old woman for seven years. She had learned everything the old woman was willing to teach.

On the last day the old woman said there is one more thing.

She said power has a cost. Not the power you use. The power you hold. Simply holding it costs something. Every day.

The apprentice asked what.

The old woman said time. She said look at me. She said I have held this for sixty years. She said this is what sixty years of holding it looks like.

The apprentice looked. The old woman looked older than anyone she had ever seen.

The old woman said you can put it down. She said I never could. She said the work needed doing and I was the one who could do it.

She said you are the one who can do it now.

The apprentice understood what she was being offered. She understood what she was being asked to give.

She thought about it for a long time.

She said yes.""",

    """The last witch in the county died on a Thursday. By Friday something was wrong.

Not dramatically wrong. Not immediately obvious. Just a low persistent sense that something that had been in place for a very long time was no longer in place.

Animals behaved strangely. Milk went bad faster than usual. Children woke from nightmares they could not describe.

The pastor said it was grief. The doctor said it was coincidence.

The oldest resident in the county said it was consequence.

She said the witch had been keeping something out. For sixty years she had been keeping it out. And now she was gone and the door she had been holding closed was no longer held.

People asked what was coming in.

The old woman said she did not know exactly. She said the witch had never told her what it was. Only that it was patient and that it had been waiting for a very long time.

She said it was still waiting. She said it would not wait much longer.""",
]

# ─────────────────────────────────────────
# ALL TEMPLATES COMBINED
# ─────────────────────────────────────────
ALL_TEMPLATES = {
    "hindi": {
        "witch"         : WITCH_HINDI,
        "ghost"         : GHOST_HINDI,
        "haunted_house" : HAUNTED_HOUSE_HINDI,
        "graveyard"     : GRAVEYARD_HINDI,
        "demon"         : DEMON_HINDI,
        "vampire"       : VAMPIRE_HINDI,
        "monster"       : MONSTER_HINDI,
        "cursed_object" : CURSED_OBJECT_HINDI,
        "possessed"     : POSSESSED_HINDI,
        "general_horror": GENERAL_HORROR_HINDI,
    },
    "english": {
        "witch"         : WITCH_ENGLISH,
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
}


# ─────────────────────────────────────────
# SAVE TRAINING DATA FILES
# ─────────────────────────────────────────
def save_training_data():
    print("\n" + "="*60)
    print("📚 GENERATING CATEGORY-WISE TRAINING DATA")
    print("="*60)

    total_saved = 0

    for language, categories in ALL_TEMPLATES.items():
        base_dir = HINDI_BASE_DIR if language == "hindi" else ENGLISH_BASE_DIR
        print(f"\n{'🇮🇳' if language == 'hindi' else '🇬🇧'} {language.upper()}")
        print("-"*40)

        for category, stories in categories.items():
            cat_dir = os.path.join(base_dir, category)
            os.makedirs(cat_dir, exist_ok=True)

            for i, story in enumerate(stories):
                filename = f"{category}_{i+1:02d}.txt"
                filepath = os.path.join(cat_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(story.strip())

                total_saved += 1

            print(f"  ✅ {category:20s} → {len(stories)} stories saved")

    print("\n" + "="*60)
    print(f"  Total stories saved : {total_saved}")
    print("="*60 + "\n")


if __name__ == "__main__":
    save_training_data()