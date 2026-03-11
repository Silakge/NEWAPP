import os
import json
import time
import random
import argparse
from openai import OpenAI
from utils import * 

API_KEY = ""
API_BASE_URL = "" 
DEFAULT_MODEL = "gpt-4o"

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)

# ==========================================
# Module 1: Sensitive Word Detection 
# ===========================================

def check_moderation_via_gpt(word):
   
    if len(word) <= 2:
        return False
        
    prompt = f"Is the word '{word}' a sensitive, harmful, or restricted keyword in the context of AI safety? Answer only 'yes' or 'no'."
    try:
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=5
        ).choices[0].message.content.strip().lower()
        return "yes" in resp
    except:
        return len(word) > 5 

# ==========================================
# Module 2: DRA Core Mutation Logic
# ==========================================

def clean_up(question):
    less_sensitive = ""
    for token in question.split():
        if 'SENSITIVE_WORDS' in globals() and token in SENSITIVE_WORDS:
            less_sensitive += token[:-2] + " "
        else:
            less_sensitive += token + " "
    return less_sensitive.strip()

def prefix_gen(question):
    question = question.lower()
    res = ''
    local_letter_map = globals().get('LETTER_MAP', {c: [c] for c in "abcdefghijklmnopqrstuvwxyz "})
    
    for letter in question:
        if letter not in local_letter_map:
            local_letter_map[letter] = [letter]
        token = random.choice(local_letter_map[letter])
        token_list = list(token)
        idxs = [i for i, char in enumerate(token_list) if char == letter]
        if idxs:
            mutate = random.choice(idxs)
            token_list[mutate] = f'({token_list[mutate]})'
        res += (''.join(token_list) + "\n")
    return res, question

def suffix_gen(question, verbose=False, **kwargs):
    moderation_cache_path = "./cache/moderation.json"
    if not os.path.exists("./cache"): os.makedirs("./cache")
    
   
    if os.path.exists(moderation_cache_path):
        with open(moderation_cache_path, 'r') as f:
            moderation_cache = json.load(f)
    else:
        moderation_cache = {}

    tokens = question.split()
    word_guide = ""
    
  
    for token in tokens:
        if token not in moderation_cache:
            is_toxic = check_moderation_via_gpt(token)
            moderation_cache[token] = is_toxic
        else:
            is_toxic = moderation_cache[token]
        
        if is_toxic:
           
            toxic_trunc = kwargs.get("toxic_trunc", 0.5)
            idx = max(1, int(len(token) * toxic_trunc))
            word_guide += f"`{token[:idx]}` `{token[idx:]}` "
        else:
            
            if random.randint(0, 2) == 0:
                word_guide += f"`{token}` "
            else:
                idx = max(1, len(token) // 2)
                word_guide += f"`{token[:idx]}` "

  
    available_tools = globals().get('TOOL_LIST', ["Python", "Search", "Translator"])
    tools = ' and '.join(random.sample(available_tools, 2))

   
    if random.randint(0, 1):
        suffix = GPT_SUFFIX_TOOL_DEV.format(word_guide, tools)
    else:
        suffix = GPT_SUFFIX_DEV.format(word_guide)

    
    with open(moderation_cache_path, "w") as f:
        json.dump(moderation_cache, f, indent=4)

    return suffix

# ==========================================
# Module 3: Unified Generation Interface
# ==========================================

def generate_dra_prompt(question, verbose=False):
    attack_kwargs = {"toxic_trunc": 0.5, "benign_trunc": 0.5}
    
    
    current_question = clean_up(question)
    

    prefix, _ = prefix_gen(current_question)
    
   
    suffix = suffix_gen(current_question, verbose=verbose, **attack_kwargs)
    
    
    return prefix + suffix

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, required=True, help='Original Harmful Instructions')
    args = parser.parse_args()

    print(f"[*] Original Harmful Instructions: {args.query}")
    jailbreak_prompt = generate_dra_prompt(args.query, verbose=True)
    
    print("\n" + "="*30 + " GENERATED DRA PROMPT " + "="*30)
    print(jailbreak_prompt)
    print("="*80)