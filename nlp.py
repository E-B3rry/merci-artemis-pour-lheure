# Internal modules
import re

# External modules
import spacy
from spacy.matcher import Matcher


nlp_en = spacy.load("en_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")

matcher_en = Matcher(nlp_en.vocab)
matcher_fr = Matcher(nlp_fr.vocab)

# English patterns
patterns_en = [
    [{"LOWER": "what"}, {"LOWER": "time"}, {"LOWER": "is"}, {"LOWER": "it"}],
    [{"LOWER": "what"}, {"LOWER": "is"}, {"LOWER": "the"}, {"LOWER": "time"}],
    [{"LOWER": "do"}, {"LOWER": "you"}, {"LOWER": "have"}, {"LOWER": "the"}, {"LOWER": "time"}],
    [{"LOWER": {"IN": ["tell", "give"]}}, {"LOWER": "me"}, {"LOWER": "the"}, {"LOWER": "time"}],
    [{"LOWER": {"IN": ["can", "could", "may", "might"]}}, {"LOWER": "you"}, {"LOWER": "tell"}, {"LOWER": "me"}, {"LOWER": "the"}, {"LOWER": "time"}],
    [{'LOWER': {"REGEX": r"what('?s)?"}}, {"LOWER": "time"}],
    [{'LOWER': {"REGEX": r"what('?s)?"}}, {"LOWER": "current", "OP": "?"}, {"LOWER": "time"}],
    [{"LOWER": {"IN": ["can", "could", "may", "might"]}}, {"LOWER": "i"}, {"LOWER": "get"}, {"LOWER": "the"}, {"LOWER": "time"}],
]
matcher_en.add("TIME_REQUEST", patterns_en)

# French patterns
patterns_fr = [
    [{"LEMMA": {"IN": ["quel", "quell"]}}, {"LEMMA": "heure"}, {"LOWER": "est"}, {"LEMMA": {"IN": ["il", "ce", "-ce"]}}],
    [{"LEMMA": {"IN": ["quel", "quell"]}}, {"LEMMA": "heure"}, {"LEMMA": "il"}, {"LOWER": "est"}],
    [{"LEMMA": "il"}, {"LOWER": "est"}, {"LEMMA": {"IN": ["quel", "quell"]}}, {"LEMMA": "heure"}],
    [{"LEMMA": {"IN": ["donne", "dire"]}}, {"LEMMA": "moi", "OP": "?"}, {"LEMMA": "le"}, {"LEMMA": "heure"}],
    [{"TEXT": {"REGEX": r"est[-]?ce"}}, {"LOWER": "que"}, {"LOWER": "tu"}, {"LOWER": "as"}, {"LOWER": "l'heure"}],
    [{"LOWER": "tu"}, {"LEMMA": "-", "OP": "?"}, {"LOWER": "as"}, {"LEMMA": "le", "OP": '?'}, {"LEMMA": "heure"}],
    [{"LOWER": "as"}, {"LEMMA": "-", "OP": "?"}, {"LOWER": "tu"}, {"LEMMA": "le", "OP": '?'}, {"LEMMA": "heure"}],
]
matcher_fr.add("TIME_REQUEST", patterns_fr)

def is_time_request_spacy(text: str) -> bool:
    text = sanitize_text(text)
    # If "heure" is in the text, assume French, otherwise English
    if "heure" in text:
        doc = nlp_fr(text)
        # for token in doc:
        #     print(f"Token: {token.text:12} | Lemma: {token.lemma_:12} | POS: {token.pos_:6} | Tag: {token.tag_}")
        matches = matcher_fr(doc)
    else:
        doc = nlp_en(text)
        matches = matcher_en(doc)
    return bool(matches)

def sanitize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", ' ', text)
    return text
