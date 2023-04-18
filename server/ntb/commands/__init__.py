
import superdesk

from .update_items import UpdateItemsCommand
from .sync_topics import SyncTopicsCommand
from .fix_events_moment_timezone_2023 import FixEventsCommand


superdesk.command('ntb:update_items', UpdateItemsCommand())
superdesk.command('ntb:sync_topics', SyncTopicsCommand())
superdesk.command('ntb:fix_events_moment_2023', FixEventsCommand())
