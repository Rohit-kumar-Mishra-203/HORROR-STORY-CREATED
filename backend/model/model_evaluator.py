import os
import sys
import json
import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')   # no display needed
import matplotlib.pyplot as plt
from datetime import datetime

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
))
from backend.model.config import *

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
EVAL_OUTPUT_DIR = "model_evaluation"
os.makedirs(EVAL_OUTPUT_DIR, exist_ok=True)

CATEGORIES = [
    "witch", "ghost", "haunted_house", "graveyard",
    "demon", "vampire", "monster", "cursed_object",
    "possessed", "general_horror"
]

# Test prompts for each category
TEST_PROMPTS = {
    "hindi": {
        "witch"         : "यह एक चुड़ैल डायन जादू टोना मंत्र की कहानी है। रात के अंधेरे में",
        "ghost"         : "यह एक भूत प्रेत आत्मा भूतिया डरावना की कहानी है। रात के अंधेरे में",
        "haunted_house" : "यह एक हवेली भूतिया घर वीरान खंडहर की कहानी है। रात के अंधेरे में",
        "graveyard"     : "यह एक कब्रिस्तान कब्र मुर्दा शमशान की कहानी है। रात के अंधेरे में",
        "demon"         : "यह एक राक्षस शैतान दानव असुर दैत्य की कहानी है। रात के अंधेरे में",
        "vampire"       : "यह एक पिशाच खून रक्त अमर रात की कहानी है। रात के अंधेरे में",
        "monster"       : "यह एक राक्षस जीव भयानक दानव खौफनाक की कहानी है। रात के अंधेरे में",
        "cursed_object" : "यह एक शापित श्राप पुरानी चीज़ अभिशाप की कहानी है। रात के अंधेरे में",
        "possessed"     : "यह एक भूत चढ़ना आवेश शरीर आत्मा की कहानी है। रात के अंधेरे में",
        "general_horror": "यह एक डरावना भूत रात अंधेरा खौफ की कहानी है। रात के अंधेरे में",
    },
    "english": {
        "witch"         : "This is a horror story about witch spell curse magic coven. It was a dark terrifying night when",
        "ghost"         : "This is a horror story about ghost spirit haunted supernatural. It was a dark terrifying night when",
        "haunted_house" : "This is a horror story about haunted house mansion abandoned. It was a dark terrifying night when",
        "graveyard"     : "This is a horror story about graveyard cemetery grave tombstone. It was a dark terrifying night when",
        "demon"         : "This is a horror story about demon devil evil dark entity. It was a dark terrifying night when",
        "vampire"       : "This is a horror story about vampire blood fangs immortal. It was a dark terrifying night when",
        "monster"       : "This is a horror story about monster creature beast lurking. It was a dark terrifying night when",
        "cursed_object" : "This is a horror story about cursed object ancient artifact. It was a dark terrifying night when",
        "possessed"     : "This is a horror story about possessed body taken over evil. It was a dark terrifying night when",
        "general_horror": "This is a horror story about horror scary dark terrifying evil. It was a dark terrifying night when",
    }
}

