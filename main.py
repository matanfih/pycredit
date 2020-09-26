# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import glob
import json
import math


def merge_categories(x, y):
    pass


def read_execl(excel):
    df = pd.read_excel(excel)
    # df1 = pd.read_excel(excel, 'עסקאות במועד החיוב')
    # df2 = pd.read_excel(excel, 'עסקאות שאושרו וטרם נקלטו')
    # df3 = pd.read_excel(excel, 'עסקאות בחיוב מיידי')

    dfx = pd.read_excel(excel, sheet_name=None)
    # print(dfx)
    return dfx


class Currency(object):
    SHEKEL = 1
    DOLLAR = 2
    EURO = 3

    @staticmethod
    def symbol2currency(s):
        if s in '₪':
            return Currency.SHEKEL
        else:
            raise Exception("what is this carp of currency %s" % s)


class Transaction(object):
    def __init__(self, name, price, currency=Currency.SHEKEL, date=None):
        self.name = name
        self.price = price
        self.date = date
        self.currency = currency


class Category(object):
    def __init__(self, name):
        self.transactions = []
        self.name = name

    def total_sum(self):
        return sum([x.price for x in self.transactions])

    def list_names(self):
        return [x.name for x in self.transactions]

    def len(self):
        return len(self.transactions)


class ExeclMax(object):
    __ATM = 'עסקאות בחיוב מיידי'
    __credit_expenses = 'עסקאות במועד החיוב'
    __not_signed = 'עסקאות שאושרו וטרם נקלטו'

    tabs = [__ATM, __credit_expenses, __not_signed]

    first_column = 'כל המשתמשים (1)'
    _key_category = 'Unnamed: 2'
    _key_name = 'Unnamed: 1'
    _key_sum = 'Unnamed: 5'
    _key_currency = 'Unnamed: 6'

    __data_start_line = 3

    def __init__(self, excel, file_path):
        self.excel = excel
        self.file_path = file_path

        self.atm_df = self.excel[self.__ATM]
        self.credit_df = self.excel[self.__credit_expenses]
        self.not_signed_df = self.excel[self.__not_signed]

        self.category = {}

    @classmethod
    def validate(cls, excel):
        # print(excel)
        if cls.__credit_expenses not in excel:
            return False

        df = excel[cls.__credit_expenses]
        if 'max' in df[cls.first_column][0] and all(t in excel.keys() for t in cls.tabs):
            print("%s ready" % cls.__class__.__name__)
            return True
        return False

    def read_credit_expenses(self):
        categories_series = self.credit_df[self._key_category][self.__data_start_line:]
        business = self.credit_df[self._key_name][self.__data_start_line:]
        price = self.credit_df[self._key_sum][self.__data_start_line:]
        currency = self.credit_df[self._key_currency][self.__data_start_line:]
        date = self.credit_df[self.first_column][self.__data_start_line:]
        total_transaction = len(categories_series)

        for c, i in zip(categories_series, range(self.__data_start_line, total_transaction)):
            if c not in self.category:
                print("adding new category %s" % c)
                self.category[c] = Category(name=c)
            i_business = business[i]
            i_price = price[i]
            i_currency = currency[i]
            i_date = date[i]
            t = Transaction(name=i_business, price=i_price, currency=Currency.symbol2currency(i_currency), date=i_date)

            self.category[c].transactions.append(t)

        return self.category


class ExcelHtz(object):

    __data_start_line = 2

    def __init__(self, excel, file_path):
        self.excel = excel
        self.file_path = file_path

        df_key = list(self.excel.keys())[0]

        self.df = self.excel[df_key]

        self.columns = self.df.keys()
        self._key_date = self.columns[0]
        self._key_name = self.columns[1]
        self._key_sum = self.columns[3]

        self.category = {}

    @classmethod
    def validate(cls, excel):
        # print(excel)
        if len(excel.keys()) == 1 and "Transactions" in list(excel.keys())[0]:
            print("%s ready" % cls.__class__.__name__)
            return True
        return False

    def read_credit_expenses(self):
        business = self.df[self._key_name][self.__data_start_line:]
        price = self.df[self._key_sum][self.__data_start_line:]
        date = self.df[self._key_date][self.__data_start_line:]

        #categories = ['דלק חשמל וגז', 'תחבורה', 'מזון וצריכה', 'רפואה וקוסמטיקה', 'ביטוח', 'עירייה וממשלה', "ספרים והוצ' משרד", 'שונות', 'WTF']
        print(business)
        category_dict = {}
        # for c in categories:
        #     category_dict[c] = []
        with open('dictionary/htz.json', 'r+') as f:
            category_dict = json.loads(f.read())

        category_dict.items()

        # TODO move to method
        for b, i in zip(business, range(self.__data_start_line, len(business))):
            if type(b) is not str:
                continue
            chosen_category = None
            ckvs = [(k, v) for k, v in category_dict.items() if v is not None]
            for ckv in ckvs:
                category = ckv[0]
                businesses = ckv[1]
                if any(bus in b for bus in businesses):
                    print("%s is in category %s" % (b, category))
                    chosen_category = category
            if chosen_category is None:
                chosen_category = 'שונות'

            i_business = business[i]
            i_price = price[i]
            i_date = date[i]

            t = Transaction(name=i_business, price=i_price, date=i_date)
            if chosen_category not in self.category:
                self.category[chosen_category] = Category(name=chosen_category)
            self.category[chosen_category].transactions.append(t)

        return self.category

        # to_json = json.dumps(category_dict, indent=4, sort_keys=True, ensure_ascii=False)
        # with open('dictionary/htz.json', 'w') as j:
        #     j.write(to_json)

        # for c, i in zip(categories_series, range(self.__data_start_line, total_transaction)):
        #     if c not in self.category:
        #         print("adding new category %s" % c)
        #         self.category[c] = Category(name=c)
        #     i_business = business[i]
        #     i_price = price[i]
        #     i_currency = currency[i]
        #     i_date = date[i]
        #     t = Transaction(name=i_business, price=i_price, currency=Currency.symbol2currency(i_currency), date=i_date)
        #
        #     self.category[c].transactions.append(t)

        pass

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    xlsx_files = glob.glob("/home/vm/presonal_credit/*.xlsx")

    x_files = []

    for ex in xlsx_files:
        dfx = read_execl(ex)
        if ExeclMax.validate(dfx):
            x = ExeclMax(excel=dfx, file_path=ex)
            x_files.append(x)

            categories = x.read_credit_expenses()
            # print(categories.keys())
            # food = categories['מזון וצריכה']
            # print("total sum for %s is %s" % ('מזון וצריכה', food.total_sum()))
            #
            # transportation = categories['תחבורה']
            # print("total sum for %s is %s" % ('תחבורה', transportation.total_sum()))
            continue

        if ExcelHtz.validate(dfx):
            x = ExcelHtz(excel=dfx, file_path=ex)
            x_files.append(x)
            categories = x.read_credit_expenses()

            # print(categories.keys())
            # food = categories['מזון וצריכה']
            # print("total sum for %s is %s" % ('מזון וצריכה', food.total_sum()))
            #
            # transportation = categories['תחבורה']
            # print("total sum for %s is %s" % ('תחבורה', transportation.total_sum()))
            continue

    print("total food cost %s" % sum([c.category['מזון וצריכה'].total_sum() for c in x_files]))
    print("total misc cost %s" % sum([c.category['שונות'].total_sum() for c in x_files]))
    print("misc stuff: %s" % [c.category['שונות'].list_names() for c in x_files])