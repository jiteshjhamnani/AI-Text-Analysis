import os
import re
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize


INPUT_FILE = "Input.xlsx"
OUTPUT_FILE = "Output.xlsx"

POSITIVE_FILE = "positive-words.txt"
NEGATIVE_FILE = "negative-words.txt"

STOPWORDS_FOLDER = "Stopwords"
ARTICLES_FOLDER = "articles"

os.makedirs(ARTICLES_FOLDER, exist_ok=True)


def load_words(filename):

    words = set()

    try:
        with open(filename, "r", encoding="latin-1") as file:
            for line in file:
                word = line.strip().lower()
                if word and not word.startswith(";"):
                    words.add(word)
    except FileNotFoundError:
        print("File not found:", filename)
    return words

positive_words = load_words(POSITIVE_FILE)
negative_words = load_words(NEGATIVE_FILE)


def load_stopwords():
    stop_words = set()

    if not os.path.exists(STOPWORDS_FOLDER):
        print("Stopwords folder not found!")
        return stop_words

    for filename in os.listdir(STOPWORDS_FOLDER):
        if filename.endswith(".txt"):
            filepath = os.path.join(
                STOPWORDS_FOLDER,
                filename
            )
            try:
                with open(
                    filepath,
                    "r",
                    encoding="latin-1"
                ) as file:
                    for line in file:

                        word = line.strip().lower()

                        if word:
                            stop_words.add(word)

            except Exception as e:

                print("Could not read:", filepath)
                print(e)

    return stop_words


stop_words = load_stopwords()

print("Positive words:", len(positive_words))
print("Negative words:", len(negative_words))
print("Stopwords:", len(stop_words))



def extract_article(url):

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.content,
            "lxml"
        )

    except Exception as e:

        print("Could not open URL:", e)

        return "", ""


    title = ""

    h1 = soup.find("h1")

    if h1:
        title = h1.get_text(
            " ",
            strip=True
        )

    elif soup.title:

        title = soup.title.get_text(
            " ",
            strip=True
        )


    article = None

    selectors = [
        "div.td-post-content",
        "div.td_block_template_1",
        "div.post-content",
        "div.entry-content",
        "article .entry-content",
        "article",
        "main"
    ]

    for selector in selectors:

        article = soup.select_one(selector)

        if article:
            break


    if article:

        unwanted = [
            "script",
            "style",
            "noscript",
            "iframe",
            "nav",
            "header",
            "footer",
            "form",
            "button",
            "aside",
            "figure",
            "figcaption"
        ]

        for tag_name in unwanted:

            for tag in article.find_all(tag_name):
                tag.decompose()


        paragraphs = []

        for paragraph in article.find_all("p"):

            text = paragraph.get_text(
                " ",
                strip=True
            )

            if text:
                paragraphs.append(text)


        if paragraphs:

            article_text = "\n\n".join(paragraphs)

        else:

            article_text = article.get_text("\n", strip=True)


    else:

        print("Article container not found.")

        paragraphs = []

        for paragraph in soup.find_all("p"):

            text = paragraph.get_text(
                " ",
                strip=True
            )

            if text:
                paragraphs.append(text)

        article_text = "\n\n".join(paragraphs)


    article_text = re.sub(r"\n\s*\n+","\n\n",article_text)

    article_text = re.sub(r"[ \t]+"," ",article_text)

    article_text = article_text.strip()


    return title, article_text