# Category keywords to check in output
CATEGORY_KEYWORDS = {
    "hindi": {
        "witch"         : ["चुड़ैल", "डायन", "जादू", "टोना", "मंत्र", "जंगल", "श्राप"],
        "ghost"         : ["भूत", "प्रेत", "आत्मा", "भूतिया", "डर"],
        "haunted_house" : ["हवेली", "घर", "वीरान", "खंडहर", "पुराना"],
        "graveyard"     : ["कब्रिस्तान", "कब्र", "मुर्दा", "शमशान"],
        "demon"         : ["राक्षस", "शैतान", "दानव", "असुर"],
        "vampire"       : ["पिशाच", "खून", "रक्त", "रात"],
        "monster"       : ["जीव", "भयानक", "जंगल", "दानव"],
        "cursed_object" : ["शापित", "श्राप", "चीज़", "पुरानी"],
        "possessed"     : ["आवेश", "शरीर", "आत्मा", "भूत"],
        "general_horror": ["डर", "रात", "अंधेरा", "भूत"],
    },
    "english": {
        "witch"         : ["witch", "spell", "curse", "magic", "forest", "old woman"],
        "ghost"         : ["ghost", "spirit", "haunted", "appeared", "voice"],
        "haunted_house" : ["house", "mansion", "door", "room", "dark"],
        "graveyard"     : ["grave", "cemetery", "dead", "tomb", "night"],
        "demon"         : ["demon", "evil", "dark", "shadow", "power"],
        "vampire"       : ["blood", "night", "fangs", "immortal", "pale"],
        "monster"       : ["creature", "beast", "forest", "eyes", "large"],
        "cursed_object" : ["object", "cursed", "ancient", "strange", "found"],
        "possessed"     : ["body", "voice", "eyes", "changed", "inside"],
        "general_horror": ["dark", "night", "fear", "sound", "something"],
    }
}


# ─────────────────────────────────────────
# LOAD HINDI MODEL
# ─────────────────────────────────────────
def load_hindi_model():
    print("  📥 Loading Hindi model...")
    if not os.path.exists(SAVED_MODEL_DIR):
        print(f"  ❌ Hindi model not found: {SAVED_MODEL_DIR}")
        return None, None, None

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tokenizer = AutoTokenizer.from_pretrained(
        SAVED_MODEL_DIR, use_fast=False, keep_accents=True
    )
    model  = AutoModelForSeq2SeqLM.from_pretrained(
        SAVED_MODEL_DIR, torch_dtype=torch.float32
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)    # type: ignore
    model.eval()        # type: ignore
    print(f"  ✅ Hindi model loaded on {device}")
    return tokenizer, model, device


# ─────────────────────────────────────────
# LOAD ENGLISH MODEL
# ─────────────────────────────────────────
def load_english_model():
    print("  📥 Loading English model...")
    eng_dir = "saved_model_english"
    if not os.path.exists(eng_dir):
        print(f"  ❌ English model not found: {eng_dir}")
        return None, None, None

    from transformers import GPT2Tokenizer, GPT2LMHeadModel
    tokenizer           = GPT2Tokenizer.from_pretrained(eng_dir)
    tokenizer.pad_token = tokenizer.eos_token
    model  = GPT2LMHeadModel.from_pretrained(
        eng_dir, torch_dtype=torch.float32
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)    # type: ignore
    model.eval()        # type: ignore
    print(f"  ✅ English model loaded on {device}")
    return tokenizer, model, device


# ─────────────────────────────────────────
# GENERATE HINDI TEXT
# ─────────────────────────────────────────
def generate_hindi(prompt, tokenizer, model, device, max_len=200):
    inputs = tokenizer(
        prompt,
        return_tensors = "pt",
        max_length     = 512,
        truncation     = True,
        padding        = True
    ).to(device)

    try:
        forced_bos = tokenizer.convert_tokens_to_ids("<2hi>")
        if forced_bos == tokenizer.unk_token_id:
            forced_bos = None
    except:
        forced_bos = None

    with torch.no_grad():
        outputs = model.generate(   # type: ignore
            input_ids            = inputs["input_ids"],
            attention_mask       = inputs["attention_mask"],
            max_length           = max_len,
            min_length           = 50,
            do_sample            = True,
            temperature          = 0.7,
            top_k                = 40,
            top_p                = 0.85,
            repetition_penalty   = 2.5,
            no_repeat_ngram_size = 3,
            forced_bos_token_id  = forced_bos,
        )

    return tokenizer.decode(
        outputs[0], skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )


