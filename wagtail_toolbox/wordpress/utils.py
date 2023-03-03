import requests


def parse_wordpress_routes(host):
    resp = requests.get(host + "/wp-json/")
    if resp.status_code != 200:
        raise Exception("Could not get wordpress routes")
    routes = [
        {
            "wp-json"
            + route: {
                "host": value.get("_links")["self"][0]["href"],
                "name": route.split("/")[-1],
                "model": "WP" + route.split("/")[-1].capitalize(),
            }
        }
        for route, value in resp.json()["routes"].items()
        if value["namespace"] == "wp/v2"
        and (value["methods"] == ["GET", "POST"] or value["methods"] == ["GET"])
        and len(route.split("/")) == 4  # only get the top level routes
    ]
    sorted_routes = sorted(routes, key=lambda x: list(x.keys())[0])
    return sorted_routes
