# -*- coding: utf-8 -*-
import re


class EngineeringDataExtractor:
    """
    Инженерный анализатор чертежей: извлекает строительные оси, отметки высот,
    размеры пирогов (h, w), заглубление сетей, датчики автоматики и объёмы.
    """

    # Строительные оси: "Оси 1-8", "Ось А-Д", "в осях 2-4/Б-В"
    AXES_RE = re.compile(
        r'(?:в\s+)?ос[ьиях]{1,3}\s+([0-9А-ЯЁA-Z]{1,4}(?:\s*[-–/]\s*[0-9А-ЯЁA-Z]{1,4})+)',
        re.IGNORECASE
    )

    # Высоты, ширина, толщина пирогов, диаметры и отметки: h=150, w=200, Ø110, отм. -1.250
    GEOMETRY_RE = re.compile(
        r'(?:\b[hwLbH]\s*=\s*\d+(?:[\.,]\d+)?(?:\s*мм|\s*м)?|'
        r'отм\.?\s*[±+-]?\d+[\.,]\d{2,3}|'
        r'[ØДуDN]\s*\d+(?:х\d+(?:[\.,]\d+)?)?|'
        r'глубин[аеу]\s+заложени[яю]\s*[-–]?\s*\d+(?:[\.,]\d+)?\s*м?)',
        re.IGNORECASE
    )

    # Датчики автоматики, КИПиА и инженерные сети
    NETWORK_SENSOR_RE = re.compile(
        r'(?:датчик[а-яё\s\-]{0,35}|'
        r'сигнализатор[а-яё\s\-]{0,30}|'
        r'клапан[а-яё\s\-]{0,30}|'
        r'контроллер[а-яё\s\-]{0,25}|'
        r'кабел[ья][а-яё0-9\s\-хx×\.]{2,35}|'
        r'труб[аы][а-яё0-9\s\-Ø\.]{2,35}|'
        r'воздуховод[а-яё0-9\s\-хx×\.]{2,35})',
        re.IGNORECASE
    )

    # Объёмы и количества: 120.5 м3, 45 шт, 12.4 т, 300 п.м.
    VOLUME_QTY_RE = re.compile(
        r'(\d+(?:[\.,]\d+)?)\s*(м3|м³|м2|м²|п\.м\.|шт\.?|т|кг|компл\.?)',
        re.IGNORECASE
    )

    @classmethod
    def analyze_text(cls, text: str) -> dict:
        if not text:
            return {
                "axes_clean": "",
                "geometry_summary": "",
                "networks_and_sensors": [],
                "volumes_summary": [],
            }

        # 1. Очистка и сбор строительных осей
        axes_found = list(dict.fromkeys(
            m.group(1).strip() for m in cls.AXES_RE.finditer(text)
        ))

        # 2. Сбор пирогов высот (h=, w=), диаметров и отметок заглубления
        geom_found = list(dict.fromkeys(
            re.sub(r'\s+', ' ', m.group(0).strip()) for m in cls.GEOMETRY_RE.finditer(text)
        ))

        # 3. Инженерные сети и датчики автоматики
        net_found = list(dict.fromkeys(
            re.sub(r'\s+', ' ', m.group(0).strip()) for m in cls.NETWORK_SENSOR_RE.finditer(text)
        ))

        # 4. Количества и объёмы
        vol_found = list(dict.fromkeys(
            f"{m.group(1).replace(',', '.')} {m.group(2)}" for m in cls.VOLUME_QTY_RE.finditer(text)
        ))

        return {
            "axes_clean": ", ".join(axes_found[:6]),
            "geometry_summary": "; ".join(geom_found[:8]),
            "networks_and_sensors": net_found[:10],
            "volumes_summary": vol_found[:10],
        }
# -*- coding: utf-8 -*-
import re


