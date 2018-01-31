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


if __name__ == "__main__":
    unittest.main()
