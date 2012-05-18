"Test for template tags."

from django.template import Template, TemplateSyntaxError
from django.template.context import RequestContext
from django.test.client import RequestFactory

from .base import ScribblerDataTestCase


class RenderScribbleTestCase(ScribblerDataTestCase):
    "Tag to render a scribble for the current page."

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/foo/')
        self.scribble = self.create_scribble(
            url='/foo/', slug='sidebar',
            content='<p>Scribble content.</p>'
        )

    def render_template_tag(self, slug, context=None, default='<p>Default.</p>'):
        "Render the template tag."
        context = context or {}
        template = Template("""
            {{% load scribbler_tags %}}{{% scribble {0} %}}{1}{{% endscribble %}}
        """.format(slug, default))
        context = RequestContext(self.request, context)
        return template.render(context)

    def test_basic_rendering(self):
        "Render a scribble by the slug."
        result = self.render_template_tag(slug='"sidebar"')
        self.assertEqual(result.strip(), '<p>Scribble content.</p>')

    def test_variable_slug(self):
        "Render a scribble by the slug as a context variable."
        result = self.render_template_tag(slug='foo', context={'foo': 'sidebar'})
        self.assertEqual(result.strip(), '<p>Scribble content.</p>')

    def test_slug_not_found(self):
        "Render default if scribble not found by slug."
        self.scribble.slug = 'blip'
        self.scribble.save()
        result = self.render_template_tag(slug='"sidebar"')
        self.assertEqual(result.strip(), '<p>Default.</p>')

    def test_url_not_found(self):
        "Render default if scribble not found for the current url."
        self.scribble.slug = '/bar/'
        self.scribble.save()
        result = self.render_template_tag(slug='"sidebar"')
        self.assertEqual(result.strip(), '<p>Default.</p>')

    def test_default_rendering(self):
        "Render default if no scribbles exist."
        self.scribble.delete()
        result = self.render_template_tag(slug='"sidebar"')
        self.assertEqual(result.strip(), '<p>Default.</p>')

    def test_no_slug_given(self):
        "Slug is required by the tag."
        self.assertRaises(TemplateSyntaxError, self.render_template_tag, slug='')