"""
Kuralix NLP Extractor v7 — complete, all fields, all languages.
"""

import re
from rapidfuzz import fuzz

NAME_KW = ["naam", "nam", "name", "नाम", "नाव", "பெயர்", "పేరు"]
NAME_TITLES = ["mr", "mrs", "shri", "smt", "dr", "kumari",
               "श्री", "श्रीमती", "डॉ", "श्रीमान", "திரு", "திருமதி"]

AGE_KW = ["umar", "umr", "age", "saal", "sal", "years", "year", "yrs",
          "वय", "वयस", "வயது", "వయస్సు", "వయసు", "उम्र",
          "साल", "वर्ष", "बरस"]

VILLAGE_KW = ["gaon", "gram", "village", "गाँव", "गांव", "गाव",
              "கிராமம்", "గ్రామం", "నగర్", "नगर", "शहर", "town", "city",
              "rehta", "rehti", "rehte", "rahta", "rahti",
              "live in", "from", "residing"]

SYMPTOM_KW = ["bukhar", "khansi", "dard", "sardi", "khujli", "ulti", "chakkar",
              "बुखार", "खांसी", "दर्द", "सर्दी", "खुजली", "उल्टी", "चक्कर",
              "ताप", "खोकला", "अंगदुखी", "डोकेदुखी", "उलटी",
              "காய்ச்சல்", "இருமல்", "வலி", "சளி", "தலைவலி",
              "జ్వరం", "దగ్గు", "నొప్పి", "జలుబు", "తలనొప్పి",
              "fever", "cough", "pain", "cold", "headache", "vomiting"]

GENDER_KW_F = ["ladki", "female", "aurat", "mahila", "स्त्री", "महिला",
               "औरत", "लड़की", "बीवी", "पत्नी", "wife",
               "मुलगी", "बाई",
               "பெண்", "pen",
               "మహిళ", "స్త్రీ", "ఆడ", "ఆడది",
               "woman", "girl", "lady"]

GENDER_KW_M = ["ladka", "male", "mard", "purush", "पुरुष", "आदमी",
               "लड़का", "पति", "pati", "husband",
               "मुलगा", "नवरा",
               "ஆண்", "aan", "பையன்",
               "పురుషుడు", "మగ", "మగవాడు", "అబ్బాయి",
               "man", "boy", "guy"]

PHONE_KW = ["phone", "mobile", "number", "फोन", "मोबाइल", "नंबर", "संख्या",
            "தொலைபேசி", "எண்", "ఫోన్", "నంబర్"]

