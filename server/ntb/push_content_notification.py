
import enum
import logging

from flask import current_app as app, json
from superdesk.timer import timer
from superdesk.signals import item_updated
from superdesk.publish.formatters import NINJSFormatter
from superdesk.publish.transmitters import AmazonSQSFIFOPublishService

logger = logging.getLogger(__name__)


class SQSConfig(enum.Enum):
    ACCESS_KEY_ID = "AMAZON_SQS_ACCESS_KEY_ID"
    SECRET_ACCESS_KEY = "AMAZON_SQS_SECRET_ACCESS_KEY"
    REGION = "AMAZON_SQS_REGION"
    QUEUE_NAME = "AMAZON_SQS_QUEUE_NAME"
    ENDPOINT_URL = "AMAZON_SQS_ENDPOINT_URL"
    MESSAGE_GROUP_ID = "AMAZON_SQS_MESSAGE_GROUP_ID"


def should_send_notification(updated, original) -> bool:
    updated_task = updated.get("task") or {}
    original_task = original.get("task") or {}
    return (
        updated.get("state") != original.get("state") or
        updated_task.get("desk") != original_task.get("desk") or
        updated_task.get("stage") != original_task.get("stage")
    )


def push_notification(sender, item, original, **kwargs):
    if not should_send_notification(item, original):
        return

    if not app.config.get(SQSConfig.ACCESS_KEY_ID.value):
        return

    try:
        formatted_item = NINJSFormatter()._transform_to_ninjs(item, None, False)
        # extra info
        formatted_item["state"] = item.get("state")
    except Exception:
        logger.exception("Could not format updated item.")
        return

    queue_item = dict(
        formatted_item=json.dumps(formatted_item),
        destination=dict(
            config=dict(
                access_key_id=app.config[SQSConfig.ACCESS_KEY_ID.value],
                secret_access_key=app.config[SQSConfig.SECRET_ACCESS_KEY.value],
                region=app.config[SQSConfig.REGION.value],
                queue_name=app.config[SQSConfig.QUEUE_NAME.value],
                endpoint_url=app.config[SQSConfig.ENDPOINT_URL.value],
                message_group_id=app.config[SQSConfig.MESSAGE_GROUP_ID.value],
            ),
        ),
    )
    transmitter = AmazonSQSFIFOPublishService()
    with timer("sqs"):
        transmitter._transmit(queue_item, None)


def init_app(_app) -> None:
    item_updated.connect(push_notification)
