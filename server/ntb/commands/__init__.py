
import superdesk

from .update_items import UpdateItemsCommand
from .sync_topics import SyncTopicsCommand


superdesk.command('ntb:update_items', UpdateItemsCommand())
superdesk.command('ntb:syn_topics', SyncTopicsCommand())
