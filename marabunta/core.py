# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Marabunta is a name given to the migration of the legionary ants or to the ants
themselves. Restless, they eat and digest everything in their way.

This tool aims to run migrations for Odoo versions as efficiencly as a
Marabunta migration.

It loads migration instructions from a YAML file and run the operations if
required.

TODO: move in its own GitHub project
"""

from __future__ import print_function

from .config import Config, get_args_parser
from .database import Database, MigrationTable
from .parser import YamlParser
from .runner import Runner

__version__ = "0.0.1"


def migrate(config):
    migration_parser = YamlParser.parse_from_file(config.project_file)
    migration = migration_parser.parse()
    database = Database(config)
    with database.connect() as conn:
        with conn.cursor() as cursor:
            try:
                table = MigrationTable(cursor)
                runner = Runner(config, migration, cursor, table)
                runner.perform()
            except:
                # We want to commit even if we had an error in a migration
                # script! Thus we have an entry in the migration table
                # indicating that a migration has been started but not
                # finished
                conn.commit()
                raise
            else:
                conn.commit()
            finally:
                conn.close()


def main():
    parser = get_args_parser()
    args = parser.parse_args()
    config = Config.from_parse_args(args)
    migrate(config)

if __name__ == '__main__':
    main()