SPAM = [
        'запрещенный', 'выиграй', 'удалю', 'читать продолжение',
        'joinchat', 'подписаться', 'подписывайся', 'подпишитесь',
        'переходи', 'перейти в канал', 'подписываемся', 'дамы и господа',
        'автор канала', 'как заработать', 'скачать можно тут', '#реклама'
        'реклама'
        ]


def check_spam(event):
    try:
        for s in SPAM:
            if s in event.message.message.lower():
                return False
            else:
                return True
    except AttributeError:
        return False
