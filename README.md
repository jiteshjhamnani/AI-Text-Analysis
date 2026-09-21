
# AI Textual Analysis — Instructions Documentation

*Blackcoffer Test Assignment — Data Extraction and NLP*

**Submitted by:** JITESH JHAMNANI

---

## 1. Approach

The solution has two stages:

1. Extracting the article text for every URL in `Input.xlsx`, and
2. Running textual analysis on each extracted article to produce the 13 output variables.

### 1.1 Data Extraction

First, the program reads the `URL_ID` and `URL` from `Input.xlsx`. It then opens each URL using the `requests` library.

A browser-like User-Agent is added to the request so that the website is less likely to block it.

After getting the webpage, BeautifulSoup is used to read the HTML and find the required content.

The program does the following:

- It first looks for the article title using the `<h1>` tag. If an `<h1>` is not found, it uses the page `<title>` instead.
- It then searches for the main article content using common HTML containers such as `div.td-post-content`, `div.entry-content`, `article`, and `main`.
- Unwanted parts of the webpage such as scripts, navigation menus, headers, footers, forms, buttons, and figures are removed.
- The remaining paragraph text is collected as the article content.
- Finally, the title and article text are saved in the `articles` folder using the `URL_ID` as the filename.

### 1.2 Textual Analysis

After extracting the articles, the program performs the required text analysis using NLTK.

The sentiment analysis uses the two word lists provided with the assignment:

- `positive-words.txt`
- `negative-words.txt`

The `Stopwords` folder is also used. All the `.txt` files inside this folder are combined and used to remove common words that are not useful for the analysis.

For processing the article text:

- `word_tokenize()` is used to split the text into individual words.
- `sent_tokenize()` is used to split the text into sentences.
- All words are converted to lowercase.
- Only alphabetic words are kept.
- Words present in the Stopwords list are removed.

The remaining words are then used for calculating word count, positive and negative scores, syllables, complex words, and average word length.

---

## 2. How to Run the Script

### 2.1 Folder Layout

Place these files/folders together in one project folder before running:

- `main.py`
- `Input.xlsx`
- `positive-words.txt`
- `negative-words.txt`
- `Stopwords/` (folder containing one or more `.txt` stop-word files)

Running the script will automatically create:

- `articles/` folder with one `<URL_ID>.txt` file per successfully scraped article
- `Output.xlsx` — the final results file, in the column order required by `Output Data Structure.xlsx`

### 2.2 Steps (VS Code)

1. Open the project folder in VS Code (`File → Open Folder...`).
2. Open a terminal in VS Code: `Terminal → New Terminal`.
3. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate      (Windows)
   ```

4. Install the required packages (see Dependencies below):

   ```bash
   pip install pandas openpyxl requests beautifulsoup4 lxml nltk
   ```

5. Download the two NLTK tokenizer models (one-time, run once in a Python shell or add to the top of the script):

   ```python
   import nltk
   nltk.download("punkt")
   nltk.download("punkt_tab")
   ```

6. Run the script from the terminal:

   ```bash
   python main.py
   ```

---

## 3. Dependencies

Python 3.8+ is required. Install all packages with:

```bash
pip install pandas openpyxl requests beautifulsoup4 lxml nltk
```

| Package | Purpose |
|---|---|
| pandas | Read `Input.xlsx`, build and write `Output.xlsx` |
| openpyxl | Excel engine used by pandas to read/write `.xlsx` files |
| requests | Download the HTML of each article URL |
| beautifulsoup4 | Parse HTML and locate the article title/body |
| lxml | Fast HTML parser backend used by BeautifulSoup |
| nltk | Sentence and word tokenization (`punkt` / `punkt_tab`) |

---

## 4. Code Links

- **GitHub Repo:** [https://github.com/jiteshjhamnani/AI-Text-Analysis](https://github.com/jiteshjhamnani/AI-Text-Analysis)
- **main.py (Python code):** [https://github.com/jiteshjhamnani/AI-Text-Analysis/blob/main/main.py](https://github.com/jiteshjhamnani/AI-Text-Analysis/blob/main/main.py)
- **Output.xlsx (output file):** [https://github.com/jiteshjhamnani/AI-Text-Analysis/blob/main/Output.xlsx](https://github.com/jiteshjhamnani/AI-Text-Analysis/blob/main/Output.xlsx)