# ─────────────────────────────────────────
# GENERATE ENGLISH TEXT
# ─────────────────────────────────────────
def generate_english(prompt, tokenizer, model, device, max_len=200):
    inputs = tokenizer(
        prompt,
        return_tensors = "pt",
        truncation     = True,
        max_length     = 200,
        padding        = True
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(   # type: ignore
            input_ids            = inputs["input_ids"],
            attention_mask       = inputs["attention_mask"],
            max_length           = max_len,
            min_length           = 50,
            do_sample            = True,
            temperature          = 0.7,
            top_k                = 40,
            top_p                = 0.85,
            repetition_penalty   = 2.0,
            no_repeat_ngram_size = 3,
            pad_token_id         = tokenizer.eos_token_id,
        )

    return tokenizer.decode(
        outputs[0], skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )


# ─────────────────────────────────────────
# CALCULATE PERPLEXITY
# lower = better (model is more confident)
# ─────────────────────────────────────────
def calculate_perplexity_hindi(text, tokenizer, model, device):
    try:
        inputs = tokenizer(
            text,
            return_tensors = "pt",
            max_length     = 512,
            truncation     = True
        ).to(device)

        with torch.no_grad():
            outputs = model(    # type: ignore
                input_ids = inputs["input_ids"],
                labels    = inputs["input_ids"]
            )
        loss = outputs.loss
        return float(torch.exp(loss).item())
    except:
        return None


def calculate_perplexity_english(text, tokenizer, model, device):
    try:
        inputs = tokenizer(
            text,
            return_tensors = "pt",
            max_length     = 512,
            truncation     = True,
            return_attention_mask = True
        ).to(device)

        input_ids = inputs["input_ids"]
        with torch.no_grad():
            outputs = model(    # type: ignore
                input_ids = input_ids,
                labels    = input_ids
            )
        loss = outputs.loss
        return float(torch.exp(loss).item())
    except:
        return None


# ─────────────────────────────────────────
# CATEGORY RELEVANCE SCORE
# checks if generated text matches category
# ─────────────────────────────────────────
def category_relevance_score(generated_text, language, category):
    keywords = CATEGORY_KEYWORDS.get(language, {}).get(category, [])
    if not keywords:
        return 0.0

    text_lower  = generated_text.lower()
    found       = sum(1 for kw in keywords if kw.lower() in text_lower)
    score       = found / len(keywords)
    return round(score, 3)


# ─────────────────────────────────────────
# REPETITION SCORE
# checks for repeated phrases (bad = high)
# ─────────────────────────────────────────
def repetition_score(text):
    words  = text.split()
    if len(words) < 10:
        return 0.0

    # Check 3-gram repetition
    trigrams = [
        tuple(words[i:i+3])
        for i in range(len(words)-2)
    ]
    unique   = set(trigrams)
    if len(trigrams) == 0:
        return 0.0

    repetition = 1 - (len(unique) / len(trigrams))
    return round(repetition, 3)


# ─────────────────────────────────────────
# LENGTH SCORE
# checks if output is long enough
# ─────────────────────────────────────────
def length_score(text, min_words=50, good_words=150):
    words = len(text.split())
    if words < min_words:
        return round(words / min_words, 3)
    elif words >= good_words:
        return 1.0
    else:
        return round(words / good_words, 3)


# ─────────────────────────────────────────
# DETECT OVERFITTING / UNDERFITTING
# from training logs
# ─────────────────────────────────────────
def detect_overfitting(log_file=None):
    print("\n" + "="*60)
    print("🔍 OVERFITTING / UNDERFITTING DETECTION")
    print("="*60)

    # Try to find training logs
    log_dirs = ["logs_hindi", "logs_english", "logs"]
    found_logs = {}

    for log_dir in log_dirs:
        trainer_state = os.path.join(log_dir, "trainer_state.json")
        if os.path.exists(trainer_state):
            found_logs[log_dir] = trainer_state

    if not found_logs:
        print("  ⚠️  No training logs found")
        print("  Train your model first to see overfitting analysis")
        return {}

    results = {}

    for log_dir, log_path in found_logs.items():
        print(f"\n  📊 Analyzing: {log_dir}")

        with open(log_path, 'r') as f:
            state = json.load(f)

        log_history = state.get("log_history", [])
        if not log_history:
            continue

        # Extract train and eval losses
        train_losses = []
        eval_losses  = []
        steps        = []

        for entry in log_history:
            if "loss" in entry and "eval_loss" not in entry:
                train_losses.append(entry["loss"])
                steps.append(entry.get("step", len(train_losses)))
            if "eval_loss" in entry:
                eval_losses.append(entry["eval_loss"])

        if not train_losses:
            continue

        # Analysis
        final_train = train_losses[-1]  if train_losses else None
        final_eval  = eval_losses[-1]   if eval_losses  else None
        best_eval   = min(eval_losses)  if eval_losses  else None

        print(f"  Final train loss : {final_train:.4f}" if final_train else "  No train loss")
        print(f"  Final eval loss  : {final_eval:.4f}"  if final_eval  else "  No eval loss")
        print(f"  Best eval loss   : {best_eval:.4f}"   if best_eval   else "  No eval loss")

        # Diagnose
        diagnosis = ""
        if final_train and final_eval:
            gap = final_eval - final_train
            if final_train > 3.0 and final_eval > 3.0:
                diagnosis = "🔴 UNDERFITTING — loss too high. Need more training epochs or more data."
            elif gap > 1.0:
                diagnosis = "🟡 OVERFITTING — eval loss much higher than train loss. Need more data or regularization."
            elif gap > 0.5:
                diagnosis = "🟡 MILD OVERFITTING — slight gap. Consider adding more stories."
            elif final_train < 0.1:
                diagnosis = "🟡 POSSIBLE OVERFITTING — train loss very low. Model may have memorized data."
            else:
                diagnosis = "🟢 GOOD FIT — train and eval losses are balanced."

        print(f"  Diagnosis        : {diagnosis}")

        results[log_dir] = {
            "train_losses": train_losses,
            "eval_losses" : eval_losses,
            "steps"       : steps,
            "diagnosis"   : diagnosis,
            "final_train" : final_train,
            "final_eval"  : final_eval,
        }

        # Plot loss curves
        if train_losses:
            plot_loss_curve(train_losses, eval_losses, log_dir)

    return results


# ─────────────────────────────────────────
# PLOT LOSS CURVE
# ─────────────────────────────────────────
def plot_loss_curve(train_losses, eval_losses, name):
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Train Loss', color='blue',  linewidth=2)
    if eval_losses:
        # Interpolate eval to same length as train
        x_eval  = np.linspace(0, len(train_losses)-1, len(eval_losses))
        x_train = np.arange(len(train_losses))
        plt.plot(x_eval, eval_losses, label='Eval Loss', color='red', linewidth=2)

    plt.title(f'Training Loss Curve — {name}')
    plt.xlabel('Steps')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Add diagnosis zone
    plt.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='Good threshold')

    save_path = os.path.join(EVAL_OUTPUT_DIR, f"loss_curve_{name}.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📊 Loss curve saved → {save_path}")


