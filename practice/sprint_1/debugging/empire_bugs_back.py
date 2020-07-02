from json import loads


request_payload = """\
{ 
"title": "Звездные войны 1: Империя приносит баги",
"description": "Эпичная сага по поиску багов в старом легаси проекте Империи",
"tags": [
    2, "семейное кино", "космос", 1.0, "сага", "эпик", "добро против зла", true, "челмедведосвин", "debug", "ipdb", 
    "PyCharm", "боевик", "боевик", "эникей", "дарт багус", 5, 6,4, "блокбастер", "кино 2020", 7, 3, 9, 12, 
    "каникулы в космосе", "коварство"
    ],
"version": 17
}
"""


def unique_tags(payload: dict) -> list:
    """Extracts unique tags from payload"""
    tags = payload.get('tags', [])
    unique = list(set(tags))

    int_inherited = filter(
        lambda tag: type(tag) != type(unique[unique.index(tag)]),
        tags
    )

    unique.extend(int_inherited)
    return unique


converted = loads(request_payload)
result = unique_tags(converted)
print(result)
