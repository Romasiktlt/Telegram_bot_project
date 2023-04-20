from constants import stock_types
from googleapiclient.discovery import build
from constants import credentials, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME


def check(data):
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    result = service.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                         range=SAMPLE_RANGE_NAME).execute()
    sheet_data = result.get('values', [])
    if len(data) == 5:
        if data[2] != 'РТИ':
            for i in sheet_data:
                if i and data[2] == i[1] and data[1] == i[2] and data[-1] == i[7]:
                    return f'{data[3].capitalize()} типа "{data[2]}" состояния "{data[1]}" ' \
                           f'на складе {stock_types[data[-1]]} в наличии в количестве ' \
                           f'{i[3]} {i[4]}.\nВ сумме на {i[6]} рублей\nПримечания: {i[8]}'
            else:
                return f'Такого товара нет на складе {stock_types[data[-1]]} \U0001F614'
        else:
            for i in sheet_data:
                if i and data[2] == i[1]:
                    return f'РТИ типа "{data[2]}" на складе в наличии в количестве {i[3]} {i[4]}.\n' \
                           f'В сумме на {i[6]} рублей\nПримечания: {i[8]}'
            else:
                return f'Такого товара нет на складе {stock_types[data[-1]]} \U0001F614'
    else:
        sp = [data[0], data[-4], data[-3], data[-2], data[3][-1]]
        if sp[2] != 'РТИ':
            for i in sheet_data:
                if i and sp[2] == i[1] and sp[1] == i[2] and sp[-1] == i[7]:
                    return f'{sp[3].capitalize()} типа "{sp[2]}" состояния "{sp[1]}" ' \
                           f'теперь на складе {stock_types[sp[-1]]} в наличии в количестве ' \
                           f'{i[3]} {i[4]}.\nВ сумме на {i[6]} рублей\nПримечания: {data[1]}'
            else:
                return f'Такого товара нет на складе {stock_types[sp[-1]]} \U0001F614'
        else:
            for i in sheet_data:
                if i and sp[2] == i[1]:
                    return f'РТИ типа "{sp[2]}" теперь на складе {stock_types[sp[-1]]} в наличии' \
                           f' в количестве {i[3]} {i[4]}.\n' \
                           f'В сумме на {i[6]} рублей\nПримечания: {i[8]}'
            else:
                return f'Такого товара нет на складе {stock_types[sp[-1]]} \U0001F614'


def add_line(index):
    build('sheets', 'v4', credentials=credentials).spreadsheets().batchUpdate(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        body={
            'requests': [{
                'insertDimension': {
                    'range': {
                        'sheetId': '0',
                        'dimension': 'ROWS',
                        'startIndex': index,
                        'endIndex': index + 1
                    }
                }
            }]
        }
    ).execute()