# ─────────────────────────────────────────
# EVALUATE HINDI MODEL
# ─────────────────────────────────────────
def evaluate_hindi_model(tokenizer, model, device):
    print("\n" + "="*60)
    print("🇮🇳 EVALUATING HINDI MODEL")
    print("="*60)

    results     = {}
    total_score = 0
    count       = 0

    for category in CATEGORIES:
        prompt    = TEST_PROMPTS["hindi"][category]
        print(f"\n  🧪 Testing: {category}")
        print(f"     Prompt: {prompt[:60]}...")

        # Generate
        generated = generate_hindi(prompt, tokenizer, model, device)

        # Scores
        rel_score  = category_relevance_score(generated, "hindi", category)
        rep_score  = repetition_score(generated)
        len_score  = length_score(generated)
        perplexity = calculate_perplexity_hindi(generated, tokenizer, model, device)

        # Overall score (higher = better)
        overall = (rel_score * 0.5) + (len_score * 0.3) + ((1 - rep_score) * 0.2)

        print(f"     Category relevance : {rel_score:.2f} {'✅' if rel_score > 0.3 else '❌'}")
        print(f"     Repetition         : {rep_score:.2f} {'✅' if rep_score < 0.3 else '❌'}")
        print(f"     Length             : {len_score:.2f} {'✅' if len_score > 0.5 else '❌'}")
        print(f"     Perplexity         : {perplexity:.1f}" if perplexity else "     Perplexity : N/A")
        print(f"     Overall score      : {overall:.2f}/1.0")
        print(f"     Generated preview  : {generated[:100]}...")

        results[category] = {
            "relevance"  : rel_score,
            "repetition" : rep_score,
            "length"     : len_score,
            "perplexity" : perplexity,
            "overall"    : overall,
            "generated"  : generated[:200]
        }

        total_score += overall
        count       += 1

    avg_score = total_score / count if count > 0 else 0
    print(f"\n  🏆 Average Score : {avg_score:.2f}/1.0")
    print(f"  {'🟢 Model is working well!' if avg_score > 0.5 else '🔴 Model needs improvement'}")

    return results, avg_score