class EngineeringDataExtractor:
    """
    Многоуровневый инженерный анализатор: извлекает Корпус, Секцию, Этаж (1-25+),
    широкие диапазоны осей, технику (башенные краны) и привязывает их к НАИМЕНОВАНИЮ.
    """

    # Корпуса и секции: "Корпус 2", "Корп. 1А", "Секция 3", "Блок Б"
    CORPUS_RE = re.compile(
        r'(?:корпус|корп\.?|секция|секц\.?|блок)\s*[№]?\s*([0-9А-ЯЁA-Z]{1,5})',
        re.IGNORECASE
    )

    # Этажи и ярусы: "1-25 этаж", "этаж 14", "на отм. +45.600", "-1 этаж"
    FLOOR_RE = re.compile(
        r'(?:[+-]?\d{1,2}(?:\s*[-–]\s*\d{1,2})?\s*этаж[а-яё]*|этаж[а-яё]*\s*[+-]?\d{1,2}(?:\s*[-–]\s*\d{1,2})?)',
        re.IGNORECASE
    )

    # Расширенные оси (поддержка двузначных чисел и букв с индексами): "Оси 1-36", "Ось 12/1-24/А-Я"
    AXES_RE = re.compile(
        r'(?:в\s+)?ос[ьиях]{1,3}\s+([0-9А-ЯЁA-Z\/\.]{1,8}(?:\s*[-–,;\/]\s*[0-9А-ЯЁA-Z\/\.]{1,8})+)',
        re.IGNORECASE
    )

    # Геометрия, пироги и отметки
    GEOMETRY_RE = re.compile(
        r'(?:\b[hwLbH]\s*=\s*\d+(?:[\.,]\d+)?(?:\s*мм|\s*м)?|'
        r'отм\.?\s*[±+-]?\d+[\.,]\d{2,3}|'
        r'[ØДуDN]\s*\d+(?:х\d+(?:[\.,]\d+)?)?)',
        re.IGNORECASE
    )

    # Объёмы и количества
    VOLUME_QTY_RE = re.compile(
        r'(\d+(?:[\.,]\d+)?)\s*(м3|м³|м2|м²|п\.м\.|шт\.?|т|кг|компл\.?)',
        re.IGNORECASE
    )

    # Конструкции, сети и грузоподъёмная техника (башенные краны)
    DOMAIN_KEYWORDS_RE = re.compile(
        r'(?:башенн[а-яё]*\s+кран[а-яё0-9\s\-№]*|кран\s*БК[-–]?\d+|'
        r'кладк[аи]|перегородк[аи]|штукатурк[аи]|стяжк[аи]|фасад|'
        r'датчик|клапан|контроллер|кабел|труб|воздуховод|'
        r'плит[аы]|фундамент|пирог|бетон|арматур|щит|насос)',
        re.IGNORECASE
    )

    @classmethod
    def _extract_clean_name(cls, line: str) -> str:
        cleaned = cls.GEOMETRY_RE.sub('', line)
        cleaned = cls.VOLUME_QTY_RE.sub('', cleaned)
        cleaned = cls.AXES_RE.sub('', cleaned)
        cleaned = cls.FLOOR_RE.sub('', cleaned)
        cleaned = re.sub(r'^[\s\-\.,:;()\/]+|[\s\-\.,:;()\/]+$', '', cleaned)
        return re.sub(r'\s{2,}', ' ', cleaned).strip()

    @classmethod
    def analyze_text(cls, text: str) -> dict:
        if not text:
            return {"structured_items": [], "location_summary": ""}

        structured_items = []
        all_corpuses, all_floors, all_axes = [], [], []

        for raw_line in text.split('\n'):
            line = raw_line.strip()
            if len(line) < 5:
                continue

            corpuses = [m.group(0).strip() for m in cls.CORPUS_RE.finditer(line)]
            floors = [m.group(0).strip() for m in cls.FLOOR_RE.finditer(line)]
            axes = [m.group(1).strip() for m in cls.AXES_RE.finditer(line)]
            geom = [re.sub(r'\s+', ' ', m.group(0).strip()) for m in cls.GEOMETRY_RE.finditer(line)]
            vols = [f"{m.group(1).replace(',', '.')} {m.group(2)}" for m in cls.VOLUME_QTY_RE.finditer(line)]
            has_domain = bool(cls.DOMAIN_KEYWORDS_RE.search(line))

            all_corpuses.extend(corpuses)
            all_floors.extend(floors)
            all_axes.extend(axes)

            if has_domain or geom or vols or floors:
                name = cls._extract_clean_name(line)
                if len(name) >= 4:
                    structured_items.append({
                        "name": name[:120],
                        "corpus": ", ".join(dict.fromkeys(corpuses)),
                        "floor": ", ".join(dict.fromkeys(floors)),
                        "axes": ", ".join(dict.fromkeys(axes)),
                        "geometry": "; ".join(dict.fromkeys(geom)),
                        "volume": ", ".join(dict.fromkeys(vols)),
                    })

        loc_parts = []
        if all_corpuses:
            loc_parts.append(", ".join(dict.fromkeys(all_corpuses)))
        if all_floors:
            loc_parts.append(", ".join(dict.fromkeys(all_floors)))
        if all_axes:
            loc_parts.append(f"Оси: {', '.join(dict.fromkeys(all_axes))}")

        return {
            "structured_items": structured_items[:30],
            "location_summary": " | ".join(loc_parts)[:100],
        }
