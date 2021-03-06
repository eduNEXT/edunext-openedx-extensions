#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django command to import the users of an external database
"""
import json
import logging
from pprint import pformat as pf

from django.core.management.base import BaseCommand, CommandError

try:
    from xml_importer.database_xml_dump_importer import DatabaseXmlDumpImporter
except ImportError as detail:
    print 'ImportError :', detail

LOGGER = logging.getLogger(__name__)  # pylint: disable=no-member


class Command(BaseCommand):
    """
    Command import_import_xml_db
    """
    help = 'Imports and Loads the data from an XML dump of a mirosite db'
    USERS_JSON = 'imported_users.json'
    ENROLLMENTS_JSON = 'imported_enrollments.json'
    STUDENTMODULE_JSON = 'imported_studentmodule.json'

    def add_arguments(self, parser):
        """
        Add arguments
        """
        parser.add_argument('xmldumpfile', type=str,
                            help='The xml dump of the database that will be imported')
        parser.add_argument('--users', type=str, nargs='+',
                            required=False, help='List of users (ids) to import')
        parser.add_argument('--microsite', type=str,
                            required=False, help='Microsite host to add to user')
        parser.add_argument('--dry-run', action='store_true',
                            required=False, help='Run without saving')
        parser.add_argument('--keep-user-flags', type=bool, default=False, required=False,
                            help='Keeps special user flags (superuser and staff). Default:False')
        parser.add_argument('--skip-inactive', type=bool, default=True,
                            required=False, help='Skips inactive users. Default:True')
    # pylint: disable=unused-argument

    def handle(self, *args, **options):
        """Entry point for the command.

        Args:
            options (dict): all the options called from the cli
        """

        # Get the parameters
        print options
        filename = options['xmldumpfile']
        microsite = options['microsite']
        dry_run = options['dry_run']
        keep_special_flags = options['keep_user_flags']
        skip_inactive = options['skip_inactive']

        user_statements = options.get('users', [])
        user_ids = []
        for statement in user_statements:
            if statement.isdigit():
                as_int = int(statement)
                user_ids.append(as_int)
            else:
                try:
                    limits = statement.split("-")
                    as_range = range(int(limits[0]), int(limits[1]) + 1)
                    user_ids = user_ids + as_range
                except Exception:
                    raise CommandError(
                        "Could not process imput {}".format(statement))

        LOGGER.info("Users to import: %s ", user_ids)
        LOGGER.info("Microsite: %s ", microsite)

        # TODO: if we validate this, we might as well validate it for real with
        # a dom parser or similar
        if not filename.endswith(".xml"):
            raise CommandError(
                "File {} is not an xml (*.xml)".format(filename))

        importer = DatabaseXmlDumpImporter(filename, dry_run)

        users_imported = importer.import_users(
            user_ids, keep_special_flags, skip_inactive, microsite)
        LOGGER.debug("Users Imported:\n" + pf(users_imported, indent=4))
        self.save_dic_list(self.USERS_JSON, users_imported)

        enrolled = importer.enroll_users(users_imported)
        LOGGER.debug("Enrollments imported:\n" + pf(enrolled, indent=4))
        self.save_dic_list(self.ENROLLMENTS_JSON, users_imported)

        studentmodules = importer.import_studentmodule(users_imported)
        LOGGER.debug("Studentmodules imported:\n" +
                     pf(studentmodules, indent=4))
        self.save_dic_list(self.STUDENTMODULE_JSON, studentmodules)

    def save_dic_list(self, filename, new_list):
        """Saves a list of dics as a log, creating new file if none existent and appending new lists to old files.
        Args:
            filename (srt): file location
            new_list (list of dics): dictionaries to log
        """
        # Load current data
        current_list = []
        try:
            data_file = open(filename, 'r')
            current_list = json.load(data_file)
            data_file.close()
        except IOError:
            current_list = []

        # Add new to current
        final_list = current_list + new_list

        # Save new data
        with open(filename, 'w+') as data_file:
            json.dump(final_list, data_file, indent=4)