SYMPTOM_MAP = {
    "bukhar": "Fever", "बुखार": "Fever", "ज्वर": "Fever", "ताप": "Fever",
    "காய்ச்சல்": "Fever", "జ్వరం": "Fever", "fever": "Fever",
    "khansi": "Cough", "खांसी": "Cough", "खाँसी": "Cough", "खोकला": "Cough",
    "இருமல்": "Cough", "దగ్గు": "Cough", "cough": "Cough",
    "dard": "Pain", "दर्द": "Pain", "अंगदुखी": "Pain",
    "வலி": "Pain", "నొప్పి": "Pain", "pain": "Pain",
    "sardi": "Cold", "सर्दी": "Cold", "சளி": "Cold",
    "జలుబు": "Cold", "cold": "Cold",
    "chakkar": "Dizziness", "चक्कर": "Dizziness",
    "ulti": "Vomiting", "उल्टी": "Vomiting", "उलटी": "Vomiting",
    "vomiting": "Vomiting",
    "khujli": "Itching", "खुजली": "Itching",
    "sir dard": "Headache", "सिरदर्द": "Headache", "सिर दर्द": "Headache",
    "डोकेदुखी": "Headache", "headache": "Headache",
    "தலைவலி": "Headache", "తలనొప్పి": "Headache",
}

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5,
    "छह": 6, "छः": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    "ग्यारह": 11, "बारह": 12, "तेरह": 13, "चौदह": 14, "पंद्रह": 15,
    "सोलह": 16, "सत्रह": 17, "अठारह": 18, "उन्नीस": 19, "बीस": 20,
    "इक्कीस": 21, "बाईस": 22, "तेईस": 23, "चौबीस": 24, "पच्चीस": 25,
    "छब्बीस": 26, "सत्ताईस": 27, "अठ्ठाईस": 28, "उनतीस": 29, "तीस": 30,
    "इकतीस": 31, "बत्तीस": 32, "बतीस": 32, "तैंतीस": 33, "चौंतीस": 34,
    "पैंतीस": 35, "छत्तीस": 36, "सैंतीस": 37, "अड़तीस": 38,
    "उनतालीस": 39, "चालीस": 40, "इकतालीस": 41, "बयालीस": 42,
    "तैंतालीस": 43, "चवालीस": 44, "पैंतालीस": 45, "छयालीस": 46,
    "सैंतालीस": 47, "अड़तालीस": 48, "उनचास": 49, "पचास": 50,
    "इक्यावन": 51, "बावन": 52, "तिरेपन": 53, "चौवन": 54, "पचपन": 55,
    "छप्पन": 56, "सत्तावन": 57, "अठावन": 58, "उनसठ": 59, "साठ": 60,
    "इकसठ": 61, "बासठ": 62, "तिरेसठ": 63, "चौंसठ": 64, "पैंसठ": 65,
    "छियासठ": 66, "सड़सठ": 67, "अड़सठ": 68, "उनहत्तर": 69, "सत्तर": 70,
    "इकहत्तर": 71, "बहत्तर": 72, "तिहत्तर": 73, "चौहत्तर": 74,
    "पचहत्तर": 75, "छिहत्तर": 76, "सतहत्तर": 77, "अठहत्तर": 78,
    "उनासी": 79, "अस्सी": 80, "इक्यासी": 81, "बयासी": 82,
    "तिरासी": 83, "चौरासी": 84, "पचासी": 85, "छियासी": 86,
    "सत्तासी": 87, "अठासी": 88, "नवासी": 89, "नब्बे": 90,
    "इक्यानवे": 91, "बानवे": 92, "तिरानवे": 93, "चौरानवे": 94,
    "पंचानवे": 95, "छियानवे": 96, "सत्तानवे": 97, "अट्ठानवे": 98,
    "निन्यानवे": 99, "सौ": 100,
    "दोन": 2, "सहा": 6, "नऊ": 9, "दहा": 10,
    "अकरा": 11, "चौदा": 14, "पंधरा": 15,
    "सोळा": 16, "सतरा": 17, "अठरा": 18, "एकोणीस": 19, "वीस": 20,
    "एकवीस": 21, "बावीस": 22, "तेवीस": 23, "चोवीस": 24, "पंचवीस": 25,
    "सव्वीस": 26, "सत्तावीस": 27, "अठ्ठावीस": 28, "एकोणतीस": 29,
    "चाळीस": 40, "पन्नास": 50, "शंभर": 100,
    "ஒன்று": 1, "இரண்டு": 2, "மூன்று": 3, "நான்கு": 4, "ஐந்து": 5,
    "ஆறு": 6, "ஏழு": 7, "எட்டு": 8, "ஒன்பது": 9, "பத்து": 10,
    "இருபது": 20, "முப்பது": 30, "நாற்பது": 40, "ஐம்பது": 50,
    "அறுபது": 60, "எழுபது": 70, "எண்பது": 80, "தொண்ணூறு": 90,
    "நூறு": 100,
    "ఒకటి": 1, "రెండు": 2, "మూడు": 3, "నాలుగు": 4, "ఐదు": 5,
    "ఆరు": 6, "ఏడు": 7, "ఎనిమిది": 8, "తొమ్మిది": 9, "పది": 10,
    "ఇరవై": 20, "ముప్పై": 30, "నలభై": 40, "యాభై": 50,
    "అరవై": 60, "డెబ్బై": 70, "ఎనభై": 80, "తొంభై": 90,
    "వంద": 100,
}

