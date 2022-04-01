from telethon.tl.types import MessageActionChannelCreate, MessageFwdHeader, PeerChannel
from .spam_filter import check_spam


def check_create_new_channel(event):
    try:
        return isinstance(event.message.action, MessageActionChannelCreate)
    except AttributeError:
        return False


def check_forward_post_from_channel(event):
    try:
        res = isinstance(event.message.fwd_from, MessageFwdHeader) \
              and isinstance(event.message.peer_id, PeerChannel)
        return res
    except AttributeError:
        return False


def check_post_from_channel_with_spam_filter(event):
    try:
        return event.message.post and check_spam(event)   # and event.message.fwd_from is None
    except AttributeError:
        return False

