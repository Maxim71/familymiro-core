def _clean_cell_text(raw: str) -> str:
    """Убирает китайские иероглифы и лишнюю пунктуацию из двуязычных чертежей."""
    txt = re.sub(r'[\u4e00-\u9fff，、（）：；。、]+', ' ', raw or "")
    return re.sub(r'\s+', ' ', txt).strip(" ,;")
