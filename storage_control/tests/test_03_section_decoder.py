# -*- coding: utf-8 -*-
from django.test import TestCase
from storage_control.models import SectionDict
from storage_control.services.section_decoder import resolve_section_and_brigade


class Node03SectionDecoderTest(TestCase):
    """Отмашка №3: Проверка справочника разделов SectionDict, ссылок СП и привязки бригад."""

    def setUp(self):
        SectionDict.objects.create(
            code="24.0454-Р-ГП",
            section="Генеральный план и благоустройство",
            snip_ref="СП 42.13330",
            snip_url="https://cntd.ru",
        )

    def test_known_section_with_snip_url_and_brigade(self):
        """Шифр из справочника возвращает название раздела, СП, ссылку и нужную бригаду."""
        res = resolve_section_and_brigade("24.0454-Р-ГП")

        self.assertEqual(res["section"], "Генеральный план и благоустройство")
        self.assertEqual(res["snip_ref"], "СП 42.13330")
        self.assertTrue(res["snip_url"].startswith("https://"))
        self.assertIn("Бригада №1", res["brigade"])

    def test_unknown_code_fallback_without_hallucination(self):
        """Неизвестный шифр не выдумывает СП, но корректно назначает бригаду по маркеру."""
        res = resolve_section_and_brigade("09-КЖ-01")

        self.assertEqual(res["section"], "")
        self.assertEqual(res["snip_ref"], "")
        self.assertEqual(res["snip_url"], "")
        self.assertIn("Монолитчики", res["brigade"])
