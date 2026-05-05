import json
import os
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
URL = os.getenv("URL")
MODEL = os.getenv("MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))
PROMPT = os.getenv("PROMPT")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def is_valid_translation(text):
    """
    Check first meaningful character is ASCII
    """
    if not text:
        return False

    # remove leading spaces / quotes
    cleaned = text.strip().lstrip("\"'“”")

    if not cleaned:
        return False

    return ord(cleaned[0]) < 128


def translate(text, history):
    messages = history + [
        {
            "role": "user",
            "content": text
        }
    ]

    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "messages": messages
    }

    res = requests.post(URL, headers=HEADERS, json=payload)
    if res.status_code != 200:
        print(f"API error: {res.status_code} {res.text}")
        return "[translation error]"
    output = res.json()["choices"][0]["message"]["content"]

    return output


def translate_with_retry(text, history, max_retries=3):
    for attempt in range(max_retries):
        result = translate(text, history)

        if is_valid_translation(result):
            return result

        print(f"Retrying ({attempt+1}/{max_retries}) → invalid: {result}")

    return "[translation failed]"

def load_dictionary(path="note.txt"):
    mapping = {}

    if not os.path.exists(path):
        return mapping

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or "=" not in line:
                continue

            jp, en = line.split("=", 1)
            mapping[jp.strip()] = en.strip()

    return mapping

def apply_dictionary(text, mapping):
    original_text = text
    for jp, en in mapping.items():
        text = text.replace(jp, en+" ")
    if text != original_text:
        print(f"After dictionary: {text}")
    return text

def load_json(path):
    print(f"Translating {path}...")
    with open(path, "r", encoding="utf-8") as f:
        data= json.load(f)
    print(f"Loaded: {path}")
    conversation_history = [
    {
        "role": "system",
        "content": PROMPT
    }
    ]
    dictionary = load_dictionary()
    for block in data["parsing_res_list"]:
        jp_text = block["block_content"]
        processed_text = apply_dictionary(jp_text, dictionary)

        en_text = translate_with_retry(processed_text, conversation_history)

        block["translated_content"] = en_text

        conversation_history.append({
            "role": "user",
            "content": jp_text
        })
        conversation_history.append({
            "role": "assistant",
            "content": en_text
        })

        print(jp_text, "→", en_text)


    # Save result
    with open(f"{path}_translated.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {path}_translated.json")


def run_all_translate(path):
    for file in os.listdir(path):
        if file.endswith(".json") and not file.endswith("_translated.json"):
            print(f"Processing {file}")
            load_json(f"{path}/{file}")

# run_all_translate("output/")
