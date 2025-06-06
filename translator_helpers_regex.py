import re

def regex_sentence_split(text):
    # 使用正则按标点断句，适配中英文
    sentences = re.split(r'(?<=[。！？!?\.])\s+', text.strip())
    return [s for s in sentences if s]

def smart_translate(text, target_lang, client, translator_fn):
    sentences = regex_sentence_split(text)
    translated_sentences = [translator_fn(s, target_lang, client) for s in sentences]
    return "\n".join(translated_sentences)