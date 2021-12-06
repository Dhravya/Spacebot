from typing import Sequence
import warnings
import random


def owofy(text: Sequence, *, wanky: bool = False, _print: bool = False):
    """translates your given text to owo!

    :param text: the string/array you want to translate to owo on
    :type text: typing.Sequence
    :param wanky: A boolean that represents if you want the word 'wank' in your translated text. Defaults to `False`
    :type wanky: bool
    :param _print: If you want to print the given output. Defaults to `False`
    :type _print: bool
    :return: Your requested, translated text in str/array/printed form!
    :rtype: Union[str, list, print()]
    """

    def last_replace(s, old, new):
        li = s.rsplit(old, 1)
        return new.join(li)

    def text_to_owo(textstr):

        exclamations = ("?", "!", ".", "*")

        prefixes = [
            "Haii UwU ",
            "Hiiiiii 0w0 ",
            "Hewoooooo >w< ",
            "*W* ",
            "mmm~ uwu ",
            "Oh... Hi there {} ".format(random.choice(["·///·", "(。O⁄ ⁄ω⁄ ⁄ O。)"])),
        ]  # I need a life, help me

        subs = {
            "why": "wai",
            "Why": "Wai",
            "Hey": "Hai",
            "hey": "hai",
            "ahw": "ao",
            "Hi": "Hai",
            "hi": "hai",
            "you": "u",
            "L": "W",
            "l": "w",
            "R": "W",
            "r": "w",
        }

        textstr = random.choice(prefixes) + textstr
        if not textstr.endswith(exclamations):
            textstr += " uwu"

        smileys = [";;w;;", "^w^", ">w<", "UwU", r"(・`ω\´・)"]

        if not wanky:  # to prevent wanking * w *
            textstr = textstr.replace("Rank", "Ⓡank").replace("rank", "Ⓡank")
            textstr = textstr.replace("Lank", "⒧ank").replace("lank", "⒧ank")

        textstr = last_replace(textstr, "there!", "there! *pounces on u*")

        for key, val in subs.items():
            textstr = textstr.replace(key, val)

        textstr = last_replace(textstr, "!", "! {}".format(random.choice(smileys)))
        textstr = last_replace(
            textstr, "?", "? {}".format(random.choice(["owo", "O·w·O"]))
        )
        textstr = last_replace(textstr, ".", ". {}".format(random.choice(smileys)))

        vowels = ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"]

        if not wanky:
            textstr = textstr.replace("Ⓡank", "rank").replace("⒧ank", "lank")

        for v in vowels:
            if "n{}".format(v) in textstr:
                textstr = textstr.replace("n{}".format(v), "ny{}".format(v))
            if "N{}".format(v) in textstr:
                textstr = textstr.replace(
                    "N{}".format(v), "N{}{}".format("Y" if v.isupper() else "y", v)
                )

        return textstr

    if not isinstance(text, str):
        owoed_msgs = map(text_to_owo, text)

        return owoed_msgs if not _print else print(*owoed_msgs, sep="\n")

    return text_to_owo(text) if not _print else print(text_to_owo(text))


def clap_emojifier(text: Sequence, *, _print: bool = False):
    """Appends your given string/array the clap 👏 emoji after every word/space.

    :param text: The text/array you want to "translate"
    :param _print: A boolean that represents if the given text is going to get printed to the console or not. Defaults to `False`.
    :return: Your clapped text/array!
    :rtype: Union[str, list, print()]
    """

    # Main translator is one line long LMAO
    clap_it = lambda _: " 👏 ".join([*_.split(" ")])

    if not isinstance(text, str):
        clapped_msgs = map(clap_it, text)

        return clapped_msgs if not _print else print(*clapped_msgs, sep="\n")

    return clap_it(text) if not _print else print(clap_it(text))


def strong_british_accent(
    text: Sequence, *, add_dashes: bool = True, _print: bool = False
):
    """Converts your given string/array to a kind-of strong british accent (if you're nonsensical about it...)

    :param text: The text/array you want to convert to
    :param add_dashes: A boolean that represents if the translation is going to have dashes or not. Defaults to `True`
    :param _print: A boolean that represents if the translation is going to get printed to the console or not. Defaults to `False`
    :return: Your translated text/array!
    :rtype: Union[str, list, print()]
    """

    def brit(brsentence):

        brsentence = brsentence.replace("it was ", "it was quite ")

        # Words relating to ppl
        brsentence = (
            brsentence.replace("friend", "mate")
            .replace("pal", "mate")
            .replace("buddy", "mate")
            .replace("person", "mate")
            .replace("man", "mate")
            .replace("people", "mates")
        )

        # Some weird past tense stuff i don't even know
        brsentence = brsentence.replace("standing", "stood")
        brsentence = brsentence.replace("sitting", "sat")

        # Pronunciations of syllables
        brsentence = brsentence.replace("o ", "oh ")
        brsentence = brsentence.replace("ee", "ea")
        brsentence = (
            brsentence.replace("er ", "-a ")
            .replace("er", "-a")
            .replace("or ", "-a ")
            .replace("or", "-a")
            .replace("ar ", "-a ")
            .replace("ar", "-a")
        )

        if not add_dashes:
            brsentence = brsentence.replace("-", "")

        brsentence = brsentence.replace("a", "ah")

        return brsentence

    if not isinstance(text, str):
        britished_msgs = map(brit, text)

        return britished_msgs if not _print else print(*britished_msgs, sep="\n")

    msg = brit(text)
    return msg if not _print else print(msg)


def text_to_emoji(text: Sequence, *, _print: bool = False):
    num_words = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
    }
    two_char_emojis = {
        "<3": "heart",
        ":)": "slight_smile",
        ":D": "smile",
        "B)": "sunglasses",
        ":P": "stuck_out_tongue",
        ":(": "frowning",
        ";(": "sob",
    }
    special_char_words = {
        "?": "question",
        "!": "exclamation",
        "#": "hash",
        "*": "asterisk",
    }
    unicode_base = ":{}:"

    def _convert_to_emoji(argument):
        new_text = ""
        finished_index = (
            None  # this var only exists to skip next char from two_char_emojis
        )
        for index, i in enumerate(argument):
            if index == finished_index:
                continue
            elif (
                not index == len(argument) - 1
                and i + text[index + 1] in two_char_emojis
            ):
                new_text += unicode_base.format(two_char_emojis[i + text[index + 1]])
                finished_index = index + 1
            elif i.isalpha():
                new_text += unicode_base.format("regional_indicator_" + i)
            elif i.isnumeric():
                new_text += unicode_base.format(num_words[i])
            elif i in special_char_words:
                new_text += unicode_base.format(special_char_words[i])
            else:
                new_text += i
            new_text += " "

        return new_text

    def print_emoji_text_to_emojis(argument):
        try:
            import emoji
        except ImportError:
            warnings.warn(
                "The emojis may not be printed properly since you didn't install the `emoji` module for converting emoji codes to emojis."
            )
            return print(argument)
        return print(emoji.emojize(argument, use_aliases=True, variant="emoji_type"))

    if isinstance(text, str):
        out = _convert_to_emoji(text)
        return print_emoji_text_to_emojis(out) if _print else out

    outputs = map(_convert_to_emoji, text)
    return outputs if not _print else map(print_emoji_text_to_emojis, text)
