import re
import speech_recognition as sr
from math import *
from typing import List


# ----------------------------------------------------------------------------------------------------------------------

def silnia(n): return n * silnia(n - 1) if n > 1 else 1


# ----------------------------------------------------------------------------------------------------------------------

operation_switcher = {
    'plus': '+',
    'minus': '-',
    'razy': '*',
    'x': '*',
    'podzielone': '/',
    'potęga': '**'
}
not_working_operation = {
    'pierwiastek': sqrt,
    'silnia': silnia,
    'cosinus': cos,
    'sinus': sin
}


# ----------------------------------------------------------------------------------------------------------------------

def check_missing_char(text_in: str) -> List[str]:
    parse_word = r'\d+|[+/*-]'
    elem = re.findall(parse_word, text_in)
    return elem


# ----------------------------------------------------------------------------------------------------------------------


def text_to_math_bracket(key_word: str, translated_text_list: List[str]):
    # merging words like: 'otwórz' 'nawias' together in one word: 'otwórz nawias' (open brackets)
    indexes_word = [i for i, x in enumerate(translated_text_list) if x == key_word]  # indexes for all word: 'nawias'

    # finding all words to delete
    words_to_delete = [key_word]
    it = 0
    for i in indexes_word:
        translated_text_list.insert(i + it + 1, translated_text_list[i + it - 1] + ' ' + key_word)
        words_to_delete.append(translated_text_list[i + it - 1])
        it += 1

    # merging together words 'otwórz'/'zamknij' 'nawias' in one word: 'otwórz/zamknij nawias' (open/close brackets)
    for _, word in enumerate(words_to_delete):
        translated_text_list = list(filter(lambda a: a != word, translated_text_list))

    # changing all words to modify to appropriate chars: '(' or ')'
    words_to_modify = ['otwórz nawias', 'zamknij nawias']
    for i, word in enumerate(translated_text_list):
        if word in words_to_modify:
            temp = True if word == 'otwórz nawias' else False
            if temp:
                translated_text_list[i] = '('
            else:
                translated_text_list[i] = ')'
        for key, value in operation_switcher.items():
            if word == key:
                translated_text_list[i] = value

    translated_text = ' '.join(translated_text_list)  # merging all math chars in one string
    print("Translated text into math notation: ", translated_text)

    try:
        result = eval(translated_text, not_working_operation)
    except SyntaxError:
        print("\nUnexpected characters, cannot check where the error is.")
        result = "Not a Number!"

    return result


# ----------------------------------------------------------------------------------------------------------------------

def text_to_math_no_bracket(translated_text_list: List[str], forbidden_first_chars, forbidden_last_chars):
    # changing all math words to math chars, for example: 'razy' -> '*'
    for i, word in enumerate(translated_text_list):
        for key, value in operation_switcher.items():
            if word == key:
                translated_text_list[i] = value

    translated_text_list = ' '.join(translated_text_list)
    translated_text_list = check_missing_char(translated_text_list)

    # checking characters in first and last positions
    error_message_list = []
    if translated_text_list[0] in forbidden_first_chars:
        error_message_list.append('Unexpected first character!')
    if translated_text_list[-1] in forbidden_last_chars:
        error_message_list.append('Unexpected last character!')

    # if first and last position is correct: finding all positions with incorrect/doubled chars
    bad_tuple_indexes_list = []
    if not error_message_list:
        indexes_not_digits = [idx for idx, word in enumerate(translated_text_list) if not word.isdigit()]
        for idx, word in enumerate(indexes_not_digits):
            if idx < len(indexes_not_digits) - 1:
                if word == indexes_not_digits[idx + 1] - 1:
                    bad_tuple_indexes_list.append((word, word + 1))

    # reducing tuple to list, deleting the same values
    reduced_bad_tuple_ind_list = []
    for t in bad_tuple_indexes_list:
        for x in t:
            if x not in reduced_bad_tuple_ind_list:
                reduced_bad_tuple_ind_list.append(x)

    translated_text_list = ' '.join(translated_text_list)
    print("Translated text into math notation: ", translated_text_list)

    try:
        result = eval(translated_text_list, not_working_operation)
    except SyntaxError:
        if 'Unexpected first character!' in error_message_list:
            print("\nUnexpected first character! \nNote: Firstly set appropriate first character. Forbidden first "
                  "characters: {}".format(forbidden_first_chars))
        elif 'Unexpected last character!' in error_message_list:
            print("\nUnexpected last character! \nNote: Firstly set appropriate last character. Forbidden last "
                  "characters: {}".format(forbidden_last_chars))
        else:
            print("Unexpected character at positions: ", reduced_bad_tuple_ind_list)
        result = "Not a Number!"

    return result


# ----------------------------------------------------------------------------------------------------------------------

def calculator(translated_text: str):
    translated_text = translated_text.lower()
    translated_text_list = translated_text.split()
    print("Translated text in Polish: ", translated_text)
    key_word = 'nawias'
    forbidden_first_chars = ['*', '/', '+']
    forbidden_last_chars = forbidden_first_chars + ['-']

    if key_word in translated_text_list:
        result = text_to_math_bracket(key_word, translated_text_list)
    else:
        result = text_to_math_no_bracket(translated_text_list, forbidden_first_chars, forbidden_last_chars)

    print("\nResult: ", result)


# ----------------------------------------------------------------------------------------------------------------------

def listen(recognizer):
    with sr.Microphone() as source:
        print('Speak now')
        audio = recognizer.listen(source)
    try:
        text_in = recognizer.recognize_google(audio, language='pl-PL')
        print(text_in)
        return text_in
    except sr.UnknownValueError:
        return "I don't hear you!"


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        r = sr.Recognizer()
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src)
    except IOError:
        print('No microphone detected!')
        exit(0)

    audio_text = listen(r)

    # Testing sentences
    text = "Otwórz nawias otwórz nawias 4 plus 2 zamknij nawias razy 3 zamknij nawias potęga 2 plus 4 potęga 2"
    text2 = "silnia otwórz nawias 4 zamknij nawias plus silnia otwórz nawias 7 zamknij nawias"
    text3 = "pierwiastek otwórz nawias 225 zamknij nawias"
    text4 = "4 podzielone 4 razy razy razy 8"
    calculator(audio_text)
