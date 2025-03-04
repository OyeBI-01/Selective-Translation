import os
import re
import openai
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

def extract_entities(text):
    """
    Use GPT-4 to extract the exact substrings (including punctuation) that should not be translated.
    """
    prompt = f"""
    Identify the exact substrings in the following text that should NOT be translated.
    These include proper nouns, brand names, technical terms, programming languages, etc.
    
    Text: "{text}"
    
    Return only a comma-separated list of the exact substrings that should remain unchanged.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that extracts exact substrings that should not be translated."},
            {"role": "user", "content": prompt}
        ]
    )
    raw = response.choices[0].message.content.strip()
    entities = [e.strip() for e in raw.split(",") if e.strip()]
    return entities

def mask_entities(text, entities):
    """
    Replace each entity in the text with a unique placeholder.
    If an entity appears with an attached punctuation (e.g., "'s" or "’s"),
    capture it and store the full match.
    """
    entity_map = {}
    masked_text = text
    for i, entity in enumerate(entities):
        placeholder = f"|||ENTITY_{i}|||"
        # Match the entity followed by an optional "'s" or "’s"
        pattern = re.compile(re.escape(entity) + r"((?:'s)|(?:’s))?", re.IGNORECASE)
        
        def sub_func(match):
            full_match = match.group(0)
            entity_map[placeholder] = full_match
            return placeholder
        
        masked_text = pattern.sub(sub_func, masked_text)
    return masked_text, entity_map

def restore_entities(translated_text, entity_map):
    """
    Use regex to match the placeholders (allowing extra spaces/case changes)
    and replace them with the original entities from the mapping.
    """
    # Pattern to match placeholders like "||| ENTITY_0 |||", ignoring extra spaces and case.
    pattern = re.compile(r'\|\|\|\s*(ENTITY_\d+)\s*\|\|\|', re.IGNORECASE)
    
    def rep_func(match):
        core = match.group(1).upper()  # Normalize to uppercase
        key = f"|||{core}|||"
        return entity_map.get(key, match.group(0))
    
    return pattern.sub(rep_func, translated_text)

def selective_translate(text, source_lang="en", target_lang="hi"):
    # Extract entities that should not be translated.
    entities = extract_entities(text)
    print("Extracted Entities:", entities)
    
    # Mask the entities in the text with unique placeholders.
    masked_text, entity_map = mask_entities(text, entities)
    print("Masked Text:", masked_text)
    
    # Translate the masked text.
    translated_masked_text = GoogleTranslator(source=source_lang, target=target_lang).translate(masked_text)
    print("Translated Masked Text:", translated_masked_text)
    
    # Restore the original entities.
    final_translation = restore_entities(translated_masked_text, entity_map)
    return final_translation

# Example Usage
input_text = "Google is developing an AI model for Python programming."
translated_output = selective_translate(input_text, source_lang="en", target_lang="hi")
print("Final Translated Output:", translated_output)
