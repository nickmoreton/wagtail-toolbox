#!/bin/bash

set -e

# Install a Wordpress theme
php wp-cli.phar theme install twentytwentytwo --allow-root
php wp-cli.phar theme activate twentytwentytwo --allow-root