def save_article(url_id, title, article_text):

    filename = os.path.join(
        ARTICLES_FOLDER,
        url_id + ".txt"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(title)
        file.write("\n\n")
        file.write(article_text)

    return filename


def clean_text(text):

    text = text.lower()

    tokens = word_tokenize(text)

    cleaned_words = []

    for word in tokens:

        if not word.isalpha():
            continue

        if word in stop_words:
            continue

        cleaned_words.append(word)

    return cleaned_words


def count_syllables(word):

    word = word.lower()

    word = re.sub(
        r"[^a-z]",
        "",
        word
    )

    if not word: return 0

    if len(word) <= 3: return 1

    vowels = "aeiouy"

    syllables = 0
    previous_vowel = False

    for char in word:

        if char in vowels:

            if not previous_vowel:
                syllables += 1

            previous_vowel = True

        else:

            previous_vowel = False


    if word.endswith("es") and syllables > 1:

        syllables -= 1

    elif word.endswith("ed") and syllables > 1:

        syllables -= 1

    elif word.endswith("e") and syllables > 1:

        syllables -= 1


    return max(1, syllables)


def count_personal_pronouns(text):

    pattern = r"\b(I|we|my|ours|us)\b"

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    count = 0

    for word in matches:

        if word == "US":
            continue

        count += 1

    return count


def analyze_article(text):

    try:

        sentences = sent_tokenize(text)

    except Exception:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        sentences = [
            sentence
            for sentence in sentences
            if sentence.strip()
        ]


    sentence_count = len(sentences)

    cleaned_words = clean_text(text)

    word_count = len(cleaned_words)


    positive_score = 0
    negative_score = 0

    for word in cleaned_words:

        if word in positive_words:
            positive_score += 1

        if word in negative_words:
            negative_score += 1


    polarity_score = (positive_score - negative_score) / ( positive_score + negative_score + 0.000001 )


    subjectivity_score = ( positive_score + negative_score ) / ( word_count + 0.000001 )


    if sentence_count > 0:
        avg_sentence_length = ( word_count / sentence_count )

    else:
        avg_sentence_length = 0


    total_syllables = 0
    complex_word_count = 0

    for word in cleaned_words:

        syllables = count_syllables(word)

        total_syllables += syllables

        if syllables > 2:
            complex_word_count += 1


    if word_count > 0: 
        percentage_complex_words = ( complex_word_count / word_count )

    else:
        percentage_complex_words = 0


    fog_index = 0.4 * ( avg_sentence_length + percentage_complex_words )


    if sentence_count > 0:
        avg_words_per_sentence = ( word_count / sentence_count )

    else:
        avg_words_per_sentence = 0


    if word_count > 0:
        syllable_per_word = ( total_syllables / word_count )

    else:

        syllable_per_word = 0


    personal_pronouns = count_personal_pronouns(
        text
    )


    if word_count > 0:

        total_characters = 0

        for word in cleaned_words:
            total_characters += len(word)

        avg_word_length = (
            total_characters / word_count
        )

    else:

        avg_word_length = 0


    return {

        "POSITIVE SCORE": positive_score,

        "NEGATIVE SCORE": negative_score,

        "POLARITY SCORE": polarity_score,

        "SUBJECTIVITY SCORE": subjectivity_score,

        "AVG SENTENCE LENGTH":  avg_sentence_length,

        "PERCENTAGE OF COMPLEX WORDS": percentage_complex_words,

        "FOG INDEX": fog_index,

        "AVG NUMBER OF WORDS PER SENTENCE": avg_words_per_sentence,

        "COMPLEX WORD COUNT":  complex_word_count,

        "WORD COUNT": word_count,

        "SYLLABLE PER WORD": syllable_per_word,

        "PERSONAL PRONOUNS": personal_pronouns,

        "AVG WORD LENGTH": avg_word_length
    }


def main():

    try:
        data = pd.read_excel(INPUT_FILE)

    except Exception as e:

        print("Could not read Input.xlsx")
        print(e)
        return


    print(
        "Total URLs:",
        len(data)
    )
    results = []

    for index, row in data.iterrows():

        url_id = str( row["URL_ID"] ).strip()

        url = str( row["URL"] ).strip()

        print(" ")
        print( "Processing:", index + 1, "/", len(data) )

        print("URL_ID:", url_id)


        title, article_text = extract_article(url)


        if not article_text:

            print("No article text found. Writing zero-value row.")

            analysis = {
                "POSITIVE SCORE": 0,
                "NEGATIVE SCORE": 0,
                "POLARITY SCORE": 0,
                "SUBJECTIVITY SCORE": 0,
                "AVG SENTENCE LENGTH": 0,
                "PERCENTAGE OF COMPLEX WORDS": 0,
                "FOG INDEX": 0,
                "AVG NUMBER OF WORDS PER SENTENCE": 0,
                "COMPLEX WORD COUNT": 0,
                "WORD COUNT": 0,
                "SYLLABLE PER WORD": 0,
                "PERSONAL PRONOUNS": 0,
                "AVG WORD LENGTH": 0
            }

        else:

            print("Title:", title)

            print( "Characters:", len(article_text) )

            filename = save_article( url_id, title, article_text )

            print(  "Saved:", filename )

            analysis = analyze_article( article_text )

            print( "Word count:", analysis["WORD COUNT"] )

            print(  "Positive:", analysis["POSITIVE SCORE"]  )

            print(  "Negative:", analysis["NEGATIVE SCORE"] )

        result = {

            "URL_ID": url_id,

            "URL": url,

            "POSITIVE SCORE":
                analysis["POSITIVE SCORE"],

            "NEGATIVE SCORE":
                analysis["NEGATIVE SCORE"],

            "POLARITY SCORE":
                analysis["POLARITY SCORE"],

            "SUBJECTIVITY SCORE":
                analysis["SUBJECTIVITY SCORE"],

            "AVG SENTENCE LENGTH":
                analysis["AVG SENTENCE LENGTH"],

            "PERCENTAGE OF COMPLEX WORDS":
                analysis[ "PERCENTAGE OF COMPLEX WORDS" ],

            "FOG INDEX": analysis["FOG INDEX"],

            "AVG NUMBER OF WORDS PER SENTENCE": analysis[ "AVG NUMBER OF WORDS PER SENTENCE" ],

            "COMPLEX WORD COUNT": analysis["COMPLEX WORD COUNT"],

            "WORD COUNT": analysis["WORD COUNT"],

            "SYLLABLE PER WORD":  analysis["SYLLABLE PER WORD"],

            "PERSONAL PRONOUNS": analysis["PERSONAL PRONOUNS"],

            "AVG WORD LENGTH": analysis["AVG WORD LENGTH"]
        }

        results.append(result)



    columns = [

        "URL_ID",
        "URL",
        "POSITIVE SCORE",
        "NEGATIVE SCORE",
        "POLARITY SCORE",
        "SUBJECTIVITY SCORE",
        "AVG SENTENCE LENGTH",
        "PERCENTAGE OF COMPLEX WORDS",
        "FOG INDEX",
        "AVG NUMBER OF WORDS PER SENTENCE",
        "COMPLEX WORD COUNT",
        "WORD COUNT",
        "SYLLABLE PER WORD",
        "PERSONAL PRONOUNS",
        "AVG WORD LENGTH"
    ]


    output = pd.DataFrame(
        results,
        columns=columns
    )
    try:
        output.to_excel(
            OUTPUT_FILE,
            index=False
        )


    except Exception as e:

        print("Could not create Output.xlsx")
        print(e)


if __name__ == "__main__":
    main()