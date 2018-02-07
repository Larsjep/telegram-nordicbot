#!/usr/bin/python2
# -*- coding: utf-8 -*-
import unittest
import menu_bot


class TestMenuParsing(unittest.TestCase):
    def test_valid_menu(self):
        text = u"""
Torsdag:
        Varm ret
            Knippelsuppe
            Klaptorsk
            Luftfrikadeller
        Salater
            Båndsalat
        Pålæg
            Slæbesild
Der tages forbehold for ændringer i menuen, såfremt de rette råvarer ikke kan fremskaffes.
"""
        menu = menu_bot.find_menu_in_text(text)

        self.assertIn('torsdag', menu)
        self.assertEqual(8, len(menu['torsdag']))

    def test_allergies_to_emoji(self):

        test_vector = [
            ('foo (L) bar', u"foo 🥛 bar"),
            ('dsd (G)', u"dsd 🍞"),
            ('(N)xyz', u"🥜xyz"),
            ('djddj (G,L)xyz', u"djddj 🍞🥛xyz"),
        ]

        for test in test_vector:
            self.assertEqual(test[1], menu_bot.allergies_to_emoji([test[0]])[0])


if __name__ == "__main__":
    unittest.main()
