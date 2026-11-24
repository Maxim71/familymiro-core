# -*- coding: utf-8 -*-
import re
from decimal import Decimal


class AutomationAndHydraulicsMacro:
    """
    Макрос считывания и расчёта для разделов АОВ, АСУД, ИТП, ВК и гидравлики:
    выделяет шкафы управления (ШУ/ЩА), датчики КИПиА, гидравлические узлы и считает объёмы.
    """

    # Шкафы управления и автоматики: ШУ-1, ЩА-ОВ1, ШАУ-ЦОД, ПЛК/PLC
    CABINET_RE = re.compile(
        r'\b((?:ШУ|ЩА|ША|ШАУ|ШР|ЩУ|ВРУ|ПЛК|PLC)[-\s]?[А-ЯЁA-Z0-9\.\-]{1,15})\b',
        re.IGNORECASE
    )

    # Датчики КИПиА (давление, температура, перепад, уровень, протечка, загазованность)
    SENSOR_RE = re.compile(
        r'(датчик[а-яё\s\-]{1,40}(?:давлени[яю]|температур[ы]|перепад[а]?|уровн[я]|протечк[и]|влажност[и]|поток[а]|СО|CH4)?|'
        r'термопреобразовател[ья][а-яё0-9\s\-]{1,30}|'
        r'манометр[а-яё0-9\s\-]{0,25}|'
        r'расходомер[а-яё0-9\s\-]{0,30})',
        re.IGNORECASE
    )

    # Гидравлические узлы и арматура (насосы, коллекторы, клапаны, гидрострелки, затворы)
    HYDRAULICS_RE = re.compile(
        r'(насос[а-яё0-9\s\-\/]{1,40}|'
        r'коллектор[а-яё0-9\s\-]{1,35}|'
        r'гидравлическ[а-яё]+\s+(?:разделител[ья]|стрелк[аи]|узел[а]?)|'
        r'клапан[а-яё0-9\s\-]{1,35}(?:регулирующ[а-яё]+|обратн[а-яё]+|балансировочн[а-яё]+|трехходов[а-яё]+)?|'
        r'электропривод[а-яё0-9\s\-]{1,30}|'
        r'теплообменник[а-яё0-9\s\-]{1,30})',
        re.IGNORECASE
    )

    # Количество в строке: "4 шт", "12 компл", "250 м"
    QTY_RE = re.compile(r'(\d+(?:[\.,]\d+)?)\s*(шт\.?|компл\.?|м|п\.м\.)', re.IGNORECASE)

    @classmethod
    def run_macro(cls, text: str) -> dict:
        """
        Выполняет пакетное считывание шкафов, датчиков и гидравлики со страницы чертежа.
        Возвращает структурированную сводку для БД и расчёта кабеля/сигналов.
        """
        if not text:
            return {"cabinets": [], "sensors": [], "hydraulics": [], "total_io_signals": 0}

        cabinets, sensors, hydraulics = {}, {}, {}
        total_signals = 0

        for raw_line in text.split('\n'):
            line = raw_line.strip()
            if len(line) < 4:
                continue

            qty_m = cls.QTY_RE.search(line)
            qty = Decimal(qty_m.group(1).replace(',', '.')) if qty_m else Decimal('1')

            # 1. Шкафы управления
            for m in cls.CABINET_RE.finditer(line):
                cab_code = m.group(1).upper()
                cabinets[cab_code] = cabinets.get(cab_code, Decimal('0')) + qty

            # 2. Датчики КИПиА (каждый датчик даёт минимум 1 входной сигнал AI/DI в шкаф)
            for m in cls.SENSOR_RE.finditer(line):
                s_name = re.sub(r'\s+', ' ', m.group(1).strip()).capitalize()
                sensors[s_name] = sensors.get(s_name, Decimal('0')) + qty
                total_signals += int(qty)

            # 3. Гидравлика и приводы (насосы и клапаны с приводом требуют сигналы управления DO/AO)
            for m in cls.HYDRAULICS_RE.finditer(line):
                h_name = re.sub(r'\s+', ' ', m.group(1).strip()).capitalize()
                hydraulics[h_name] = hydraulics.get(h_name, Decimal('0')) + qty
                if any(w in h_name.lower() for w in ('насос', 'привод', 'регулирующ', 'клапан')):
                    total_signals += int(qty)

        return {
            "cabinets": [{"code": k, "qty": float(v)} for k, v in cabinets.items()],
            "sensors": [{"name": k, "qty": float(v)} for k, v in sensors.items()],
            "hydraulics": [{"name": k, "qty": float(v)} for k, v in hydraulics.items()],
            "total_io_signals": total_signals,
        }
