#!/bin/bash

set -e

# Install a Wordpress theme
php wp-cli.phar theme install twentytwentyone --allow-root
php wp-cli.phar theme activate twentytwentyone --allow-root