import nltk
import spacy

nltk.download("punkt_tab")
from nltk.tokenize import word_tokenize

nlp = spacy.load("en_core_web_sm")


def calculate_score(user_content: list, stt_confidences: list) -> tuple:
    total_score = 0
    total_words = 0

    for i, user_input in enumerate(user_content):
        score = 0
        words = word_tokenize(user_input)
        total_words += len(words)

        def grammar_score():
            doc = nlp(user_input)
            return 2 if all(token.is_alpha or token.is_punct for token in doc) else 1

        def relevance_score():
            return 2 if len(user_input.split()) > 3 else 1

        def engagement_score():
            return 2 if "?" in user_input or len(user_input.split()) > 5 else 1

        def coherence_score():
            return 2 if len(words) > 3 else 1

        def pronunciation_score():
            return 2 if stt_confidences[i] > 0.8 else 1

        score += grammar_score()
        score += relevance_score()
        score += engagement_score()
        score += coherence_score()
        score += pronunciation_score()
        total_score += score

    avg_score = round(total_score / len(user_content), 2) if user_content else 0
    return avg_score, total_words
