
import superdesk

from .migrate_topics import MigrateTopicsCommand


superdesk.command('ntb:migrate_topics', MigrateTopicsCommand())
