import pandas as pd
import pymorphy3
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download('punkt')
nltk.download('stopwords')


def preprocess(text, stop_words, punctuation_marks, morph):
    tokens = word_tokenize(text.lower())
    preprocessed_text = []
    for token in tokens:
        if token not in punctuation_marks:
            lemma = morph.parse(token)[0].normal_form
            if lemma not in stop_words:
                preprocessed_text.append(lemma)
                print(lemma)
    return " ".join(preprocessed_text)


def main():
    punctuation_marks = [",", ".", "(", ")", "-"]
    stop_words = stopwords.words("russian")
    morph = pymorphy3.MorphAnalyzer()

    data = pd.read_csv("src/ksr.csv", sep=",")

    data['name'] = data['name'].apply(lambda x: preprocess(x, stop_words, punctuation_marks, morph))

    data.to_csv("src/ksr_lemma.csv", index=False, columns=['code', 'name', 'uint'])


if __name__ == "__main__":
    main()
