import sys

import requests

_session = requests.Session()


class Client:
    # TODO: decide if this api is really of any benefit
    def __init__(self, host, url):
        self.host = host
        self.url = url
        self.urls = {}

        try:
            self.response = _session.get(self.build_url)

            sys.stdout.write(f"Fetching {self.build_url}\n")

            if not self.response.ok:
                sys.stdout.write(f"Error: {self.response.text}\n")
                raise Exception(self.response.text)
        except Exception as e:
            sys.stdout.write(f"Error: {e}\n")
            raise e

    def get(self, url):
        try:
            return _session.get(url).json()
        except Exception as e:
            raise e

    @property
    def build_url(self):
        return f"{self.host}/{self.url}"

    def parse_response(self):
        for item in self.response.json():
            self.urls[item["model"]] = {
                "object_list": item["objects"],
                "related_list": item["url_with_related"],
            }

    def get_wordpress_objects(self, model):
        # a list of urls for each object
        return self.urls[model]["object_list"]

    def get_wordpress_related(self, model):
        # a url for all the objects with related records
        return self.urls[model]["related_list"]
