import logging
from collections import deque, OrderedDict
from typing import Union, List
from itertools import zip_longest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_UPOS_MAPPING = [
    ("NOUN", "N"),  # 4130481
    ("VERB", "V"),  # 3345193
    ("ADP", "a"),  # 1851693
    ("ADV", "A"),  # 1651200
    ("PRON", "P"),  # 1525969
    ("ADJ", "J"),  # 1427357
    ("PART", "p"),  # 1147072
    ("CCONJ", "C"),  # 1101499
    ("DET", "D"),  # 873070
    ("PROPN", "O"),  # 684675
    ("SCONJ", "S"),  # 484188
    ("X", "X"),  # 175188
    ("NUM", "n"),  # 96248
    ("PUNCT", "t"),  # 88265
    ("INTJ", "I"),  # 61924
    ("SYM", "s"),  # 415
    ("AUX", "x"),  # 275
]

COMPRESS_UPOS_MAPPING = dict(_UPOS_MAPPING)
DECOMPRESS_UPOS_MAPPING = {v: k for k, v in _UPOS_MAPPING}

_FEATURES_MAPPING = [
    ("Number", "N"),  # 11271039
    ("Case", "C"),  # 10571690
    ("Gender", "G"),  # 8542912
    ("Animacy", "A"),  # 5989920
    ("Aspect", "a"),  # 3525739
    ("VerbForm", "V"),  # 3522972
    ("PronType", "P"),  # 2919605
    ("Mood", "M"),  # 2853237
    ("Tense", "T"),  # 2790165
    ("Person", "p"),  # 2338011
    ("Degree", "D"),  # 932900
    ("NameType", "t"),  # 549831
    ("Polarity", "O"),  # 435068
    ("Poss", "o"),  # 277106
    ("Reflex", "R"),  # 200099
    ("Uninflect", "U"),  # 182471
    ("Voice", "v"),  # 180374
    ("Foreign", "F"),  # 174835
    ("NumType", "n"),  # 168614
    ("PunctType", "u"),  # 76819
    ("Abbr", "B"),  # 59132
    ("Variant", "r"),  # 22024
    ("Hyph", "H"),  # 13212
    ("Animacy[gram]", "g"),  # 11597
    ("PartType", "Y"),  # 5582
    ("Orth", "h"),  # 3516
]

COMPRESS_FEATURES_MAPPING = dict(_FEATURES_MAPPING)
DECOMPRESS_FEATURES_MAPPING = {v: k for k, v in _FEATURES_MAPPING}

COMPRESS_FEATURE_VALUES_MAPPING = {
    "Animacy": {"Inan": "0", "Anim": "1"},
    "Case": {"Nom": "0", "Acc": "1", "Gen": "2", "Ins": "3", "Loc": "4", "Dat": "5", "Voc": "6"},
    "Gender": {"Masc": "0", "Fem": "1", "Neut": "2"},
    "Number": {"Sing": "0", "Plur": "1", "Ptan": "2"},
    "PronType": {"Prs": "0", "Dem": "1", "Rel": "2", "Ind": "3", "Tot": "4", "Int": "5", "Neg": "6", "Emp": "7"},
    "Degree": {"Pos": "0", "Cmp": "1", "Sup": "2", "Abs": "3"},
    "NumType": {"Card": "0", "Ord": "1"},
    "Aspect": {"Imp": "0", "Perf": "1"},
    "Mood": {"Ind": "0", "Imp": "1", "Cnd": "2"},
    "Tense": {"Past": "0", "Pres": "1", "Fut": "2"},
    "VerbForm": {"Fin": "0", "Inf": "1", "Part": "2", "Conv": "3"},
    "Voice": {"Pass": "0", "Act": "1"},
    "Person": {"3": "0", "1": "1", "2": "2", "0": "3"},
    "Polarity": {"Neg": "0"},
    "NameType": {"Giv": "0", "Sur": "1", "Pat": "2"},
    "Poss": {"Yes": "0"},
    "Reflex": {"Yes": "0"},
    "Variant": {"Uncontr": "0", "Short": "1"},
    "Foreign": {"Yes": "0"},
    "PunctType": {"Hyph": "0", "Dash": "1", "Ndash": "2", "Quot": "3"},
    "Hyph": {"Yes": "0"},
    "Uninflect": {"Yes": "0"},
    "Animacy[gram]": {"Anim": "0", "Inan": "1"},
    "PartType": {"Conseq": "0"},
    "Abbr": {"Yes": "0"},
    "Orth": {"Khark": "0"},
}

