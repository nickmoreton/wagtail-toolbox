# Wordpress Importer

## This is a work in progress

However, it is functional and can be used to import a Wordpress site into Wagtail.

## Development setup

You will need to have virtual environment activated to install the python dependencies.

There is a requirements.txt file in the root of the project that can be used to install the python dependencies. Or you can use Poetry to install the dependencies and activate a virtual environment.

### Using Poetry

```bash
poetry install
poetry shell
```

### Wordpress demo site

If you have a Wordpress site already up & running you can use that as a data source for the importer, it will need the JSON API enabled.

If you don't have a Wordpress site, you can use the Wordpress demo site provided in this project.

The Wordpress demo site is used as a data source to test the importer. It is a complete Wordpress site that runs in a Docker container. It's based on the [Wordpress theme testing site](https://developer.wordpress.org/themes/getting-started/).

The Docker container is defined in the `docker-compose.yml` file in the root of the project. It runs a MySQL database and a Wordpress site.

To setup the Wordpress demo site container, run the following commands:

```bash
make wp-setup
make wp-up
make wp-init
```

The `wp-setup` command will create a `wp-data` volume that will be used to store the database data. The `wp-up` command will start the Wordpress demo site container. The `wp-init` command will install Wordpress and activate the JSON API plugin.

The Wordpress demo site will be available at [http://localhost:8888](http://localhost:8888).

### Wagtail site

In the folder `testapp` there is a Wagtail site that can be used to test the importer. It is a complete Wagtail site based on the [Wagtail User Guide example blog site](https://docs.wagtail.org/en/stable/getting_started/tutorial.html).

To setup the Wagtail site, run the following commands:

```bash
make migrate
make superuser
make server
```

The Wagtail site will be available at [http://localhost:8000](http://localhost:8000).

You can log in to the Wagtail admin at [http://localhost:8000/admin](http://localhost:8000/admin) with the username `admin` and password `password`.

### Wagtail Initial Setup

The Wagtail site needs to be setup before the importer can be used. This is done by running the following commands:

```bash
make init-wagtail
```

This will create the following pages as children of the Home page:

- [Blog](http://localhost:8000/blog/)
- [Tags](http://localhost:8000/tags/)

In the admin you should now see a new menu item called `WP Import` whcih has the following sub-menu items:

- Wordpress Host
- Import Data
- Transfer Data
- plus a number of sub-menu items for each of the Wordpress content types that can be access in the [Django admin](http://localhost:8000/wordpress-import-admin/wordpress/).

#### Wordpress Host

The Wordpress Host page is used to store the JSON API urls of the Wordpress site that will be used as a data source for the importer.

You can enter these manually or use the provided command to automatically populate the page with the default Wordpress demo site urls.

```bash
make init-host
```

#### Import Data

The Import Data page is used to import the data from the Wordpress site into the Wagtail site but the data is only available in the Django admin site.

The intention is that the data will be imported into the Django admin site and then transferred to the Wagtail site using the Transfer Data page.

Run an initial import of the data from the Wordpress site into the Django admin site using the following command:

```bash
make import-all
```

This will import the following data into the Django admin site:

- [Authors](http://localhost:8000/wordpress-import-admin/wordpress/wpauthor/)
- [Categories](http://localhost:8000/wordpress-import-admin/wordpress/wpcategory/)
- [Tags](http://localhost:8000/wordpress-import-admin/wordpress/wptag/)
- [Media](http://localhost:8000/wordpress-import-admin/wordpress/wpmedia/)
- [Pages](http://localhost:8000/wordpress-import-admin/wordpress/wppage/)
- [Posts](http://localhost:8000/wordpress-import-admin/wordpress/wppost/)
- [Comments](http://localhost:8000/wordpress-import-admin/wordpress/wpcomment/)

ORDER MATTERS: The data needs to be imported in the order above to preserve the relationships between the data.

Next, the Django admin [Streamfield signature tables](http://localhost:8000/wordpress-import-admin/wordpress/streamblocksignatureblocks/) need to be seeded with data that is used to map the content of each page to streamfield blocks when the import process is run.

Run the following commands to seed the Django admin tables:

```bash
make inspect-post
make inspect-page
```

IMPORANT: Re-run the import command to import the data again. This time the data will be mapped to streamfield blocks and saved to the Wagtail site.

```bash
make import-all
```

#### Transfer Data to Wagtail

##### Via the Wagtail Admin

The [Transfer Data admin page](http://localhost:8000/admin/transfer-wordpress-data/) is used to transfer the data from the Django admin site to the Wagtail site.

You can be selective about which posts to import by expanding the `select records` chooser and selecting the posts you want to import or import all posts.

If you view the [Blog](http://localhost:8000/blog/) page in the Wagtail site you should now see the imported posts.

If you view the [Blog Index](http://localhost:8000/admin/pages/4/) page in the Wagtail admin you should now see the imported posts as children of the page.

Imported content should be visible within the streamfield blocks it was mapped to in the Django admin site.

##### Via a management command

There is also a management command you can use `python managae.py transfer` but there are options you will need to specify.

## TODO

- Link up rich text fields anchor links and images etc.
- Add more blocks for content types that are not currently supported. e.g. Table, Gallery, Video, Audio, and more...
- Add support for importing comments.
- Add support for importing custom post types (pages)
- Add more tests
- Add more documentation
