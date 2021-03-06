# -*- coding: utf-8 -*-
from plone.app.testing import PloneSandboxLayer
from PIL import Image
from plone import api
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from StringIO import StringIO

import random


def generate_jpeg(width, height):
    # Mandelbrot fractal
    # FB - 201003254
    # drawing area
    xa = -2.0
    xb = 1.0
    ya = -1.5
    yb = 1.5
    maxIt = 25  # max iterations allowed
    # image size
    image = Image.new('RGB', (width, height))
    c = complex(random.random() * 2.0 - 1.0, random.random() - 0.5)

    for y in range(height):
        zy = y * (yb - ya) / (height - 1) + ya
        for x in range(width):
            zx = x * (xb - xa) / (width - 1) + xa
            z = complex(zx, zy)
            for i in range(maxIt):
                if abs(z) > 2.0:
                    break
                z = z * z + c
            r = i % 4 * 64
            g = i % 8 * 32
            b = i % 16 * 16
            image.putpixel((x, y), b * 65536 + g * 256 + r)

    output = StringIO()
    image.save(output, format='PNG')
    return output.getvalue()


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(Fixture, self).setUpZope(app, configurationContext)
        # Load ZCML
        import metodista.site.tiles
        self.loadZCML(package=metodista.site.tiles)

    def setUpPloneSite(self, portal):
        super(Fixture, self).setUpPloneSite(portal)
        with api.env.adopt_roles(roles=['Manager']):

            # Install into Plone site using portal_setup
            self.applyProfile(portal, 'metodista.site.tiles:default')

            api.content.create(
                type='Folder',
                title='my-news-folder',
                container=portal
            )
            api.content.create(
                type='News Item',
                title='my-news',
                container=portal['my-news-folder']
            )
            api.content.create(
                type='Image',
                title='my-image',
                container=portal['my-news-folder']
            ).setImage(generate_jpeg(50, 50))
            api.content.create(
                container=portal['my-news-folder'],
                type='Collection',
                title='my-collection',
                description=u'Image gallery',
                query=[{
                    'i': 'Type',
                    'o': 'plone.app.querystring.operation.string.is',
                    'v': ['Image'],
                }]
            )
            portal['my-news-folder'].reindexObject()
            portal['my-news-folder']['my-news'].reindexObject()
            portal['my-news-folder']['my-image'].reindexObject()
            portal['my-news-folder']['my-collection'].reindexObject()

FIXTURE = Fixture()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='metodista.site.tiles:Integration',
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='metodista.site.tiles:Functional',
)
