# Checks

Run against a development site running at, e.g. localhost:8000 and is ready to accept HTTP requests.

## Model Endpoint Response

> Find specific endpoints that don't return a 200 response code.

```bash
python manage.py model_response
```

It checks a single endpoint of each page model for both the admin site (edit) and front end (view) and reports the response codes.

## Model Types Endpoint Report

> Quickly locate a page model edit url that uses a given content type.

```bash
python manage.py model_types [-i]
```

Output a report of page types in a project.

- Run without options to list all content types
- Run with a given content type PK option to list all pages created from a single content type.
