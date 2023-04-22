from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from googleapiclient.discovery import build
import datetime as dt
from constants import credentials, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME
from constants import start_list, wtd, kinds
from definitions import check, add_line


bot = Bot(token='6012637787:AAE66KEJm5p1KnOAAt4v5pBbFjfDpmrmYs0')
dp = Dispatcher(bot)
final_data = ''


@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    but_check = types.InlineKeyboardButton(text='Просмотреть наличие', callback_data='check')
    but_incoming = types.InlineKeyboardButton(text='Отметить приход', callback_data='incoming')
    but_outgo = types.InlineKeyboardButton(text='Отметить расход', callback_data='outgo')
    keyboard_markup.add(but_check)
    keyboard_markup.add(but_incoming)
    keyboard_markup.add(but_outgo)
    await message.answer('Здравствуйте!\nЧто вы хотите сделать?',
                         reply_markup=keyboard_markup)


@dp.callback_query_handler(text=['check', 'incoming', 'outgo'])
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    typs = ['рельсы', 'метизы', 'накладки', 'подкладки', 'РТИ', 'АРС', 'ЖБР',
            'шпала', 'стрелки', 'клеммы прочие', 'хомуты к лесам']
    answer_data = query.data
    cb = '_' + answer_data
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    for typ in typs:
        keyboard_markup.add(types.InlineKeyboardButton(text=typ.upper(), callback_data=typ + cb))
    await bot.send_message(query.from_user.id, 'Какой тип вы хотите выбрать?',
                           reply_markup=keyboard_markup)
    await query.answer(wtd[query.data.split('_')[0]], show_alert=True)


@dp.callback_query_handler(Text(startswith=['рельсы', 'метизы', 'накладки', 'подкладки', 'РТИ', 'АРС',
                                            'ЖБР', 'шпала', 'стрелки', 'клеммы прочие', 'хомуты к лесам']))
async def answer_callback_handler(query: types.CallbackQuery):
    cb = '_' + query.data
    typ = query.data.split('_')[0]
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    for i in kinds[typ]:
        keyboard_markup.add(types.InlineKeyboardButton(text=i, callback_data=i + cb))
    await bot.send_message(query.from_user.id, 'Виберите вид',
                           reply_markup=keyboard_markup)
    await query.answer(query.data.split('_')[0], show_alert=True)


@dp.callback_query_handler(Text(startswith=start_list))
async def answer_cb_handler(query: types.CallbackQuery):
    cb = '_' + query.data
    typ = query.data.split('_')[1]
    kb_markup = types.InlineKeyboardMarkup(row_width=3)
    kb_markup.add(types.InlineKeyboardButton(text='нов', callback_data='нов' + cb))
    if typ != 'РТИ':
        if typ == 'рельсы' or typ == 'стрелки':
            cond = ['хр', 'вс', 'бу00', 'бу01', 'бу1гр', 'бу2гр',
                    'хрнд', 'бунд', 'бок', 'гнутг', 'гнутв']
        else:
            cond = ['хр', 'вс', 'бу']
        for i in cond:
            kb_markup.add(types.InlineKeyboardButton(text=i, callback_data=i + cb))
    await bot.send_message(query.from_user.id, 'Состояние',
                           reply_markup=kb_markup)
    await query.answer(query.data.split('_')[0], show_alert=True)


@dp.callback_query_handler(Text(startswith=['нов', 'хр', 'вс', 'бу', 'бок', 'гн',
                                            '328', '143', '74', '366', '362', '487', '153']))
async def location(query: types.CallbackQuery):
    cb = '_' + query.data
    kb = types.InlineKeyboardMarkup(row_width=2)
    if cb.endswith('_check'):
        cb = 'check' + '_'.join(cb.split('_')[0:-1]) + '_'
        kb.add(types.InlineKeyboardButton(text='Автозаводском', callback_data=cb + 'райА'))
        kb.add(types.InlineKeyboardButton(text='Центральном', callback_data=cb + 'райЦ'))
    else:
        kb.add(types.InlineKeyboardButton(text='Автозаводском', callback_data='райА' + cb))
        kb.add(types.InlineKeyboardButton(text='Центральном', callback_data='райЦ' + cb))
    await bot.send_message(query.from_user.id, 'На складе в ... районе',
                           reply_markup=kb)
    await query.answer(query.data.split('_')[0], show_alert=True)


