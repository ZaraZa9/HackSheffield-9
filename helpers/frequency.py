import matplotlib.pyplot as plt


def word_frequency(text, words_to_check):
    text = text.lower()
    
    word_freq = {}
    
    for word_or_phrase in words_to_check:
        word_or_phrase_lower = word_or_phrase.lower()
        
        count = text.count(word_or_phrase_lower)
        word_freq[word_or_phrase] = count

    return word_freq