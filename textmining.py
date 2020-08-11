"""
Descrition:
    Tool made with Python 3, to help clean up text. 
    This class can be used during text preprocessing in Data Science.

Packages:
    - autocorrect
    - nltk
    - pandas
    - re
    - textblob
    - tqdm
"""

__author__ = ("Manitas Bahri")
__version__ = "1.0"
__date__ = "2020/08"

# Import Libraries
try:
    import nltk
    import pandas as pd
    import re

    from autocorrect import Speller
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    from tqdm import tqdm
    from textblob import TextBlob

except ImportError as e:
    print("""Import Error : The process could not import the necessary libraries. 
    Please run the following command to install the necessary packages:
    pip install -r requirements.txt """)


class TextMining:
    def __init__(self, df=None, df_abbreviation=None):
        """
        TextMining is Python packages, containing three method, used to help
        clean up text.

        Args:
            - df: The dataframe containing the text to be cleaned.
            - df_abbreviation: The data frame used to replace abbreviations with
            their equivalents.
        """
        self.dataframe = df
        self.df_abbreviation = df_abbreviation
        try:
            self.stop_words = set(stopwords.words("english"))
        
        except LookupError:
            nltk.download("stopwords")
            self.stop_words = set(stopwords.words("english"))

        self.spell_checker = Speller()
        self.stemmer = PorterStemmer()

        self.pattern_flatten = re.compile("\w+")
        self.pattern_identical_letters = re.compile(r"(.)\1{2,}")

    def remove_sequences(self, word:str):
        """
        Remove the sequences of the same letter in a word. Then, check the 
        spelling of the word.

        Arg:
            - word (str): The word containing a sequence of the same letter.

        
        Returns:
            string: New word without a sequence of same letter.
        
        Example:
            >>> word = "Peopllle"
            >>> miner = TextMining()
            >>> word = miner.remove_sequences(word)
            >>> print(word)
            people
        """
        word = word.lower()
        
        # If a word contains a sequence with more than three identical letters,
        # then this sequence is deleted.
        word = self.pattern_identical_letters.sub(r"\1\1", word)
        
        # Check the spelling of the word
        word = self.spell_checker(word) 
        
        return word
    
    def cleaner(self, column:str):
        """
        Cleaner method is a tool to normalized the text.

        Processus of cleaning:
            - Remove URL.
            - Tokenize the sentence.
            - Removes all characters that are neither a letter nor a number.
            - Remove english stop words.
            - Replace abbreviations with their equivalents.
            - Word stem process.

        Args:
            - column (str): The column in the dataframe containing the texts 
            to normalized.

        Return:
            New list containing clean texts.
        
        Example:
            >>> df = pd.DataFrame(data={"Tweets":["My car is so faaaassst",
                                  "Check out the latest Python3 news at http://python.org.", 
                                  "#Summer it's toooooo hot 🥵"], 
                        "Locations":["CA", "New York", "London"]})

            >>> df_abbreviation = pd.read_csv(main_path + "abbreviation_cleaned.txt", 
            delimiter=";")

            >>> miner = TextMining(df, df_abbreviation)
            >>> df["Tweets"] = miner.cleaner("Tweets")
            >>> df["Locations"] = miner.cleaner("Locations")

            >>> df

                Tweets                          Locations
            0	[car, fast]	                    [californ]
            1	[check, latest, python3, news]	[new, york]
            2	[summer, hot]	                [london]
        """
        # List containing the standardized text.
        filtered_sentences = []

        with tqdm(total=len(self.dataframe[column]), desc="Text Cleaning") as pgbar:
            for sentence in self.dataframe[column]:
                # List containing the standardized sentence.
                token_sentence = []
                # Remove http url.
                sentence = re.sub(r"http\S+", "", sentence)
                # Divide each sentence into words.
                sentence = word_tokenize(sentence)

                for word in sentence:
                    # Remove special characters.
                    word = re.sub("[^a-zA-Z0-9]+", "", word)
                    
                    # Remove sequecences of identical letters.
                    word = self.remove_sequences(word)

                    # Remove all stopword.
                    if word not in self.stop_words:

                        # Replace abbreviation with the right word.
                        if word in self.df_abbreviation["abbreviation"].values:
                            word = df_abbreviation[df_abbreviation["abbreviation"]==word]
                            word = word.word.to_string(index=False).lstrip()
                            word = word_tokenize(word)
                            # Delete the quotes.
                            word = str(word)[1:-1]
                            
                        # Abbreviations have already been stemmed.
                        else:
                            word = self.stemmer.stem(word)

                        # Add the cleaned word, as token, in the list containing 
                        # other word of the sentence.
                        if word:
                            token_sentence.append(word)

                # Checks that the token isn't null.
                if token_sentence:
                    # Flatten 2d list to 1d list.
                    token_sentence = self.pattern_flatten.findall(str(token_sentence))
                    filtered_sentences.append(token_sentence)
                
                else:
                    filtered_sentences.append("")

                # Update the progress bar.
                pgbar.update(1)

        return filtered_sentences

    def revome_duplicate_tokens(self, column):
        """
        Find duplicate tokens in sentence and delete one.

        Args:
            - column (str): The column in which duplicate tokens should 
            be removed.
        
        Return :
            New list without duplicate tokens.
        
        Example:
            >>> df = pd.DataFrame(data={"Token":[["fast", "car", "fast"],
                                            ["check", "latest", "python3", "python3", "news"], 
                                            ["summer", "hot"]]})

            >>> miner = TextMining(df)
            >>> df["Token"] = miner.revome_duplicate_tokens("Token")
            >>> df

                Token
            0	[fast, car]
            1	[check, latest, python3, news]
            2	[summer, hot]
        """
        filtered_tokens = []

        with tqdm(total=len(self.dataframe[column]), desc="Removal of duplicate tokens") as pgbar:
            for row in self.dataframe[column]:
                # Remove duplicate token while keeping order.
                row = list(dict.fromkeys(row))
                filtered_tokens.append(row)
                
                # Update the progress bar.
                pgbar.update(1)

        return filtered_tokens