SPOKEN_DIGITS = {
    "zero": "0", "oh": "0", "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8",
    "nine": "9",
    "शून्य": "0", "एक": "1", "दो": "2", "तीन": "3", "चार": "4",
    "पांच": "5", "पाँच": "5", "छह": "6", "सात": "7", "आठ": "8",
    "नौ": "9",
    "दोन": "2", "पाच": "5", "सहा": "6", "नऊ": "9",
}

BOUNDARY_WORDS = {
    "is", "am", "the", "and", "from", "my", "of", "a", "an", "called", "named",
    "है", "हूँ", "हूं", "हैं", "का", "की", "के", "को", "से", "में", "और",
    "मेरा", "मेरी", "हमारा", "हमारी",
    "hai", "hun", "hoon", "hain", "ka", "ki", "ke", "ko", "se", "mein",
    "mera", "meri",
    "आहे", "आहेत", "माझे", "माझी", "माझा", "आणि", "म्हणजे",
    "aahe", "aahet", "maza", "mazi", "majhe", "aani",
    "என்", "எனது", "இருக்கிறது", "இருக்கும்", "என்று", "என்பது",
    "ஆகும்", "மற்றும்",
    "en", "enadu", "irukku", "irukkum", "endru",
    "నా", "నాది", "ఉంది", "ఉన్నది", "అని", "అనే", "మరియు",
    "na", "nadi", "undi", "unnadi", "ani", "ane", "mariyu",
}

BOUNDARY_LOWER = {w.lower() for w in BOUNDARY_WORDS}

ALL_FIELD_KW = (AGE_KW + VILLAGE_KW + SYMPTOM_KW +
                GENDER_KW_F + GENDER_KW_M + PHONE_KW)


def extract_fields(text: str) -> dict:
    if not text:
        return {}
    text_lower = text.lower()
    fields = {}

    name = _extract_name(text, text_lower)
    if name:
        conf = 0.9 if len(name.split()) >= 2 else 0.75
        fields["name"] = {"value": name, "confidence": conf}

    age = _extract_age(text, text_lower)
    if age:
        fields["age"] = {"value": age, "confidence": 0.9}

    village = _extract_village(text, text_lower)
    if village:
        fields["village"] = {"value": village, "confidence": 0.8}

    symptoms = _extract_symptoms(text_lower)
    if symptoms:
        conf = 0.9 if len(symptoms) >= 2 else 0.85
        fields["symptoms"] = {"value": ", ".join(symptoms), "confidence": conf}

    gender = _extract_gender(text_lower)
    if gender:
        fields["gender"] = {"value": gender, "confidence": 0.85}

    phone = _extract_phone(text)
    if phone:
        fields["phone"] = {"value": phone, "confidence": 0.95}

    return fields


def _strip_matras(word: str) -> str:
    out = []
    for c in word:
        code = ord(c)
        if 0x093E <= code <= 0x094F: continue
        if 0x0900 <= code <= 0x0903: continue
        if 0x0BBE <= code <= 0x0BCD: continue
        if 0x0C3E <= code <= 0x0C4D: continue
        out.append(c)
    return "".join(out)


def _find_keyword(text_lower: str, keywords: list, start: int = 0):
    for kw in sorted(keywords, key=len, reverse=True):
        idx = text_lower.find(kw.lower(), start)
        if idx != -1:
            return idx, kw
    words_with_pos = []
    pos = 0
    for w in text_lower.split():
        p = text_lower.find(w, pos)
        words_with_pos.append((w, p))
        pos = p + len(w)
    for w, p in words_with_pos:
        if p < start:
            continue
        w_strip = _strip_matras(w)
        for kw in keywords:
            if fuzz.ratio(w, kw.lower()) >= 85:
                return p, kw
            kw_strip = _strip_matras(kw.lower())
            if w_strip and kw_strip and fuzz.ratio(w_strip, kw_strip) >= 88:
                return p, kw
    return -1, None


def _clean_fillers(chunk: str) -> str:
    chunk = chunk.strip(" ,.:;-=:")
    for _ in range(3):
        lowered = chunk.lower()
        stripped = False
        for filler in ["is", "hai", "है", "mera", "meri", "का", "की",
                       "नाम", "name", "aahe", "आहे", "என்", "en", "na", "నా"]:
            if lowered.startswith(filler + " "):
                chunk = chunk[len(filler):].strip(" ,.:;-=")
                stripped = True
                break
        if not stripped:
            break
    return chunk