DECOMPRESS_FEATURE_VALUES_MAPPING = {
    k: {feat_val: feat_key for feat_key, feat_val in v.items()} for k, v in COMPRESS_FEATURE_VALUES_MAPPING.items()
}


def compress_features(feats):
    res = ""
    for pair in feats.split("|"):
        if not pair:
            continue
        cat, val = pair.split("=")

        try:
            c_cat = COMPRESS_FEATURES_MAPPING[cat]
        except KeyError:
            logger.warning(f"Cannot find the feature '{cat}' in the mapping, skipping it for now")
            continue

        try:
            c_val = COMPRESS_FEATURE_VALUES_MAPPING[cat][val]
        except KeyError:
            logger.warning(f"Cannot find the value '{val}' for the feature '{cat}' in the mapping, skipping it for now")
            continue

        res += c_cat + c_val

    return res


def grouper(iterable, n, fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def decompress_features(compressed):
    res = ""

    compressed = compressed.strip()
    if len(compressed.strip()) % 2 == 1:
        logger.warning(f"Length of the compressed features seems odd!")
        return res

    for c_cat, c_val in grouper(compressed, 2):
        try:
            cat = DECOMPRESS_FEATURES_MAPPING[c_cat]
        except KeyError:
            logger.warning(f"Cannot find the feature '{c_cat}' in the mapping, skipping it for now")
            continue

        try:
            val = DECOMPRESS_FEATURE_VALUES_MAPPING[cat][c_val]
        except KeyError:
            logger.warning(f"Cannot find the value '{c_val}' for the feature '{cat}' in the mapping, skipping it for now")
            continue

        # Let's stick to concatenation insted of format for the sake of speed
        res += cat + "=" + val + "|"

    return res.strip("|")



def unpack_values(param_name: str, s: str) -> List[List[Union[str, OrderedDict]]]:
    def _unpack_value(v: str) -> Union[str, OrderedDict]:
        if param_name == "ud_postags":
            try:
                return DECOMPRESS_UPOS_MAPPING[v]
            except KeyError:
                logger.warning(
                    f"Cannot find the upos '{v}' in the mapping, skipping it for now"
                )
                return "UNK"

        elif param_name == "ud_features":
            res = []

            for c_cat, c_val in grouper(v, 2):
                try:
                    cat = DECOMPRESS_FEATURES_MAPPING[c_cat]
                except KeyError:
                    logger.warning(
                        f"Cannot find the feature '{c_cat}' in the mapping, skipping it for now"
                    )
                    cat = "UNK"

                try:
                    val = DECOMPRESS_FEATURE_VALUES_MAPPING[cat][c_val]
                except KeyError:
                    logger.warning(
                        f"Cannot find the value '{c_val}' for the feature '{cat}' in the mapping, skipping it for now"
                    )
                    
                    val = "UNK"

                res.append((cat, val))
            return OrderedDict(res)
        else:
            return v

    if param_name == "ud_postags":
        return [[_unpack_value(w) for w in l] for l in s.split("\n")]
    else:
        return [[_unpack_value(w) for w in l.split(" ")] for l in s.split("\n")]


def decompress(tokens: str=None, ud_lemmas: str=None, ud_features: str=None, ud_postags: str=None) -> List[OrderedDict]:
    params = locals()

    assert any(
        map(lambda x: x is not None, params.values())
    ), "at least one param should be not None"

    zipped: dict = {}

    for param_name, param_value in params.items():
        if param_value is not None:
#             if param_name == "tokens":
#                 # TODO: validate if this workaround can be properly fixed
#                 param_value = param_value.strip()
            zipped[param_name] = unpack_values(param_name, param_value)
    

    sentences_length: set = set(map(len, zipped.values()))
    assert len(sentences_length) == 1, f"Text contains different number of sentences: {sentences_length}"

    res: list = []
    param_names: list[str] = list(zipped.keys())
    param_values: list[str] = list(zipped.values())

    for sent in zip(*param_values): 
        word_length:set = set(map(len, sent))

        assert len(sentences_length) == 1, f"Text contains different number of words in sentence: {sent}"

        res.append(
            [OrderedDict(zip(param_names, word_info)) for word_info in zip(*sent)]
        )


    return res
