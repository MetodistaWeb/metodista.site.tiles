# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from metodista.site.tiles.testing import INTEGRATION_TESTING
from metodista.site.tiles.testing import generate_jpeg
from plone import api
from metodista.site.tiles.tiles.carrosselautomatico import CarrosselAutomaticoTile
from metodista.site.tiles.tiles.carrosselautomatico import ICarrosselAutomaticoTile


import unittest

EMPTY = [dict(
    i='portal_type',
    o='plone.app.querystring.operation.selection.is',
    v='Foo',
)]


class CarrosselAutomaticoTileTestCase(TestTileMixin, unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        super(CarrosselAutomaticoTileTestCase, self).setUp()
        self.tile = CarrosselAutomaticoTile(self.cover, self.request)
        self.tile.__name__ = u'carrosselautomatico'
        self.tile.id = u'test'

    def _update_tile_data(self):
        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format(str(self.tile.__name__), str(self.tile.id)))

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = ICarrosselAutomaticoTile
        self.klass = CarrosselAutomaticoTile
        super(CarrosselAutomaticoTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_droppable)
        self.assertTrue(self.tile.is_editable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Collection'])

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_crud(self):
        # now we add a couple of objects to the list
        obj1 = self.portal['my-news-folder']['my-collection']
        obj2 = self.portal['my-news-folder']['my-image']

        # Adicionamos a colecao de imagens
        self.tile.populate_with_object(obj1)
        self._update_tile_data()

        # Verificamos que ha um item existente
        self.assertEqual(len(self.tile.results()), 1)

        # Verificamos que a colecao nao e listada
        self.assertNotIn(obj1, self.tile.results())

        # Verificamos a imagem e listada
        self.assertIn(obj2, self.tile.results())

    def test_populate_tile_with_invalid_object(self):
        obj = self.portal['my-news-folder']['my-image']
        self.tile.populate_with_object(obj)
        self.assertTrue(self.tile.is_empty())

    def test_render_empty_collection(self):
        obj = self.portal['my-news-folder']['my-collection']
        obj.setQuery(EMPTY)
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        # Testa se o tile renderiza mesmos em itens
        self.assertIn("galleria slide cover-carousel-tile tile-content", rendered)

    def test_thumbnail_original_image(self):
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['image']['imgsize'] = '_original'
        self.tile.set_tile_configuration(tile_conf)
        obj = self.portal['my-news-folder']['my-image']
        self.assertTrue(self.tile.thumbnail(obj))
        self.assertIsInstance(self.tile(), unicode)

    def test_number_of_items(self):
        obj = self.portal['my-news-folder']['my-collection']
        self.tile.populate_with_object(obj)

        with api.env.adopt_roles(roles=['Manager']):

            api.content.create(
                type='Image',
                title='my-image-2',
                container=self.portal['my-news-folder']
            ).setImage(generate_jpeg(50, 50))

            api.content.create(
                type='Image',
                title='my-image-3',
                container=self.portal['my-news-folder']
            ).setImage(generate_jpeg(50, 50))

        # Collection has three images and shows them all.
        self.assertEqual(len(self.tile.results()), 3)

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['number_to_show']['size'] = 2
        self.tile.set_tile_configuration(tile_conf)

        # Collection has three images and shows the first two items.
        items = self.tile.results()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].getId(), 'my-image')
        self.assertEqual(items[1].getId(), 'my-image-2')
