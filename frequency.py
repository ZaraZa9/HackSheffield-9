import matplotlib.pyplot as plt


def word_frequency(text, words_to_check):
    
    text = text.lower()

    
    words = text.split()

    word_freq = {}
    
    for word in words_to_check:
        word_freq[word] = words.count(word.lower())

    return word_freq


text = "This is a simple example. This example shows how to count the frequency of a word in a text. Example is a common word."


words_to_check = ["example", "text", "word", "simple", "this"]


word_freq = word_frequency(text, words_to_check)


plt.plot(list(word_freq.keys()), list(word_freq.values()), marker='o', linestyle='-', color='b')

plt.title("Word Frequency in Text")
plt.xlabel("Words")
plt.ylabel("Frequency")


plt.show()
