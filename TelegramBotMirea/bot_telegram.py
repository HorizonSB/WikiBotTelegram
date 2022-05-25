from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio, aioschedule

import wikipedia, re, os

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)
wikipedia.set_lang("ru")
chat_id = ''
GREETING = (
    '\nЯ телеграм-бот, который умеет искать статьи в Википедии. '
    '\nПросто отправьте фразу, и я постараюсь что-нибудь найти.'
    '\nТакже я буду отправлять вам по одному факту из истроии каждый день.'
)


async def on_startup(_):
    print('Бот работает')
    asyncio.create_task(scheduler())


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    try:
        await message.answer(message.from_user, GREETING)
        await message.delete()
    except Exception as e:
        print(e)
        await message.answer(GREETING)


@dp.message_handler(content_types=["photo"])
async def send_photo(message: types.Message):
    await message.answer('Не отправляйте сюда фотографии, пожалуйста')


@dp.message_handler(commands=['Факт дня'])
async def wiki_command(message: types.Message):
    await message.answer("Факт дня: ")


@dp.callback_query_handler(lambda query: query.data.startswith("title_"))
async def ans(call: types.CallbackQuery):
    try:
        chat_id = call.message.chat.id
        title = call.data.split("_")[1]
        inline_btn_1 = InlineKeyboardButton('Читать всю статью', callback_data=f'button1_{title}')
        arcticlekeybord = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
        print(wikipedia.page(title).images)
        await bot.send_photo(chat_id, photo=wikipedia.page(title).images[0])
        await call.answer(show_alert=False, cache_time=3)
        await call.message.answer(getwiki(title), reply_markup=arcticlekeybord)
    except Exception as e:
        print(e)
        await call.message.answer("Не удалось загрузить статью")


@dp.callback_query_handler(lambda query: query.data.startswith("button1_"))
async def process_callback_button1(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    title = call.data.split("_")[1]
    await call.message.answer(
        'Для более подробного ознакомления со статьей перейдите по ссылке: ' + wikipedia.page(title).url)


@dp.message_handler()
async def echo_send(message: types.Message):
    try:
        keyboard = InlineKeyboardMarkup(row_width=4)
        word = str(wikipedia.search(message.text, results=4)).split(", '")
        print(wikipedia.search(message.text, results=4))
        for i in range(0, len(word)):
            word[i] = word[i].replace('[', ' ').replace(']', ' ').replace("'", " ")
            keyboard.add(InlineKeyboardButton(word[i], callback_data=f"title_{word[i]}"))
        await message.answer('Выберите наиболее подходящий заголовок: ', reply_markup=keyboard)
    except Exception as e:
        await message.answer('В википедии нет статьи на данную тему')
        print(e)


async def everyday_fact():
    await bot.send_message(chat_id, 'Факт дня: ')


def getwiki(text):
    ny = wikipedia.page(text)
    wikitext = ny.content[:1000]
    wikimas = wikitext.split('.')
    wikimas = wikimas[:-1]
    wikitext2 = ''
    for x in wikimas:
        if not ('==' in x):
            if (len((x.strip())) > 3):
                wikitext2 = wikitext2 + x + '.'
        else:
            break
    wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
    wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
    wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)

    return wikitext2


async def scheduler():
    aioschedule.every().day.at("15:00").do(everyday_fact)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
