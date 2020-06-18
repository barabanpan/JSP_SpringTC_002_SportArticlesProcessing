import spacy  # install spacy
from collections import Counter
from dateutil.parser import parse  # install python-dateutil

# en_core_web_sm is some spacy model thing
# download archive(!) manually from here:
# https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-2.2.5
EN_CORE_WEB_SM = 'en_core_web_sm-2.2.5/en_core_web_sm/en_core_web_sm-2.2.5'


def _is_date(string):
    """
    Return whether the string can be interpreted as a date.
    :param string: str, string to check for date

    Is used to weed out dates like "12 years ago".
    """
    try:
        parse(string, fuzzy=False)
        return True

    except ValueError:
        return False


def _group_ents(ents_list):
    """
    Return a dictionary with grouped entities from ents_list.

    Is used in case some token is repeated in text like this:
    "Full token one", "Token one", "Full token", so that those
    are considered to be one token.
    """
    ents_dict = {}
    ents_list.sort(key=lambda x: len(x[0]))  # longer tokens first

    while ents_list:
        ent = ents_list.pop()

        # Skip labels that we don't need
        # Geographical point messes some other labels up
        if ent[1] in ["CARDINAL", "ORDINAL", "LAW", "TIME"] \
           or (ent[1] == "DATE" and not _is_date(ent[0])):
            continue    # skip

        # Try to put item in some group
        found_place = False
        for key in ents_dict:
            if ent[0] in key:
                ents_dict[key].append(ent)
                found_place = True
                break

        # Otherwise create own group for this item
        if not found_place:
            ents_dict[ent[0]] = [ent]

    return ents_dict

def _to_pretty_dict(ents_list):
    """
    Transform a list of entities into dictionary.
    """
    ents_pretty_dict = {}
    length = Counter([e[1] for e in ents_list]).most_common(1)[0][1]
    while ents_list:
        ent = ents_list.pop()

        # Try to put item in some group
        found_place = False
        for label_key in ents_pretty_dict:
            if ent[1] in label_key:
                ents_pretty_dict[label_key].append(ent[0])
                found_place = True
                break

        # Otherwise create own group for this item
        if not found_place:
            ents_pretty_dict[ent[1]] = [ent[0]]

    # Fill missing spots to avoid errors
    for key, val in ents_pretty_dict.items():
        if len(val) < length:
            val = val + ["" for _ in range(length - len(val))]

    for label in ["PERSON", "GPE", "ORG", "LOC", "DATE"]:
        if label not in ents_pretty_dict:
            ents_pretty_dict[label] = ["" for _ in range(length)]

    return ents_pretty_dict


def get_tokens_and_labels(text):
    """
    Return a dictionary like:
    {"PERSON": ["Person1", "Person2", ..],
     "ORG": ["Org1", "Org2", ..],
     ..}
     with tokens and labels from article in text,
     and maximum length of lists of tokens.
    """
    global EN_CORE_WEB_SM
    try:
        nlp = spacy.load(EN_CORE_WEB_SM)
    except Exception:  # if not found, change path
        EN_CORE_WEB_SM = "../libs/" + EN_CORE_WEB_SM
        nlp = spacy.load(EN_CORE_WEB_SM)

    article = nlp(text)

    ents_list = [(x.text, x.label_) for x in article.ents]
    grouped_ents_dict = _group_ents(ents_list)

    new_ents = []
    # pick the most common label (sometimes it isn't the right one)
    for key, val_list in grouped_ents_dict.items():
        label = Counter([x[1] for x in val_list]).most_common(1)[0][0]
        # or first is better?
        new_ents.append((key, label))

    length = Counter([e[1] for e in new_ents]).most_common(1)[0][1]
    return length, _to_pretty_dict(new_ents)
