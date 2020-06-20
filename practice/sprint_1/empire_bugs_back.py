from json import loads
from typing import List


request_payload = """\
{ 
"title": "Звездные войны 1: Империя приносит баги",
"description": "Эпичная сага по поиску багов в старом легаси проекте Империи",
"tags": [2, "семейное кино", "космос", 1.0, "сага", "эпик", "добро против зла", true, "челмедведосвин", "debug", "ipdb", "PyCharm", "боевик", "боевик", "эникей", "дарт багус", 5, 6,4, "блокбастер", "кино 2020", 7, 3, 9, 12, "каникулы в космосе", "коварство"],
"version": 17
}
"""


def unique_tags(payload: dict) -> List[str]:
    result = []
    tags = payload.get('tags', [])

    for tag in tags:
        if tag not in result or type(result[result.index(tag)]) != type(tag):
            result.append(tag)

    return result


converted = loads(request_payload)
result = unique_tags(converted)
