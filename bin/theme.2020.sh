#!/bin/bash

set -e

# Install a Wordpress theme
php wp-cli.phar theme install twentytwenty --allow-root
php wp-cli.phar theme activate twentytwenty --allow-root