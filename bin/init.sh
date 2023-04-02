#!/bin/bash

set -e

# install the Wordpess cli
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar

# downlaod the Wordpress theme sample XML file
mkdir -p /xml
curl https://raw.githubusercontent.com/WPTT/theme-unit-test/master/themeunittestdata.wordpress.xml -o /xml/import.xml

# Install and setup Wordpress
php wp-cli.phar core install --allow-root --url=localhost:8888 --title=WordPress --admin_user=$ADMIN_USER --admin_password=$ADMIN_PASSWORD --admin_email=$ADMIN_EMAIL

# Install the Wordpress importer plugin
php wp-cli.phar plugin install wordpress-importer --activate --allow-root

# Install the Wordpress WPGraphQL plugin and wp-graphql-offset-pagination plugin
php wp-cli.phar plugin install wp-graphql --activate --allow-root
php wp-cli.phar plugin activate wp-graphql-offset-pagination --allow-root

# Import the Wordpress XML file
php wp-cli.phar import /xml/import.xml --authors=create --allow-root

# Enable the json API
php wp-cli.phar rewrite structure /%postname%/ --allow-root

# Alter the URL to the HOST in .env
php wp-cli.phar search-replace 'http://localhost:8888' ${HOST} --allow-root
