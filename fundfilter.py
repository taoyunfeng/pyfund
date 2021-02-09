# -*- coding: UTF-8 -*-

all = [
    'funds_type_filter_list',
    'is_my_favorite',
    'choose_my_favorite_funds'
]

funds_type_filter_list = [
    '混合型', 'QDII', 'QDII-指数', '股票型', '股票指数'
]

def is_my_favorite(fund):
    fundname, fundcode, networth = fund
    worthset = [networth[i]['y'] for i in range(len(networth))]
    if len(worthset) < 10:
        return False

    start_worth = worthset[0]
    end_worth = worthset[-1]
    total_increment = (end_worth - start_worth) * 100 / len(networth)
    if total_increment < 0:
        return False

    increment_array = []
    for index, value in enumerate(worthset[-10:]):
        if index != 0:
            increment_array.append(value - worthset[index - 1])

    if len(list(filter(lambda x: x < 0, increment_array[-6:]))) < 3:
        return False

    dec_days = 0
    worthset = worthset[-10:]
    worthset.reverse()
    reversed_worthset = worthset
    
    for index, value in enumerate(reversed_worthset):
        if index == len(reversed_worthset) - 1:
            break
        
        if value <= reversed_worthset[index + 1]:
            dec_days = dec_days + 1
            
    if reversed_worthset[0] < reversed_worthset[-1] and dec_days >= 6:
        return True

    return False

def choose_my_favorite_funds(funds_list:list):
    return list(filter(is_my_favorite, funds_list))