import gspread
from oauth2client.service_account import ServiceAccountCredentials

import datetime
import tempfile
import os
import requests

from collections import Counter

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client =  gspread.authorize(creds)

#### SHEETS ####
def get_curr_month_sheet():
    now = datetime.datetime.now()
    sheet_name = now.strftime("%m-%Y")

    try:
        worksheet = client.open("SalesBot").worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = client.open("SalesBot").add_worksheet(title=sheet_name, rows="1000", cols="20")
        worksheet.append_row(["Дата", "Время", "Товар", "Цена", "User ID", "Имя"])

    return worksheet

def get_sheet_by_date(date_str):
    date = datetime.datetime.strptime(date_str, "%d.%m.%y")
    sheet_name = date.strftime("%m-%Y")

    try:
        worksheet = client.open("SalesBot").worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        return None
    
    return worksheet

def get_sheet_by_month(month_str):
    date = datetime.datetime.strptime(month_str, "%m.%y")
    sheet_name = date.strftime("%m-%Y")

    try:
        worksheet = client.open("SalesBot").worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        return None
    
    return worksheet

#### ACTIONS ####

def add_sale(date, time, product, price, user_id, name):
    sheet = get_curr_month_sheet()
    sheet.append_row([date, time, product, price, user_id, name])
    
def remove_last_user_sale(user_id):
    sheet = get_curr_month_sheet()
    data = sheet.get_all_values()
    for i in range(len(data) - 1, 0, -1):
        row = data[i]
        if row[4] == str(user_id):
            sheet.delete_rows(i + 1)
            return True
    return False

def get_report(date):
    sheet = get_sheet_by_date(date)
    if not sheet:
        return 0, 0
    
    data = sheet.get_all_values()
    rows = data[1:] 

    sales = 0
    amount = 0
    for row in rows:
        if row[0] == date:
            try:
                sales += 1
                amount += float(row[3].replace(",", "."))
            except:
                continue
    return sales, amount

def get_month_summary(month_str):
    sheet = get_sheet_by_month(month_str)
    if not sheet:
        return 0, 0
    
    data = sheet.get_all_values()
    rows = data[1:]

    sales = 0
    amount = 0
    for row in rows:
        try:
            sales += 1
            amount += float(row[3].replace(",", "."))
        except:
            continue
    return sales, amount
    
def get_year_summary(year_str):
    sheet = client.open("SalesBot")
    worksheets = sheet.worksheets()

    sales = 0
    amount = 0
    for ws in worksheets:
        if ws.title.endswith(f"-{year_str}"):
            rows = ws.get_all_values()[1:]

            for row in rows:
                try:
                    sales += 1
                    amount += float(row[3].replace(",", "."))
                except:
                    continue
    return sales, amount

def get_top_products(month_str=None):
    if month_str is None:
        sheet = get_curr_month_sheet()
    else:
        sheet = get_sheet_by_month(month_str)
        if sheet is None:
            return None
    
    data = sheet.get_all_values()[1:]
    products = [row[2] for row in data if len(row) > 2]

    counter = Counter(products)
    top = counter.most_common(10)

    return top
    

#### EXPORT ####

def export_sheet_xlsx():
    sheet = client.open("SalesBot")
    sheet_id = sheet.id

    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    headers = {
        "Authorization": f"Bearer {creds.get_access_token().access_token}"
    }

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    response = requests.get(export_url, headers=headers)

    if response.status_code == 200:
        tmp_file.write(response.content)
        tmp_file.close()
        return tmp_file.name
    else:
        tmp_file.close()
        os.unlink(tmp_file.name)
        return None
    