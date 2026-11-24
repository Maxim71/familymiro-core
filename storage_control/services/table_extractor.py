# -*- coding: utf-8 -*-
import re
import logging

logger = logging.getLogger(__name__)


def extract_tables_and_words(page) -> dict:
    """Восстанавливает ячейки таблиц спецификаций и снимает геометрию слов (x0, y0, x1, y1)."""
    table_rows = []
    try:
        for tab in page.find_tables():
            for row in tab.extract():
                cells = [re.sub(r'\s+', ' ', (c or '')).strip() for c in row]
                if any(cells):
                    table_rows.append(" | ".join(cells))
    except Exception as exc:
        logger.debug("Таблицы на листе не найдены: %s", exc)

    words = page.get_text("words")
    return {
        "table_rows": table_rows,
        "words_count": len(words),
    }
