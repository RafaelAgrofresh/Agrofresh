from django.db.backends.postgresql.base import (
    DatabaseWrapper as Psycopg2DatabaseWrapper,
)
from django.db import ProgrammingError
from .schema import TimescaleSchemaEditor
import logging
logger = logging.getLogger(__name__)


class DatabaseWrapper(Psycopg2DatabaseWrapper):
    SchemaEditorClass = TimescaleSchemaEditor

    def prepare_database(self):
        """Prepare the configured database.
        This is where we enable the `timescaledb` extension
        if it isn't enabled yet."""

        super().prepare_database()
        self.enable_timescaledb_extension()
        self.disable_timescaledb_telemetry()

    def enable_timescaledb_extension(self):
        with self.cursor() as cursor:
            try:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS timescaledb')
            except ProgrammingError:  # permission denied
                logger.warning(
                    'Failed to create "timescaledb" extension. '
                    'Usage of timescale capabilities might fail'
                    'If timescale is needed, make sure you are connected '
                    'to the database as a superuser '
                    'or add the extension manually.',
                    exc_info=True
                )

    def disable_timescaledb_telemetry(self):
        with self.schema_editor() as schema_editor:
            try:
                schema_editor.set_telemetry_level("off")

            except ProgrammingError:  # permission denied
                logger.warning(
                    'Failed to disable "timescaledb" telemetry.',
                    exc_info=True
                )