# ─────────────────────────────────────────
# EVALUATE ENGLISH MODEL
# ─────────────────────────────────────────
def evaluate_english_model(tokenizer, model, device):
    print("\n" + "="*60)
    print("🇬🇧 EVALUATING ENGLISH MODEL")
    print("="*60)

    results     = {}
    total_score = 0
    count       = 0

    for category in CATEGORIES:
        prompt    = TEST_PROMPTS["english"][category]
        print(f"\n  🧪 Testing: {category}")
        print(f"     Prompt: {prompt[:60]}...")

        # Generate
        generated = generate_english(prompt, tokenizer, model, device)

        # Scores
        rel_score  = category_relevance_score(generated, "english", category)
        rep_score  = repetition_score(generated)
        len_score  = length_score(generated)
        perplexity = calculate_perplexity_english(generated, tokenizer, model, device)

        overall = (rel_score * 0.5) + (len_score * 0.3) + ((1 - rep_score) * 0.2)

        print(f"     Category relevance : {rel_score:.2f} {'✅' if rel_score > 0.3 else '❌'}")
        print(f"     Repetition         : {rep_score:.2f} {'✅' if rep_score < 0.3 else '❌'}")
        print(f"     Length             : {len_score:.2f} {'✅' if len_score > 0.5 else '❌'}")
        print(f"     Perplexity         : {perplexity:.1f}" if perplexity else "     Perplexity : N/A")
        print(f"     Overall score      : {overall:.2f}/1.0")
        print(f"     Generated preview  : {generated[:100]}...")

        results[category] = {
            "relevance"  : rel_score,
            "repetition" : rep_score,
            "length"     : len_score,
            "perplexity" : perplexity,
            "overall"    : overall,
            "generated"  : generated[:200]
        }

        total_score += overall
        count       += 1

    avg_score = total_score / count if count > 0 else 0
    print(f"\n  🏆 Average Score : {avg_score:.2f}/1.0")
    print(f"  {'🟢 Model is working well!' if avg_score > 0.5 else '🔴 Model needs improvement'}")

    return results, avg_score