def _is_boundary(word: str) -> bool:
    w = word.strip(".,;:!?").lower()
    if not w:
        return True
    if w in BOUNDARY_LOWER:
        return True
    for stop in BOUNDARY_LOWER:
        if len(stop) >= 3 and fuzz.ratio(w, stop) >= 90:
            return True
    return False


def _extract_name(text: str, text_lower: str) -> str:
    idx, kw = _find_keyword(text_lower, NAME_KW)
    if idx == -1:
        return ""
    start = idx + len(kw)
    next_boundary = len(text)
    for other_kw in ALL_FIELD_KW:
        p = text_lower.find(other_kw.lower(), start)
        if p != -1 and p < next_boundary:
            if p == 0 or text[p - 1] in " \t,.;:!?।":
                next_boundary = p
    chunk = _clean_fillers(text[start:next_boundary])
    words = chunk.split()
    name_words = []
    for w in words[:4]:
        w_clean = w.strip(".,;:!?").lower()
        if not w_clean:
            continue
        if _is_boundary(w):
            break
        if w_clean in {t.lower() for t in NAME_TITLES}:
            continue
        if any(c.isdigit() for c in w_clean):
            break
        if len(w_clean) < 2:
            break
        name_words.append(w.strip(".,;:!?"))
    return " ".join(name_words).strip(" ,.")


def _num_from_word(word: str):
    w = word.strip(".,;:!?")
    if not w:
        return None
    if w in NUMBER_WORDS:
        return NUMBER_WORDS[w]
    w_strip = _strip_matras(w)
    for key, val in NUMBER_WORDS.items():
        if _strip_matras(key) == w_strip and w_strip:
            return val
    for key, val in NUMBER_WORDS.items():
        if not key.isascii():
            if fuzz.ratio(w, key) >= 80:
                return val
            key_strip = _strip_matras(key)
            if w_strip and key_strip and fuzz.ratio(w_strip, key_strip) >= 85:
                return val
    for key, val in NUMBER_WORDS.items():
        if key.isascii() and fuzz.ratio(w.lower(), key) >= 85:
            return val
    return None


def _parse_number(text: str):
    tokens = re.findall(r"[\w\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F]+", text)
    for t in tokens:
        v = _num_from_word(t)
        if v and 1 <= v <= 120:
            return v
    for i in range(len(tokens) - 1):
        a, b = tokens[i].lower(), tokens[i + 1].lower()
        if a in NUMBER_WORDS and b in NUMBER_WORDS:
            av, bv = NUMBER_WORDS[a], NUMBER_WORDS[b]
            if av >= 20 and av % 10 == 0 and 1 <= bv <= 9:
                return av + bv
    return None


def _extract_age(text: str, text_lower: str) -> str:
    text_no_phone = re.sub(r"\b[6-9]\d{9}\b", " ", text)
    text_no_phone_lower = text_no_phone.lower()

    for kw in AGE_KW:
        kw_re = re.escape(kw)
        m = re.search(rf"{kw_re}\s*[:\-]?\s*(\d{{1,3}})", text_no_phone, re.I)
        if m:
            v = int(m.group(1))
            if 1 <= v <= 120:
                return str(v)
        m = re.search(rf"(\d{{1,3}})\s*[:\-]?\s*{kw_re}", text_no_phone, re.I)
        if m:
            v = int(m.group(1))
            if 1 <= v <= 120:
                return str(v)

    if any(kw in text_no_phone_lower for kw in AGE_KW):
        m = re.search(r"\b(\d)\s+(\d)\b", text_no_phone)
        if m:
            combined = int(m.group(1) + m.group(2))
            if 10 <= combined <= 99:
                return str(combined)

    for kw in AGE_KW:
        idx = text_no_phone_lower.find(kw.lower())
        if idx != -1:
            window = text_no_phone[max(0, idx - 30): idx + 50]
            v = _parse_number(window)
            if v:
                return str(v)

    if any(kw in text_no_phone_lower for kw in AGE_KW):
        v = _parse_number(text_no_phone)
        if v:
            return str(v)
        for n in re.findall(r"\b(\d{1,3})\b", text_no_phone):
            iv = int(n)
            if 1 <= iv <= 120:
                return n

    return ""


