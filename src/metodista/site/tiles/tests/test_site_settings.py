# -*- coding: utf-8 -*-
import unittest

from metodista.site.tiles.testing import INTEGRATION_TESTING


class SiteSettingsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_title(self):
        self.assertTrue(self.portal.title.startswith('Produto de tiles'),
                        'Title not applied')

    def test_email_configs(self):
        self.assertTrue(self.portal.email_from_address,
                        'E-mail address not set')
        self.assertTrue(self.portal.email_from_name,
                        'E-mail name not set')

    def test_language_settings(self):
        languages = self.portal['portal_languages']
        self.assertEqual(languages.use_combined_language_codes, 1,
                         'Combined language code not supported')

        self.assertEqual(languages.getDefaultLanguage(), 'pt-br',
                         'Language not set')
