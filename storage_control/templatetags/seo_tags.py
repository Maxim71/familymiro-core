# -*- coding: utf-8 -*-
import re
from django import template

register = template.Library()

_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def make_seo_slug(text: str) -> str:
    """Превращает 'Труба ПЭ 110 (защ.)' в чистый SEO-адрес 'truba-pe-110-zasch' без %D0%."""
    s = (text or "").lower().strip()
    out = "".join(_TRANSLIT.get(ch, ch) for ch in s)
    out = re.sub(r'[^a-z0-9]+', '-', out).strip('-')
    return out[:90] or "marka"


@register.filter(name="seo_slug")
def seo_slug_filter(value):
    return make_seo_slug(str(value or ""))
