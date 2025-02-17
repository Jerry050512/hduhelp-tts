from langdetect import detect, lang_detect_exception

def detect_language(text):
    """
    Detects the language of the given text and classifies it into a predefined set.

    Args:
        text (str): The text to detect the language of.

    Returns:
        str: The language code ("EN", "ES", "FR", "ZH", "JP", "KR") or "Unknown" if detection fails.
    """
    try:
        lang = detect(text)
        if lang == 'en':
            return "EN"
        elif lang == 'es':
            return "ES"
        elif lang == 'fr':
            return "FR"
        elif lang == 'zh-cn' or lang == 'zh-tw' or lang == 'zh': #handle various chinese language codes.
            return "ZH"
        elif lang == 'ja':
            return "JP"
        elif lang == 'ko':
            return "KR"
        else:
            return "Unknown"
    except lang_detect_exception.LangDetectException:
        return "Unknown"

# Example Usage:
def example():
    texts = [
        "This is an English sentence.",
        "Esta es una frase en español.",
        "Ceci est une phrase en français.",
        "这是一个中文句子。",
        "これは日本語の文です。",
        "이것은 한국어 문장입니다.",
        "Some random characters: asdfghjkl",
        "混合 sentence with english and 中文"
    ]

    for text in texts:
        language = detect_language(text)
        print(f"Text: '{text}' - Language: {language}")

if __name__ == "__main__":
    example()