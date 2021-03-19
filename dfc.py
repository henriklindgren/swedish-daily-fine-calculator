#!/usr/bin/env python3
"""
This is just a quick hack for fun, don't trust the calculations. If you are older than 65 you are allowed larger tax
 breaks and as such will have a higher lower tax layer.

Calculations based on
https://lagen.nu/1962:700#K25P2
https://www.advokatsamfundet.se/globalassets/advokatsamfundet_sv/nyheter/rar-2007_2.pdf
https://www.skatteverket.se/privat/etjansterochblanketter/svarpavanligafragor/inkomstavtjanst/privattjansteinkomsterfaq/narskamanbetalastatliginkomstskattochhurhogarden.5.10010ec103545f243e8000166.html

LICENSE
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""

# from 2020 and forward the upper tax layer is not in play (would had been 5% reduction on values above it)
import sys

YEARLY_LOWER_TAX_LAYER = {
    2021: 523200,
    2020: 509300,
}
LOWER_TAX_LAYER_PERCENTAGE = 0.8

BASE_BALANCE_THRESHOLD = 1500000
BASE_BALANCE_MODIFIER = 50
COMPLEMENTARY_BALANCE_THRESHOLD = 500000
COMPLEMENTARY_BALANCE_MODIFIER = 50

MINIMUM_DAYS = 30
MAXIMUM_DAYS = 150
MINIMUM_DAY_FEE = 50
MAXIMUM_DAY_FEE = 1000


def calculate_balance_modifier_fee(balance: int):
    complementary_fee = 0
    if balance < BASE_BALANCE_THRESHOLD:
        return complementary_fee
    remaining_balance = balance - BASE_BALANCE_THRESHOLD
    complementary_fee += BASE_BALANCE_MODIFIER
    while (remaining_balance := remaining_balance - COMPLEMENTARY_BALANCE_THRESHOLD) > COMPLEMENTARY_BALANCE_THRESHOLD:
        complementary_fee += COMPLEMENTARY_BALANCE_MODIFIER
    return complementary_fee


def calculate_fee(year: int, gross_income: int, balance: int):
    lower_tax = YEARLY_LOWER_TAX_LAYER[year]
    if lower_tax > gross_income:
        # if gross income is larger than lower tax layer, deduct 20% off of top part.
        full_value = lower_tax + ((lower_tax - gross_income) * LOWER_TAX_LAYER_PERCENTAGE)
    else:
        full_value = gross_income

    day_fee = full_value / 1000
    if balance >= 0:
        # if balance is asset
        day_fee += calculate_balance_modifier_fee(balance)
    else:
        # if balance is debt
        day_fee -= calculate_balance_modifier_fee(balance)

    if day_fee < MINIMUM_DAY_FEE:
        return MINIMUM_DAY_FEE
    elif day_fee > MAXIMUM_DAY_FEE:
        return MAXIMUM_DAY_FEE

    return day_fee


if __name__ == '__main__':
    try:
        year, gross_income, balance, penalty_days = sys.argv[1:]
        year = int(year)
        gross_income = int(gross_income)
        balance = int(balance)
        penalty_days = int(penalty_days)
    except ValueError:
        print('Usage: \n dfc.py <year> <gross_income> <balance> <penalty_days>')
        sys.exit(1)

    day_fee = calculate_fee(year=year, gross_income=gross_income, balance=balance)
    print(
        f'Daily fine: {day_fee} kr. Fine will be between: {day_fee * MINIMUM_DAYS} kr and {day_fee * MAXIMUM_DAYS} kr'
    )
    print(f'If convicted to {penalty_days} days the sum would be {penalty_days * day_fee} kr.')
