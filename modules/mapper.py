"""
Kuralix Field Mapper
Maps extracted entities to form field IDs with confidence + review flags.
"""

FORM_SCHEMA = {
    "name":     {"label": "Full Name",    "type": "text",   "required": True},
    "age":      {"label": "Age",          "type": "number", "required": True},
    "gender":   {"label": "Gender",       "type": "select", "required": True,
                 "options": ["Male", "Female", "Other"]},
    "village":  {"label": "Village",      "type": "text",   "required": True},
    "phone":    {"label": "Phone Number", "type": "tel",    "required": False},
    "symptoms": {"label": "Symptoms",     "type": "text",   "required": True},
}

CONFIDENCE_THRESHOLD = 0.75


def map_to_form(extracted: dict) -> dict:
    form = {}
    low_conf = []
    confidences = []
    required_filled = 0
    required_total = sum(1 for f in FORM_SCHEMA.values() if f["required"])

    for field_id, schema in FORM_SCHEMA.items():
        if field_id in extracted:
            value = extracted[field_id]["value"]
            conf = extracted[field_id]["confidence"]
            needs_review = conf < CONFIDENCE_THRESHOLD
            if needs_review:
                low_conf.append(field_id)
            if schema["required"]:
                required_filled += 1
        else:
            value = ""
            conf = 0.0
            needs_review = schema["required"]
            if needs_review:
                low_conf.append(field_id)

        form[field_id] = {
            "label": schema["label"],
            "type": schema["type"],
            "value": value,
            "confidence": round(conf, 2),
            "needs_review": needs_review,
            "required": schema["required"],
            **({"options": schema["options"]} if "options" in schema else {}),
        }
        confidences.append(conf)

    overall = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    completion = round(required_filled / required_total, 2) if required_total else 0.0

    return {
        "form": form,
        "low_confidence_fields": low_conf,
        "overall_confidence": overall,
        "completion": completion,
    }