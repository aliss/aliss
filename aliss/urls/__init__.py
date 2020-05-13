from django.conf.urls import url, include
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.sitemaps import views

from aliss.views import SearchShareView, ReportsView
from aliss.sitemap import *

sitemaps = {
    'services': ServiceSitemap,
    'organisations': OrganisationSitemap,
    'searches': SearchSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name="homepage.html"),
        name='homepage'
    ),
    url(r'^terms-and-conditions/$',
        TemplateView.as_view(template_name="terms-and-conditions.html"),
        name='terms_and_conditions'
    ),
    url(r'^privacy-policy/$',
        TemplateView.as_view(template_name="privacy-policy.html"),
        name='privacy_policy'
    ),
    url(r'^about/$',
        TemplateView.as_view(template_name="about.html"),
        name='about'
    ),
    url(r'^help/$',
        TemplateView.as_view(template_name="help.html"),
        name='help'
    ),
    url(r'^access-to-information/$',
        TemplateView.as_view(template_name="landing-page-users.html"),
        name='landing_page_users'
    ),
    url(r'^information-to-share/$',
        TemplateView.as_view(template_name="landing-page-helpers.html"),
        name='landing_page_helpers'
    ),
    url(r'^promote-assess-demand-charity-services/$',
        TemplateView.as_view(template_name="landing-page-charity.html"),
        name='landing_page_charity'
    ),
    url(r'^lightening-the-load-on-your-organisation/$',
        TemplateView.as_view(template_name="landing-page-leaders.html"),
        name='landing_page_leaders'
    ),
    url(r'^service-area-definition/$',
        TemplateView.as_view(
            template_name='service_area_definition.html'
        ),
        name='service_area_definition'
    ),
    url(r'^places/', include('aliss.urls.places')),
    url(r'^reports/$', ReportsView.as_view(), name='reports'),
    url(r'^account/', include('aliss.urls.account')),
    url(r'^search/', include('aliss.urls.search')),
    url(r'^organisations/', include('aliss.urls.organisation')),
    url(r'^locations/', include('aliss.urls.location')),
    url(r'^services/', include('aliss.urls.service')),
    url(r'^claims/', include('aliss.urls.claim')),
    url(r'^sitemap\.xml$', views.index, {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', views.sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^(?P<postcode>[0-9A-Za-z ]+)/((?P<query>.+)/)?$', SearchShareView.as_view(), name='search_share')
]

if not settings.DEBUG:
    urlpatterns.append(url(r'^robots\.txt$', TemplateView.as_view(template_name="production-robots.txt", content_type='text/plain')))
else:
    urlpatterns.append(url(r'^robots\.txt$', TemplateView.as_view(template_name="staging-robots.txt", content_type='text/plain')))