def _extract_village(text: str, text_lower: str) -> str:
    idx, kw = _find_keyword(text_lower, VILLAGE_KW)
    if idx != -1:
        start = idx + len(kw)
        next_boundary = len(text)
        for other_kw in (AGE_KW + SYMPTOM_KW + GENDER_KW_F + GENDER_KW_M + PHONE_KW):
            p = text_lower.find(other_kw.lower(), start)
            if p != -1 and p < next_boundary:
                if p == 0 or text[p - 1] in " \t,.;:!?।":
                    next_boundary = p
        chunk = _clean_fillers(text[start:next_boundary])
        words = chunk.split()
        v_words = []
        for w in words[:4]:
            w_clean = w.strip(".,;:!?").lower()
            if not w_clean:
                continue
            if _is_boundary(w):
                break
            if any(c.isdigit() for c in w_clean):
                break
            if len(w_clean) < 2:
                break
            v_words.append(w.strip(".,;:!?"))
        if v_words:
            return " ".join(v_words).strip(" ,.")

    for kw in sorted(VILLAGE_KW, key=len, reverse=True):
        idx = text_lower.find(kw.lower())
        if idx == -1:
            continue
        before = text[:idx].strip(" ,.:;-")
        words = before.split()
        v_words = []
        for w in reversed(words[-3:]):
            w_clean = w.strip(".,;:!?").lower()
            if _is_boundary(w):
                break
            if any(c.isdigit() for c in w_clean):
                break
            if len(w_clean) < 2:
                break
            v_words.insert(0, w.strip(".,;:!?"))
        if v_words:
            return " ".join(v_words).strip(" ,.")

    return ""


def _extract_symptoms(text_lower: str) -> list:
    found = []
    seen = set()
    for key, english in SYMPTOM_MAP.items():
        if english in seen:
            continue
        if key in text_lower:
            found.append(english)
            seen.add(english)
            continue
        key_strip = _strip_matras(key)
        for word in text_lower.split():
            w_strip = _strip_matras(word)
            if fuzz.ratio(key, word) > 82:
                found.append(english)
                seen.add(english)
                break
            if w_strip and key_strip and fuzz.ratio(w_strip, key_strip) >= 85:
                found.append(english)
                seen.add(english)
                break
    return found


def _extract_gender(text_lower: str) -> str:
    for kw in sorted(GENDER_KW_F, key=len, reverse=True):
        if kw.lower() in text_lower:
            return "Female"
    for kw in sorted(GENDER_KW_M, key=len, reverse=True):
        if kw.lower() in text_lower:
            return "Male"
    words = text_lower.split()
    for w in words:
        w_clean = w.strip(".,;:!?")
        if len(w_clean) < 3:
            continue
        for kw in GENDER_KW_F:
            if " " not in kw and fuzz.ratio(w_clean, kw.lower()) >= 85:
                return "Female"
        for kw in GENDER_KW_M:
            if " " not in kw and fuzz.ratio(w_clean, kw.lower()) >= 85:
                return "Male"
    return ""


def _extract_phone(text: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)\.]", "", text)
    cleaned = re.sub(r"^\+?91", "", cleaned)

    m = re.search(r"\b([6-9]\d{9})\b", cleaned)
    if m:
        return m.group(1)

    single_digits = re.findall(r"\b(\d)\b", text)
    if len(single_digits) >= 10:
        phone = "".join(single_digits[-10:])
        if phone[0] in "6789":
            return phone

    words = text.lower().split()
    digit_chars = []
    for w in words:
        w_clean = w.strip(".,;:!?")
        if w_clean in SPOKEN_DIGITS:
            digit_chars.append(SPOKEN_DIGITS[w_clean])
    if len(digit_chars) >= 10:
        phone = "".join(digit_chars[-10:])
        if phone[0] in "6789":
            return phone

    return ""