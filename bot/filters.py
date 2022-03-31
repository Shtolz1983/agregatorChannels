from telethon.tl.types import MessageActionChannelCreate, MessageFwdHeader, PeerChannel


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


def check_post_from_channel(event):
    try:

        return event.message.post  # and event.message.fwd_from is None
    except AttributeError:
        return False


def check_spam(event):
    spam = ['запрещенный', 'выиграй', 'удалю', 'читать продолжение',
            'joinchat', 'подписаться', 'подписывайся', 'подпишитесь',
            'переходи', 'перейти в канал', 'подписываемся', 'дамы и господа',
            'автор канала', 'как заработать' 'скачать можно тут']
    try:
        for s in spam:
            if s in event.message.message.lower():
                return False
            else:
                return True
    except AttributeError:
        return False