@dp.callback_query_handler(Text(startswith=['райА', 'райЦ']))
async def amount_answer_cb_handler(query: types.CallbackQuery):
    stock_types = {'райА': 'Автозаводский район',
                   'райЦ': 'Центральный район'}
    cb = '_' + query.data
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(text='тонны', callback_data='т' + cb))
    kb.add(types.InlineKeyboardButton(text='штуки', callback_data='шт' + cb))
    await bot.send_message(query.from_user.id, 'Единицы измерения',
                           reply_markup=kb)
    await query.answer(stock_types[query.data.split('_')[0]], show_alert=True)


@dp.callback_query_handler(Text(startswith=['т', 'шт']))
async def the_end(query: types.CallbackQuery):
    cb = query.data
    global final_data
    final_data = cb
    await bot.send_message(query.from_user.id,
                           f'Количество и примечания:\n'
                           f'(Количество на первой, '
                           f'примечания писать на следующей строке, '
                           f'если их нет, написать только количество.)')
    await query.answer(query.data.split('_')[0], show_alert=True)


@dp.message_handler()
async def final(message: types.Message):
    txt = message.text.split('\n')
    if len(txt) == 1:
        txt.append(None)
    cb = txt + final_data.split('_')
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    result = service.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                         range=SAMPLE_RANGE_NAME).execute()
    sheet_data = result.get('values', [])
    cb[3] = cb[3][-1]
    for i in sheet_data:
        if i and i[1] == cb[-3] and i[2] == cb[-4] and i[7] == cb[3]:
            if cb[-1] == 'outgo':
                x = sheet_data.index(i)
                range_ = 'Лист1!A' + str(x + 1) + ':J' + str(x + 1)
                if cb[1]:
                    cb[1] = i[8] + cb[1] + '; '
                arr = {'values': [[None, None, None,
                                   float(i[3].replace(',', '.')) - float(cb[0].replace(',', '.')),
                                   None, None, None, cb[3], cb[1],
                                   dt.datetime.now().strftime('%H:%M %d.%m.%y')]]}
                response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_,
                                          valueInputOption='USER_ENTERED', body=arr).execute()
                await bot.send_message(message.from_user.id, check(cb))
                break
            x = sheet_data.index(i)
            range_ = 'Лист1!A' + str(x + 1) + ':J' + str(x + 1)
            if cb[1]:
                cb[1] = i[7] + cb[1] + '; '
            arr = {'values': [[None, None, None,
                               float(i[3].replace(',', '.')) + float(cb[0].replace(',', '.')),
                               None, None, None, cb[3], cb[1],
                               dt.datetime.now().strftime('%H:%M %d.%m.%y')]]}
            response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_,
                                      valueInputOption='USER_ENTERED', body=arr).execute()
            await bot.send_message(message.from_user.id, check(cb))
            break
    else:
        if cb[-1] == 'incoming':
            flag = False
            for i in range(len(sheet_data)):
                if sheet_data[i][0] and sheet_data[i][0] != cb[-2] and flag:
                    add_line(i - 2)
                    range_ = 'Лист1!A' + str(i - 1) + ':J' + str(i - 1)
                    arr = {'values': [[None, cb[-3], cb[-4],
                                       float(cb[0]),
                                       cb[2], None, None, cb[3], cb[1],
                                       dt.datetime.now().strftime('%H:%M %d.%m.%y')]]}
                    service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_,
                                   valueInputOption='USER_ENTERED', body=arr).execute()
                    break
                if sheet_data[i][0].lower() == cb[-2].lower():
                    flag = True
        await message.answer(check(cb))


@dp.callback_query_handler(Text(startswith='check_'))
async def checking(query: types.CallbackQuery):
    cb = query.data
    fdt = cb.split('_')
    fdt[-1] = fdt[-1][-1]
    await bot.send_message(query.from_user.id, check(fdt))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
