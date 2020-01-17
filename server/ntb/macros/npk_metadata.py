import logging

from superdesk import get_resource_service
from superdesk.errors import StopDuplication

logger = logging.getLogger(__name__)


def npk_metadata_macro(item, **kwargs):
    """
    The NPKSisteNytt Metadata Macro will perform the following changes to current content item:
    - change the byline to "(NPK-NTB)"
    - change the signoff to "npk@npk.no"
    - change the body footer to "(©NPK)" - NB: copyrightsign, not @
    - change the service to "NPKSisteNytt"
    - change the language to "nn-NO"
    """

    desk_id = kwargs.get('dest_desk_id')
    if not desk_id:
        logger.warning("no destination id specified")
        return
    stage_id = kwargs.get('dest_stage_id')
    if not stage_id:
        logger.warning("no stage id specified")
        return

    archive_service = get_resource_service('archive')
    move_service = get_resource_service('move')
    translate_service = get_resource_service('translate')

    # change item
    item['byline'] = 'NPK-' + item.get('byline', '')
    item['sign_off'] = 'npk@npk.no'
    item['body_footer'] = '(©NPK)'
    item['anpa_category'] = [
        {
            'qcode': 's',
            'selection_type': 'single selection',
            'name': 'NPKSisteNytt',
            'language': 'nn-NO',
            'scheme': None
        }
    ]
    item['language'] = 'nn-NO'
    # make a translation
    new_id = translate_service.create([item])
    # move item to the desk/stage
    dest = {"task": {"desk": desk_id, "stage": stage_id}}
    move_service.move_content(new_id, dest)
    # apply the update
    new_item = archive_service.find_one(req=None, _id=new_id)
    archive_service.put(new_id, new_item)

    raise StopDuplication


name = 'NPKSisteNytt Metadata Macro'
label = 'NPKSisteNytt Metadata Macro'
callback = npk_metadata_macro
access_type = 'frontend'
action_type = 'direct'
