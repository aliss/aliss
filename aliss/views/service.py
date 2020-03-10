from django.views.generic import CreateView, UpdateView, ListView, DetailView, FormView, DeleteView, TemplateView
from django.contrib import messages
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt

import pytz
from datetime import datetime

from braces.views import (
    LoginRequiredMixin,
    StaffuserRequiredMixin,
    UserPassesTestMixin
)

from aliss.models import Service, ServiceProblem, ServiceArea, Organisation, RecommendedServiceList, Location
from aliss.forms import (
    ServiceForm,
    ServiceProblemForm,
    ServiceProblemUpdateForm,
    ServiceEmailForm
)
from aliss.views import OrganisationMixin

import logging

class ServiceCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    OrganisationMixin,
    CreateView
):

    model = Service
    form_class = ServiceForm
    template_name = 'service/create.html'

    def test_func(self, user):
        return self.get_organisation().is_edited_by(user)

    def get_form_kwargs(self):
        kwargs = super(ServiceCreateView, self).get_form_kwargs()
        kwargs.update({
            'organisation': self.organisation,
            'updated_by': self.request.user,
            'created_by': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        self.object = form.save()


        messages.success(
            self.request,
            '{name} has been successfully created.'.format(
                name=self.object.name
            )
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if (self.object.organisation.services.count() <= 1):
            return reverse(
                'organisation_confirm',
                kwargs={'pk': self.object.organisation.pk}
            )

        else:
            return reverse(
                'organisation_detail',
                kwargs={'pk': self.object.organisation.pk}
            )
class ServiceCreateClaimView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    OrganisationMixin,
    CreateView
):

    model = Service
    form_class = ServiceForm
    template_name = 'service/create-claim.html'

    def test_func(self, user):
        return self.get_organisation().is_edited_by(user)

    def get_form_kwargs(self):
        kwargs = super(ServiceCreateClaimView, self).get_form_kwargs()
        kwargs.update({
            'organisation': self.organisation,
            'updated_by': self.request.user,
            'created_by': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        self.object = form.save()


        messages.success(
            self.request,
            '{name} has been successfully created.'.format(
                name=self.object.name
            )
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if (self.object.organisation.services.count() <= 1):
            return reverse(
                'organisation_confirm',
                kwargs={'pk': self.object.organisation.pk}
            )

        else:
            return reverse(
                'organisation_detail',
                kwargs={'pk': self.object.organisation.pk}
            )





class ServiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'service/update.html'

    def test_func(self, user):
        return self.get_object().is_edited_by(user)

    def get_form_kwargs(self):
        kwargs = super(ServiceUpdateView, self).get_form_kwargs()
        kwargs.update({
            'organisation': self.object.organisation,
            'updated_by': self.request.user
        })
        return kwargs

    def get_success_url(self):
        referer = self.request.META.get('HTTP_REFERER', '/')
        if 'redirect-review' in referer:
            return reverse('account_my_reviews')
        else:
            return reverse('organisation_detail_slug', kwargs={'slug': self.object.organisation.slug}
            )

    def form_valid(self, form):
        self.object.update_last_edited()
        self.object = form.save()

        messages.success(
            self.request,
            '{name} has been successfully updated.'.format(
                name=self.object.name
            )
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ServiceUpdateView, self).get_context_data(**kwargs)
        context['organisation'] = self.object.organisation
        return context


class ServiceDetailView(UserPassesTestMixin, DetailView):
    model = Service
    template_name = 'service/detail.html'
    query_pk_and_slug = True

    def test_func(self, user):
        service = self.get_object()
        return (service.is_published() or service.is_edited_by(user))

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['recommended_service_lists'] = RecommendedServiceList.objects.filter(user=self.request.user)
        locations = self.object.locations.all()
        lat_longs = {}
        for location in locations:
            lat_longs[location.street_address] = [location.latitude, location.longitude]
        context['location_lat_longs'] = lat_longs
        return context

class ServiceDetailEmbeddedMapView(UserPassesTestMixin, DetailView):
    model = Service
    template_name = 'service/embedded_map.html'
    query_pk_and_slug = True

    def test_func(self, user):
        service = self.get_object()
        return service.is_published()

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailEmbeddedMapView, self).get_context_data(**kwargs)
        locations = self.object.locations.all()
        lat_longs = {}
        for location in locations:
            lat_longs[location.street_address] = [location.latitude, location.longitude]
        context['location_lat_longs'] = lat_longs
        return context

    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ServiceDetailEmbeddedMapView, self).dispatch(*args, **kwargs)


class ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Service
    template_name = 'service/delete.html'

    def test_func(self, user):
        return self.get_object().is_edited_by(user)

    def get_success_url(self):
        return reverse(
            'organisation_detail',
            kwargs={'pk': self.object.organisation.pk}
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()

        messages.success(
            self.request,
            '{name} has been successfully deleted.'.format(
                name=self.object.name
            )
        )
        return HttpResponseRedirect(success_url)


class ServiceReportProblemView(LoginRequiredMixin, CreateView):
    model = ServiceProblem
    form_class = ServiceProblemForm
    template_name = 'service/report_problem.html'
    success_url = reverse_lazy('service_report_problem_thanks')

    def get_service(self):
        return get_object_or_404(
            Service,
            pk=self.kwargs.get('pk')
        )

    def get(self, request, *args, **kwargs):
        self.service = self.get_service()
        return super(ServiceReportProblemView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.service = self.get_service()
        return super(ServiceReportProblemView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ServiceReportProblemView, self).get_context_data(**kwargs)
        context['service'] = self.service
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.service = self.service
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url() + '?back='+reverse('service_detail', kwargs={'pk': self.object.service_id}))


class ServiceProblemListView(StaffuserRequiredMixin, ListView):
    model = ServiceProblem
    template_name = 'service/problem_list.html'
    paginate_by = 10

    def get_queryset(self):
        if self.request.GET.get('f') == "all":
            return ServiceProblem.objects.all().order_by('-created_on')
        elif self.request.GET.get('f') == "resolved":
            return ServiceProblem.objects.filter(status=1).all().order_by('-created_on')
        else:
            return ServiceProblem.objects.filter(status=0).all().order_by('-created_on')


class ServiceProblemUpdateView(StaffuserRequiredMixin, UpdateView):
    model = ServiceProblem
    form_class = ServiceProblemUpdateForm
    success_url = reverse_lazy('service_problem_list')

    def send_resolved_email(self, issue):
        link = self.request.build_absolute_uri(reverse('service_detail_slug', kwargs={ 'slug': self.object.service.slug }))

        message = "Thank you for submitting a suggestion on ALISS. "
        message += "This request for improvement has now been resolved, thank you for helping us improve ALISS."
        message += "\n\nYou can view the updated service on ALISS by following this link: {link}".format(link=link)
        message += "\n\n-----\n\n\nRegards from the ALISS team\n\nIf you need to get in touch please contact us at:\n\nhello@aliss.org or 0141 404 0239"

        send_mail(
            "Resolved: Your suggested improvement for \"{service}\" on ALISS".format(service=issue.service.name),
            message,
            settings.DEFAULT_FROM_EMAIL,
            [issue.user.email],
            fail_silently=True,
        )

    def form_valid(self, form):
        self.object = form.save()

        if self.object.status == 1:
            self.send_resolved_email(self.object)
            messages.success(self.request, 'Service issue has been resolved.')
        return HttpResponseRedirect(self.get_success_url())


class ServiceCoverageView(StaffuserRequiredMixin, TemplateView):
    template_name = 'service/coverage.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceCoverageView, self).get_context_data(**kwargs)

        services = Service.objects.prefetch_related(
                                'locations', 'service_areas'
                              ).all()
        context['services'] = services
        context['service_areas'] = ServiceArea.objects.prefetch_related('services').order_by('type', 'code')

        return context


class ServiceEmailView(SuccessMessageMixin, FormView):
    form_class = ServiceEmailForm
    success_message = "Service emailed successfully"

    def get_success_url(self):
        return reverse(
            'service_detail',
            kwargs={'pk': self.service.pk}
        )

    def form_valid(self, form):
        self.service = form.cleaned_data.get('service')

        current_site = get_current_site(self.request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'service': self.service,
            'domain': domain,
            'protocol': 'https'
        }
        subject = "Someone has emailed you a resource from ALISS"
        body = loader.render_to_string("service/email/single.txt", context)

        email_message = EmailMultiAlternatives(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [form.cleaned_data.get('email')]
        )
        html_email = loader.render_to_string("service/email/single.html", context)
        email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

        return super(ServiceEmailView, self).form_valid(form)

    def form_invalid(self, form):
        self.service = form.cleaned_data.get('service')
        error_message = "Submitted email not valid, please try again."
        messages.warning(self.request, error_message)
        failure_url = reverse('service_detail', kwargs={'pk': self.service.pk})
        return HttpResponseRedirect(failure_url)

class ServiceAtLocationDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_message = "Location successfully removed from service."
    model = Service
    template_name = 'service/detail.html'

    def get_object(self):
        service_pk = self.get_service_location_pks()['service_pk']
        object = Service.objects.get(pk=service_pk)
        return object

    def get_location_object(self):
        location_pk = self.get_service_location_pks()['location_pk']
        location = Location.objects.get(pk=location_pk)
        return location

    def test_func(self, user):
        return self.get_object().is_edited_by(user)

    def get_success_url(self):
        return reverse(
            'service_detail',
            kwargs={'pk': self.get_object().pk}
        )

    def delete(self, request, *args, **kwargs):
        service = self.get_object()
        location = self.get_location_object()
        service.locations.remove(location)
        service.save()
        success_url = self.get_success_url()
        messages.success(
            self.request,
            'Successfully removed location from service.'
            )
        return HttpResponseRedirect(success_url)

    def get_service_location_pks(self):
        service_at_location_pks = {}
        service_at_location_slug = self.kwargs.get("service_at_location_pk")
        pk_array = service_at_location_slug.split(':')
        service_pk = pk_array[0]
        location_pk = pk_array[1]
        service_at_location_pks['service_pk'] = service_pk
        service_at_location_pks['location_pk'] = location_pk
        return service_at_location_pks