# ─────────────────────────────────────────
# PLOT CATEGORY SCORES
# ─────────────────────────────────────────
def plot_category_scores(hindi_results, english_results):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, results, title, color in [
        (axes[0], hindi_results,   "Hindi Model",   "blue"),
        (axes[1], english_results, "English Model", "green"),
    ]:
        if not results:
            ax.text(0.5, 0.5, 'Model not available',
                    ha='center', va='center', transform=ax.transAxes)
            continue

        cats   = list(results.keys())
        scores = [results[c]["overall"] for c in cats]
        rel    = [results[c]["relevance"] for c in cats]
        rep    = [1 - results[c]["repetition"] for c in cats]

        x = np.arange(len(cats))
        w = 0.25

        ax.bar(x - w, scores, w, label='Overall',    color=color,    alpha=0.8)
        ax.bar(x,     rel,    w, label='Relevance',  color='orange', alpha=0.8)
        ax.bar(x + w, rep,    w, label='No Repeat',  color='red',    alpha=0.8)

        ax.set_xlabel('Category')
        ax.set_ylabel('Score (0-1)')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(cats, rotation=45, ha='right', fontsize=8)
        ax.legend()
        ax.set_ylim(0, 1.1)
        ax.axhline(y=0.5, color='black', linestyle='--', alpha=0.3)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(EVAL_OUTPUT_DIR, "category_scores.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  📊 Category scores chart → {save_path}")


# ─────────────────────────────────────────
# SAVE EVALUATION REPORT
# ─────────────────────────────────────────
def save_eval_report(hindi_results, hindi_score,
                     english_results, english_score,
                     overfitting_results):

    report_path = os.path.join(EVAL_OUTPUT_DIR, "evaluation_report.txt")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("MODEL EVALUATION REPORT\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")

        # Overall summary
        f.write("OVERALL SUMMARY:\n")
        f.write("-"*40 + "\n")
        if hindi_score:
            status = "GOOD" if hindi_score > 0.5 else "NEEDS IMPROVEMENT"
            f.write(f"Hindi Model   : {hindi_score:.2f}/1.0  [{status}]\n")
        if english_score:
            status = "GOOD" if english_score > 0.5 else "NEEDS IMPROVEMENT"
            f.write(f"English Model : {english_score:.2f}/1.0  [{status}]\n")

        # Overfitting
        f.write("\nOVERFITTING ANALYSIS:\n")
        f.write("-"*40 + "\n")
        for log_dir, data in overfitting_results.items():
            f.write(f"\n{log_dir}:\n")
            f.write(f"  Train Loss : {data.get('final_train', 'N/A')}\n")
            f.write(f"  Eval Loss  : {data.get('final_eval',  'N/A')}\n")
            f.write(f"  Diagnosis  : {data.get('diagnosis',   'N/A')}\n")

        # Hindi details
        f.write("\nHINDI MODEL — CATEGORY SCORES:\n")
        f.write("-"*40 + "\n")
        for cat, data in (hindi_results or {}).items():
            f.write(f"\n{cat}:\n")
            f.write(f"  Relevance   : {data['relevance']}\n")
            f.write(f"  Repetition  : {data['repetition']}\n")
            f.write(f"  Length      : {data['length']}\n")
            f.write(f"  Overall     : {data['overall']}\n")
            f.write(f"  Preview     : {data['generated'][:100]}...\n")

        # English details
        f.write("\nENGLISH MODEL — CATEGORY SCORES:\n")
        f.write("-"*40 + "\n")
        for cat, data in (english_results or {}).items():
            f.write(f"\n{cat}:\n")
            f.write(f"  Relevance   : {data['relevance']}\n")
            f.write(f"  Repetition  : {data['repetition']}\n")
            f.write(f"  Length      : {data['length']}\n")
            f.write(f"  Overall     : {data['overall']}\n")
            f.write(f"  Preview     : {data['generated'][:100]}...\n")

        # Recommendations
        f.write("\nRECOMMENDATIONS:\n")
        f.write("-"*40 + "\n")

        all_scores = []
        for data in (hindi_results or {}).values():
            all_scores.append(data["overall"])
        for data in (english_results or {}).values():
            all_scores.append(data["overall"])

        if all_scores:
            avg = sum(all_scores) / len(all_scores)
            if avg < 0.3:
                f.write("🔴 Model needs significant improvement:\n")
                f.write("   → Add more training stories (50+ per category)\n")
                f.write("   → Run more training epochs (30-50)\n")
                f.write("   → Use GPT-2 Large instead of Medium\n")
            elif avg < 0.6:
                f.write("🟡 Model is average:\n")
                f.write("   → Add more stories per category\n")
                f.write("   → Retrain with more epochs\n")
            else:
                f.write("🟢 Model is performing well!\n")
                f.write("   → Continue adding data for even better results\n")

    print(f"\n  📄 Full report saved → {report_path}")


