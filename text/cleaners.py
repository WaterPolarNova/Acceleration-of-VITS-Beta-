""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
from phonemizer import phonemize
import pyopenjtalk
from jamo import h2j, j2hcj
from pypinyin import lazy_pinyin, BOPOMOFO
import jieba, cn2an

# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# Regular expression matching Japanese without punctuation marks:
_japanese_characters = re.compile(r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# Regular expression matching non-Japanese characters or punctuation marks:
_japanese_marks = re.compile(r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
  ('mrs', 'misess'),
  ('mr', 'mister'),
  ('dr', 'doctor'),
  ('st', 'saint'),
  ('co', 'company'),
  ('jr', 'junior'),
  ('maj', 'major'),
  ('gen', 'general'),
  ('drs', 'doctors'),
  ('rev', 'reverend'),
  ('lt', 'lieutenant'),
  ('hon', 'honorable'),
  ('sgt', 'sergeant'),
  ('capt', 'captain'),
  ('esq', 'esquire'),
  ('ltd', 'limited'),
  ('col', 'colonel'),
  ('ft', 'fort'),
]]

# List of (Latin alphabet, bopomofo) pairs:
_latin_to_bopomofo = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
  ('a', 'ㄟˉ'),
  ('b', 'ㄅㄧˋ'),
  ('c', 'ㄙㄧˉ'),
  ('d', 'ㄉㄧˋ'),
  ('e', 'ㄧˋ'),
  ('f', 'ㄝˊㄈㄨˋ'),
  ('g', 'ㄐㄧˋ'),
  ('h', 'ㄝˇㄑㄩˋ'),
  ('i', 'ㄞˋ'),
  ('j', 'ㄐㄟˋ'),
  ('k', 'ㄎㄟˋ'),
  ('l', 'ㄝˊㄛˋ'),
  ('m', 'ㄝˊㄇㄨˋ'),
  ('n', 'ㄣˉ'),
  ('o', 'ㄡˉ'),
  ('p', 'ㄆㄧˉ'),
  ('q', 'ㄎㄧㄡˉ'),
  ('r', 'ㄚˋ'),
  ('s', 'ㄝˊㄙˋ'),
  ('t', 'ㄊㄧˋ'),
  ('u', 'ㄧㄡˉ'),
  ('v', 'ㄨㄧˉ'),
  ('w', 'ㄉㄚˋㄅㄨˋㄌㄧㄡˋ'),
  ('x', 'ㄝˉㄎㄨˋㄙˋ'),
  ('y', 'ㄨㄞˋ'),
  ('z', 'ㄗㄟˋ')
]]

# List of (bopomofo, romaji) pairs:
_bopomofo_to_romaji = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
  ('ㄅㄛ', 'p⁼wo'),
  ('ㄆㄛ', 'pʰwo'),
  ('ㄇㄛ', 'mwo'),
  ('ㄈㄛ', 'fwo'),
  ('ㄅ', 'p⁼'),
  ('ㄆ', 'pʰ'),
  ('ㄇ', 'm'),
  ('ㄈ', 'f'),
  ('ㄉ', 't⁼'),
  ('ㄊ', 'tʰ'),
  ('ㄋ', 'n'),
  ('ㄌ', 'l'),
  ('ㄍ', 'k⁼'),
  ('ㄎ', 'kʰ'),
  ('ㄏ', 'h'),
  ('ㄐ', 'ʧ⁼'),
  ('ㄑ', 'ʧʰ'),
  ('ㄒ', 'ʃ'),
  ('ㄓ', 'ʦ`⁼'),
  ('ㄔ', 'ʦ`ʰ'),
  ('ㄕ', 's`'),
  ('ㄖ', 'ɹ`'),
  ('ㄗ', 'ʦ⁼'),
  ('ㄘ', 'ʦʰ'),
  ('ㄙ', 's'),
  ('ㄚ', 'a'),
  ('ㄛ', 'o'),
  ('ㄜ', 'ə'),
  ('ㄝ', 'e'),
  ('ㄞ', 'ai'),
  ('ㄟ', 'ei'),
  ('ㄠ', 'au'),
  ('ㄡ', 'ou'),
  ('ㄧㄢ', 'yeNN'),
  ('ㄢ', 'aNN'),
  ('ㄧㄣ', 'iNN'),
  ('ㄣ', 'əNN'),
  ('ㄤ', 'aNg'),
  ('ㄧㄥ', 'iNg'),
  ('ㄨㄥ', 'uNg'),
  ('ㄩㄥ', 'yuNg'),
  ('ㄥ', 'əNg'),
  ('ㄦ', 'əɻ'),
  ('ㄧ', 'i'),
  ('ㄨ', 'u'),
  ('ㄩ', 'ɥ'),
  ('ˉ', '→'),
  ('ˊ', '↑'),
  ('ˇ', '↓↑'),
  ('ˋ', '↓'),
  ('˙', ''),
  ('，', ','),
  ('。', '.'),
  ('！', '!'),
  ('？', '?'),
  ('—', '-')
]]

