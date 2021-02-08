
import superdesk

from .update_items import UpdateItemsCommand


superdesk.command('ntb:update_items', UpdateItemsCommand())