# ─────────────────────────────────────────
# FINAL DIAGNOSIS SUMMARY
# ─────────────────────────────────────────
def print_final_diagnosis(hindi_score, english_score, overfit_results):
    print("\n" + "="*60)
    print("🏥 FINAL MODEL DIAGNOSIS")
    print("="*60)

    # Score summary
    print("\n  📊 PERFORMANCE SCORES:")
    if hindi_score is not None:
        bar = "█" * int(hindi_score * 20) + "░" * (20 - int(hindi_score * 20))
        print(f"  Hindi   [{bar}] {hindi_score:.2f}/1.0")
    if english_score is not None:
        bar = "█" * int(english_score * 20) + "░" * (20 - int(english_score * 20))
        print(f"  English [{bar}] {english_score:.2f}/1.0")

    # Overfitting summary
    print("\n  🔍 TRAINING HEALTH:")
    for log_dir, data in overfit_results.items():
        print(f"  {log_dir}: {data.get('diagnosis', 'unknown')}")

    # What to do
    print("\n  💡 WHAT TO DO NEXT:")

    scores = [s for s in [hindi_score, english_score] if s is not None]
    avg    = sum(scores) / len(scores) if scores else 0

    if avg < 0.3:
        print("  🔴 Model is performing poorly")
        print("     → Add 10+ stories per category")
        print("     → Run: python data/generate_training_data.py")
        print("     → Retrain: python backend/model/train.py")
        print("     → Increase epochs to 50 in config")
    elif avg < 0.5:
        print("  🟡 Model is average")
        print("     → Add more category-specific stories")
        print("     → Retrain with more epochs")
        print("     → Templates will handle weak categories")
    elif avg < 0.7:
        print("  🟢 Model is decent")
        print("     → Keep adding more stories")
        print("     → Model will improve with more data")
    else:
        print("  ✅ Model is performing well!")
        print("     → Keep adding stories for even better results")

    print("\n  📁 Full evaluation saved to: model_evaluation/")
    print("="*60 + "\n")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n" + "="*60)
    print("🔬 HORROR STORY MODEL EVALUATOR")
    print("="*60)
    print("  1. Full evaluation (both models)")
    print("  2. Hindi model only")
    print("  3. English model only")
    print("  4. Overfitting check only")
    print("="*60)

    choice = input("\n  Choose (1/2/3/4): ").strip()

    hindi_results   = {}
    english_results = {}
    hindi_score     = None
    english_score   = None
    overfit_results = {}

    # Always check overfitting from logs
    overfit_results = detect_overfitting()

    if choice in ["1", "2"]:
        h_tok, h_model, h_device = load_hindi_model()
        if h_model is not None:
            hindi_results, hindi_score = evaluate_hindi_model(
                h_tok, h_model, h_device
            )

    if choice in ["1", "3"]:
        e_tok, e_model, e_device = load_english_model()
        if e_model is not None:
            english_results, english_score = evaluate_english_model(
                e_tok, e_model, e_device
            )

    # Plot charts
    if hindi_results or english_results:
        plot_category_scores(hindi_results, english_results)

    # Save report
    save_eval_report(
        hindi_results,   hindi_score,
        english_results, english_score,
        overfit_results
    )

    # Final diagnosis
    print_final_diagnosis(hindi_score, english_score, overfit_results)


if __name__ == "__main__":
    main()