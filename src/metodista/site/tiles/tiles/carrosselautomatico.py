# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from plone.app.uuid.utils import uuidToObject
from plone.autoform import directives as form
from plone.memoize import view
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema import getFieldsInOrder

import random

# autoplay feature is enabled in view mode only
INIT_JS = """
            $(function() {{
                    Galleria.loadTheme('++resource++metodista.site.tiles/js/cover.carrossel.js');
                    Galleria.run('#galleria-{0}', {
                        height: 0.3531;
                    })
            }});
"""


class ICarrosselAutomaticoTile(IPersistentCoverTile):

    form.omitted('image')
    form.no_omit(IDefaultConfigureForm, 'image')
    image = NamedImage(
        title=_(u'Image'),
        required=False,
    )

    # FIXME: this field should be named 'count'
    form.omitted('number_to_show')
    form.no_omit(IDefaultConfigureForm, 'number_to_show')
    number_to_show = schema.List(
        title=_(u'Number of items to display'),
        value_type=schema.TextLine(),
        required=False,
    )

    form.omitted('offset')
    form.no_omit(IDefaultConfigureForm, 'offset')
    offset = schema.Int(
        title=_(u'Start at item'),
        required=False,
        default=0,
    )

    form.omitted(IDefaultConfigureForm, 'random')
    random = schema.Bool(
        title=_(u"Select random items"),
        required=False,
        default=False
    )

    autoplay = schema.Bool(
        title=_(u'Auto play'),
        required=False,
        default=True,
    )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


@implementer(ICarrosselAutomaticoTile)
class CarrosselAutomaticoTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/carrosselautomatico.pt')

    is_configurable = True
    is_editable = True
    short_name = _(u'automaticCarrossel', default=u'Auto Carrossel')
    configured_fields = []

    def results(self):
        self.configured_fields = self.get_configured_fields()
        size_conf = [i for i in self.configured_fields if i['id'] == 'number_to_show']

        if size_conf and 'size' in size_conf[0].keys():
            size = int(size_conf[0]['size'])
        else:
            size = 4

        offset = 0
        offset_conf = [i for i in self.configured_fields if i['id'] == 'offset']
        if offset_conf:
            try:
                offset = int(offset_conf[0].get('offset', 0))
            except ValueError:
                offset = 0

        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        if uuid and obj:
            results = obj.results(batch=False)
            if self.data.get('random', False):
                if size > len(results):
                    size = len(results)
                return random.sample(results, size)

            return results[offset:offset + size]
        else:
            self.remove_relation()
            return []

    def is_empty(self):
        return self.data.get('uuid', None) is None or \
            uuidToObject(self.data.get('uuid')) is None

    def populate_with_object(self, obj):
        super(CarrosselAutomaticoTile, self).populate_with_object(obj)  # check permission

        if obj.portal_type in self.accepted_ct():
            data_mgr = ITileDataManager(self)
            data_mgr.set({
                'uuid': IUUID(obj),
            })

    def accepted_ct(self):
        """Return Collection as the only content type accepted in the tile.
        """
        return ['Collection']

    def get_configured_fields(self):
        # Override this method, since we are not storing anything
        # in the fields, we just use them for configuration
        tileType = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()

        fields = getFieldsInOrder(tileType.schema)

        results = []
        for name, obj in fields:
            field = {'id': name,
                     'title': obj.title}
            if name in conf:
                field_conf = conf[name]
                if ('visibility' in field_conf and field_conf['visibility'] == u'off'):
                    # If the field was configured to be invisible, then just
                    # ignore it
                    continue

                if 'htmltag' in field_conf:
                    # If this field has the capability to change its html tag
                    # render, save it here
                    field['htmltag'] = field_conf['htmltag']

                if 'imgsize' in field_conf:
                    field['scale'] = field_conf['imgsize']

                if 'format' in field_conf:
                    field['format'] = field_conf['format']

                if 'size' in field_conf:
                    field['size'] = field_conf['size']

                if 'offset' in field_conf:
                    field['offset'] = field_conf['offset']

            results.append(field)

        return results

    def thumbnail(self, item):
        """Return a thumbnail of an image if the item has an image field and
        the field is visible in the tile.

        :param item: [required]
        :type item: content object
        """
        if self._has_image_field(item) and self._field_is_visible('image'):
            tile_conf = self.get_tile_configuration()
            image_conf = tile_conf.get('image', None)
            if image_conf:
                scaleconf = image_conf['imgsize']
                # scale string is something like: 'mini 200:200'
                # we need the name only: 'mini'
                if scaleconf == '_original':
                    scale = None
                else:
                    scale = scaleconf.split(' ')[0]
                scales = item.restrictedTraverse('@@images')
                return scales.scale('image', scale)

    def get_alt(self, obj):
        """Return the alt attribute for the image in the obj."""
        return obj.Description() or obj.Title()

    def get_uid(self, obj):
        return IUUID(obj, None)

    def autoplay(self):
        if self.data['autoplay'] is None:
            return True  # default value

        return self.data['autoplay']

    @property
    def get_image_ratio(self):
        """Return image ratio to be used in the carousel.
        See: http://galleria.io/docs/options/height/
        """
        thumbs = [self.thumbnail(i) for i in self.results()]
        # exclude from calculation any item with no image
        ratios = [
            float(t.height) / float(t.width) for t in thumbs if t is not None]
        if not ratios:
            return '1'
        return str(max(ratios))

    def init_js(self):
        if self.is_empty():
            # Galleria will display scary error messages when it
            # cannot find its <div>.  So don't start galleria unless
            # the <div> is there and has some items in it.
            return ''

        # return INIT_JS.format(
        #    self.id, self.get_image_ratio, str(self.autoplay()).lower())
        return INIT_JS.format(self.id)

    @view.memoize
    def get_image_position(self):
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('image', None)
        if image_conf:
            return image_conf['position']

    def remove_relation(self):
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if 'uuid' in old_data:
            old_data.pop('uuid')
        data_mgr.set(old_data)

    def collection_url(self):
        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        return obj.absolute_url() if obj else ''