def expand_abbreviations(text):
  for regex, replacement in _abbreviations:
    text = re.sub(regex, replacement, text)
  return text


def expand_numbers(text):
  return normalize_numbers(text)


def lowercase(text):
  return text.lower()


def collapse_whitespace(text):
  return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
  return unidecode(text)


def japanese_to_romaji_with_accent(text):
  '''Reference https://r9y9.github.io/ttslearn/latest/notebooks/ch10_Recipe-Tacotron.html'''
  sentences = re.split(_japanese_marks, text)
  marks = re.findall(_japanese_marks, text)
  text = ''
  for i, sentence in enumerate(sentences):
    if re.match(_japanese_characters, sentence):
      if text!='':
        text+=' '
      labels = pyopenjtalk.extract_fullcontext(sentence)
      for n, label in enumerate(labels):
        phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
        if phoneme not in ['sil','pau']:
          text += phoneme.replace('ch','ʧ').replace('sh','ʃ').replace('cl','Q')
        else:
          continue
        n_moras = int(re.search(r'/F:(\d+)_', label).group(1))
        a1 = int(re.search(r"/A:(\-?[0-9]+)\+", label).group(1))
        a2 = int(re.search(r"\+(\d+)\+", label).group(1))
        a3 = int(re.search(r"\+(\d+)/", label).group(1))
        if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil','pau']:
          a2_next=-1
        else:
          a2_next = int(re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
        # Accent phrase boundary
        if a3 == 1 and a2_next == 1:
          text += ' '
        # Falling
        elif a1 == 0 and a2_next == a2 + 1 and a2 != n_moras:
          text += '↓'
        # Rising
        elif a2 == 1 and a2_next == 2:
          text += '↑'
    if i<len(marks):
      text += unidecode(marks[i]).replace(' ','')
  return text


def latin_to_hangul(text):
  for regex, replacement in _latin_to_hangul:
    text = re.sub(regex, replacement, text)
  return text


def latin_to_bopomofo(text):
  for regex, replacement in _latin_to_bopomofo:
    text = re.sub(regex, replacement, text)
  return text


def bopomofo_to_romaji(text):
  for regex, replacement in _bopomofo_to_romaji:
    text = re.sub(regex, replacement, text)
  return text


def basic_cleaners(text):
  '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def transliteration_cleaners(text):
  '''Pipeline for non-English text that transliterates to ASCII.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def japanese_cleaners(text):
  text=japanese_to_romaji_with_accent(text)
  if re.match('[A-Za-z]',text[-1]):
    text += '.'
  return text


def japanese_cleaners2(text):
  return japanese_cleaners(text).replace('ts','ʦ').replace('...','…')


def english_cleaners(text):
  '''Pipeline for English text, including abbreviation expansion.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_abbreviations(text)
  phonemes = phonemize(text, language='en-us', backend='espeak', strip=True)
  phonemes = collapse_whitespace(phonemes)
  return phonemes


def english_cleaners2(text):
  '''Pipeline for English text, including abbreviation expansion. + punctuation + stress'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_abbreviations(text)
  phonemes = phonemize(text, language='en-us', backend='espeak', strip=True, preserve_punctuation=True, with_stress=True)
  phonemes = collapse_whitespace(phonemes)
  return phonemes


def japanese_phrase_cleaners(text):
  '''Pipeline for dividing Japanese text into phrases.'''
  sentences = re.split(_japanese_marks, text)
  marks = re.findall(_japanese_marks, text)
  text = ''
  for i, sentence in enumerate(sentences):
    if re.match(_japanese_characters, sentence):
      if text != '':
        text += ' '
      labels = pyopenjtalk.extract_fullcontext(sentence)
      for n, label in enumerate(labels):
        phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
        if phoneme not in ['sil','pau']:
          text += phoneme
        else:
          continue
        a3 = int(re.search(r"\+(\d+)/", label).group(1))
        if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil','pau']:
          a2_next=-1
        else:
          a2_next = int(re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
        # Accent phrase boundary
        if a3 == 1 and a2_next == 1:
          text += ' '
    if i<len(marks):
      text += unidecode(marks[i]).replace(' ','')
  if re.match('[A-Za-z]',text[-1]):
    text += '.'
  return text
