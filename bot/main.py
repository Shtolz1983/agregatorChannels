import logging
import asyncio
import aioredis
from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel, UpdateChannel
from config import API_ID, API_HASH, SESSION_STRING, REDIS_HOST
from filters import check_forward_post_from_channel, check_create_new_channel, \
    check_post_from_channel_with_spam_filter

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO)

redis = aioredis.from_url(f"redis://{REDIS_HOST}", decode_responses=True)
client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)

SUBSCRIBE_CHANNELS = 'subscribe_channels'  # тип данных redis - set
CREATE_CHANNELS = 'create_channels'  # тип данных redis - set
MAPS = 'maps'  # карта соответствий подписанных каналов и созданных каналов, тип данных redis - hset
DELETE = 'del'  # карта соответствий сообщений в созданных каналах подписанным каналам из которых они пересылались,
# ключ: значение со временем жизни EXPIRED_TIME

EXPIRED_TIME = 30 * 60 * 60  # 30 минут


@client.on(events.Raw(func=check_create_new_channel))  # ловим event: создание канала пользователем
async def create_new_channel(event):
    channel_id = event.message.peer_id.channel_id  # id созданного канала
    await redis.sadd(CREATE_CHANNELS, channel_id)
    logger.info(f'CREATE_CHANNELS: {await redis.smembers(CREATE_CHANNELS)}')


@client.on(events.NewMessage(func=check_forward_post_from_channel))  # обработчик форвардных сообщений
async def manager_handler(event):
    create_channels = await redis.smembers(CREATE_CHANNELS)  # достаём из базы список созданных каналов

    if str(event.message.peer_id.channel_id) in create_channels:  # форвард только в созданные каналы
        # print(event.stringify())
        id_delete = str(event.message.peer_id.channel_id) + '_' + str(event.message.id)  # уникальное id сообщение
        res = await redis.setex(id_delete, EXPIRED_TIME, event.message.fwd_from.from_id.channel_id)
        logger.info(f'Сообщение {id_delete} внесено в базу: {bool(res)}')

        res = await redis.sadd(SUBSCRIBE_CHANNELS,
                               event.fwd_from.from_id.channel_id)  # добавляем канал в список подписок
        logger.info(f'Канал {event.fwd_from.from_id.channel_id} добавлен в подписку '
                    f'{event.message.peer_id.channel_id}: {bool(res)}')

        await redis.sadd(str(event.message.peer_id.channel_id), event.fwd_from.from_id.channel_id)  # соответствие
        # созданного канала и подписок (необходимо для последующего удаления канала)

        await redis.hset(MAPS, event.fwd_from.from_id.channel_id, event.message.peer_id.channel_id)


@client.on(events.MessageDeleted())  # обработчик позволяет удалив сообщение отписаться от канала
async def describe_handler(event):
    create_channels = await redis.smembers(name=CREATE_CHANNELS)
    if str(event.original_update.channel_id) in create_channels:  # удаление сообщение только из созданных каналов
        id_delete = str(event.original_update.channel_id) + '_' + str(event.deleted_id)  # восстанавливаем уникальное id
        # сообщения для данного канала

        channel_id = await redis.get(id_delete)  # получаем канал, который соответствует данному сообщению
        res = await redis.srem(SUBSCRIBE_CHANNELS, channel_id)  # удаляем канал из подписок

        logger.info(f'describe: {channel_id} is {bool(res)}')
        res = await redis.hdel(MAPS, channel_id)  # удаляем канал из карты соответствий
        logger.info(f'describe: {channel_id} is {bool(res)}')


@client.on(events.NewMessage(func=check_post_from_channel_with_spam_filter))  # обрабатывает все новые посты в каналах
# c учетом простой фильтрации спама по ключевым словам
async def manager_handler(event):
    subscribe_channels = await redis.smembers(name=SUBSCRIBE_CHANNELS)
    if str(event.message.peer_id.channel_id) in subscribe_channels:  # появление сообщения только в подписанных каналах

        logger.info(f'Получено сообщение из подписанного канала: {event.message.id}')
        create_channel = await redis.hget(MAPS, event.message.peer_id.channel_id)  # получаем канал
        # в который надо отправить из карты соответствия

        await asyncio.sleep(2)
        create_channel_mark = utils.get_peer_id(PeerChannel(int(create_channel)))
        res = await client.forward_messages(create_channel_mark, event.message)  # перенаправляем сообщение в канал
        logger.info(f'Cообщение: {event.message.id} отправлено в канал {create_channel}')

        await client.send_read_acknowledge(event.message.peer_id.channel_id, event.message, clear_mentions=True)  #
        # помечает сообщение в подписанном канале как прочитанное

        id_delete = str(res.peer_id.channel_id) + '_' + str(res.id)
        await redis.setex(id_delete, EXPIRED_TIME, event.message.peer_id.channel_id)


@client.on(events.Raw(func=lambda e: isinstance(e, UpdateChannel)))  # ловим event: удаление канала пользователем
async def delete_channel(event):
    create_channels = await redis.smembers(CREATE_CHANNELS)
    if str(event.channel_id) in create_channels:  # проверяем есть ли канал в списке созданных
        subscribe_channel = await redis.smembers(str(event.channel_id))  # достаем из базы
        # список подписок на удаленный канал

        res = await redis.hdel(MAPS, *subscribe_channel)  # удаляем канал из MAPS
        logger.info(f'Удаление подписок из MAPS: {res}')

        for ch in subscribe_channel:
            res = await redis.srem(SUBSCRIBE_CHANNELS, ch)  # удаляем подписки удаляемого канала из SUBSCRIBE_CHANNELS
            logger.info(f'Канал: {ch} удален SUBSCRIBE_CHANNELS: {bool(res)}')
        # diff = await redis.sdiff(SUBSCRIBE_CHANNELS, subscribe_channel)
        # res = await redis.sadd(SUBSCRIBE_CHANNELS)

        res = await redis.srem(CREATE_CHANNELS, str(event.channel_id))
        logger.info(f'Канал: {event.channel_id} удален из CREATE_CHANNELS: {bool(res)}')

with client:
    client.run_until_disconnected()
