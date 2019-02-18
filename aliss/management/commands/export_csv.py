from django.core.management.base import BaseCommand, CommandError
from aliss.models import *

from django.db import models
from django.http import StreamingHttpResponse
from django.views.generic import View
import csv
from django.shortcuts import render
from urllib.request import Request, urlopen

class Command(BaseCommand):




    def write_collection_csv(self, collection, filepath, object_dict):

        def generate_permalink(record, model):
            id = str(record.id)
            start_url = "www.aliss.org/" + model + "/"
            permalink = start_url + id + "/"
            return permalink

        def get_value(record, key):
            return getattr(record, key, "")

        def get_nested_value(record, keys):
            object = get_value(record, keys[0])
            value = get_value(object, keys[1])
            return value

        def get_nested_value_list(record, keys):
            values = ""
            objects_list = get_value(record, keys[0])
            for object in objects_list.all():
                values += "\"" + str(get_value(object, keys[1])) + "\" "
            return values

        def get_nested_permalink(record, keys):
            object = get_value(record, keys[0])
            nested_permalink = generate_permalink(object, keys[1])
            return nested_permalink

        def get_nested_permalinks_list(record, keys):
            values = ""
            objects_list = get_value(record, keys[0])
            for object in objects_list.all():
                values += "\"" + generate_permalink(object, keys[0]) + "\" "
            return values

        def generate_aliss_url(record, model):
            aliss_url = ""
            if record.slug:
                slug = str(record.slug)
                start_url = "www.aliss.org/" + model + "/"
                aliss_url = start_url + slug + "/"
            return aliss_url

        def get_values_dict(record, value_names):
            list_values = list(value_names)
            results = []
            for value_element in list_values:
                if isinstance(value_element, list):
                    if "list" in value_element:
                        results.append(get_nested_value_list(record, value_element))
                    elif "permalink" in value_element:
                        results.append(generate_permalink(record, value_element[0]))
                    elif "nested_url" in value_element:
                        results.append(get_nested_permalinks_list(record, value_element))
                    elif "aliss_url" in value_element:
                        results.append(generate_aliss_url(record, value_element[0]))
                    elif "nested_permalink" in value_element:
                        results.append(get_nested_permalink(record, value_element))
                    else:
                        results.append(get_nested_value(record, value_element))
                else:
                    results.append(get_value(record, value_element))
            return results


        fieldnames = object_dict.keys()
        with open(filepath, mode='w') as output_file:
            csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(fieldnames)
            for record in collection:
                csv_writer.writerow(get_values_dict(record, object_dict.values()))

    def handle(self, *args, **options):

        service_dict = {
            "id": "id",
            "name": "name",
            "description": "description",
            "url": "url",
            "phone_number": "phone",
            "email_address": "email",
            "aliss_url": ["services", "aliss_url"],
            "permalink": ["services", "permalink"],
            "last_edited": "last_edited",
            "organisation_id": "organisation_id",
            "organisation_name": ["organisation", "name"],
            "orgasnisation_permalink": ["organisation", "organisations", "nested_permalink"],
            "categories": ["categories", "name", "list"],
            "service_areas": "service_areas",
            "locations_ids": ["locations", "id", "list"],
        }

        location_dict = {
            "id": "id",
            "formatted_address": "formatted_address",
            "name": "name",
            "locality": "locality",
            "region": "region",
            "postal_code": "postal_code",
            "country": "country",
            "latitude": "latitude",
            "longitude": "longitude",
            "organisation_name": ["organisation", "name"],
            "organisation_id": "organisation_id",
        }

        organisation_dict = {
            "id": "id",
            "name": "name",
            "description": "description",
            "aliss_url": ["organisations", "aliss_url"],
            "permalink": ["organisations", "permalink"],
            "url": "url",
            "twitter": "twitter",
            "facebook": "facebook",
            "phone": "phone",
            "email": "email",
            "last_edited": "last_edited",
            "service_names": ["services", "name", "list"],
            "service_ids": ["services", "id", "list"],
            "service_permalink": ["services", "nested_url"],
        }

        self.stdout.write("\nWriting Services CSV\n")
        services_collection = Service.objects.all()[:5]
        self.write_collection_csv(services_collection, "aliss_service_result.csv", service_dict)
        #
        # self.stdout.write("\nWriting Locations CSV\n")
        # locations_collection = Location.objects.all()[:5]
        # self.write_collection_csv(locations_collection, "aliss_location_result.csv", location_dict)

        self.stdout.write("\nWriting Organisations CSV\n")
        organisations_collection = Organisation.objects.all()[:5]
        self.write_collection_csv(organisations_collection, "aliss_organisation_result.csv", organisation_dict)


#name, description, url, phone, email, aliss_url, permalink, last_edited, organisation_id, organisation_name, organisation_permalink, categories, service_areas, location_ids
