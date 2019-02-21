import string
from django.views.generic import View, TemplateView
from django.views.generic.list import MultipleObjectMixin
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect

from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from aliss.paginators import ESPaginator
from aliss.forms import SearchForm
from aliss.models import Postcode, Service, Category
from aliss.search import (
    filter_by_query,
    filter_by_postcode,
    filter_by_location_type,
    filter_by_category,
    postcode_order,
    keyword_order,
    combined_order
)

import logging


class SearchView(MultipleObjectMixin, TemplateView):
    template_name = 'search/results.html'
    #paginator_class = ESPaginator
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['postcode'] = self.postcode
        service_area = self.postcode.get_local_authority()
        if service_area:
            context['service_area'] = service_area.name
        context['category'] = self.category
        context['expanded_radius'] = self.radius * 2
        return context

    def get(self, request, *args, **kwargs):

        # check for the location param
        location = self.request.GET.get("location")
        # logger = logging.getLogger(__name__)
        # logger.error(str(location))
        if "Brechin" or "Dundee" or "Erskine" in str(location):
            self.q = self.request.GET.get('q', None)
            puncstripper = str.maketrans('', '', string.punctuation.replace('-', '')) #keep -
            if self.q:
                self.q = self.q.translate(puncstripper)
            self.location_type = None
            self.sort = self.request.GET.get('sort', None)
            self.category = self.request.GET.get('category', None)
            if self.category:
                self.category = Category.objects.get(slug=self.category)
            self.radius = None
            if self.radius == None:
                self.radius = 20000

            if "Brechin" in str(location):
                postcode = Postcode.objects.get(postcode = "EH21 6UW")
                self.postcode = Postcode.objects.get(postcode=postcode)
                self.object_list = self.filter_queryset(self.get_queryset())
                return self.render_to_response(self.get_context_data())

            if "Dundee" in str(location):
                postcode = Postcode.objects.get(postcode = "EH21 6UW")
                self.postcode = Postcode.objects.get(postcode=postcode)
                self.object_list = self.filter_queryset(self.get_queryset())
                return self.render_to_response(self.get_context_data())

            if "Erskine" in str(location):
                postcode = Postcode.objects.get(postcode = "EH21 6UW")
                self.postcode = Postcode.objects.get(postcode=postcode)
                self.object_list = self.filter_queryset(self.get_queryset())
                return self.render_to_response(self.get_context_data())

        search_form = SearchForm(data=self.request.GET)

        if search_form.is_valid():
            self.q = search_form.cleaned_data.get('q', None)
            puncstripper = str.maketrans('', '', string.punctuation.replace('-', '')) #keep -
            self.q = self.q.translate(puncstripper)
            self.location_type = search_form.cleaned_data.get('location_type',None)
            self.sort = search_form.cleaned_data.get('sort', None)
            self.category = search_form.cleaned_data.get('category', None)
            self.radius = search_form.cleaned_data.get('radius', None)
            if self.radius == None:
                self.radius = 20000

            postcode = search_form.cleaned_data.get('postcode', None)
            try:
                if postcode and len(postcode) > 3:
                    self.postcode = Postcode.objects.get(postcode=postcode)
                else:
                    self.postcode = Postcode.get_by_district(postcode)
            except Postcode.DoesNotExist:
                return self.render_to_response(context={'invalid_area': True})

            self.object_list = self.filter_queryset(self.get_queryset())
            return self.render_to_response(self.get_context_data())
        else:
            invalid_area = search_form.cleaned_data.get('postcode', None) == None
            return self.render_to_response(context={
                'form': search_form,
                'errors': search_form.errors,
                'invalid_area': invalid_area
            })

    def get_queryset(self, *args, **kwargs):
        connections.create_connection(
            hosts=[settings.ELASTICSEARCH_URL], timeout=20, http_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD))
        queryset = Search(index='search', doc_type='service')
        if self.request.user.is_staff:
            queryset = queryset.extra(explain=True)
        return queryset

    def filter_queryset(self, queryset):
        if self.category:
            queryset = filter_by_category(queryset, self.category)
        if self.location_type:
            queryset = filter_by_location_type(queryset, self.location_type)
        if self.postcode:
            queryset = filter_by_postcode(queryset, self.postcode, self.radius)
        if self.q:
            queryset = filter_by_query(queryset, self.q)

        if self.q and self.sort == 'keyword':
            results = keyword_order(queryset)
        elif self.q and self.sort in ['best_match', None, '']:
            results = combined_order(queryset, self.postcode)
        else:
            results = postcode_order(queryset, self.postcode)
        return Service.objects.filter(id__in=results["ids"]).order_by(results["order"])


class SearchShareView(View):
    def get(self, request, *args, **kwargs):
        postcode = self.kwargs.get('postcode')
        query = self.kwargs.get('query')
        return HttpResponseRedirect(
            "{url}?postcode={postcode}{query}".format(
                url=reverse('search'),
                postcode=postcode,
                query="&q={query}".format(query=query) if query else ''
            )
        )
