import os

import pandas
import json
import re


# 指定文件名，指定 key, value 名，读取字典
def inquiry_single_key_value(filepath, key_col, value_col) -> dict:
    db = pandas.read_csv(filepath, sep='\t')
    dic = {}
    for key, value in zip(db[key_col], db[value_col]):
        if str(key) == 'nan':
            continue
        if str(value) == 'nan':
            value = "文件\"{}\"中没有\"{}[{}]\"对应的\"{}\"信息".format(filepath, key_col, key, value_col)
        dic[key] = value
    return dic


# 指定文件名，指定 key, value 名，读取字典。
# key_col：支持使用 | 分开多个列名。比如 a_col|b_col。查询结果会被合并
def inquiry_key_value(filepath: str, key_col: str, value_col: str) -> dict:
    if '|' not in key_col:
        return inquiry_single_key_value(filepath, key_col, value_col)

    dic = {}
    for key in key_col.split('|'):
        result_dic = inquiry_single_key_value(filepath, key, value_col)
        dic.update(result_dic)
    return dic


# 对“机构（属性信息）.csv”单独处理
def inquiry_institution_attribute(filepath, key_col, value_col):
    if '|' not in key_col:
        return inquiry_single_key_value(filepath, key_col, value_col)

    dic = {}
    for key in key_col.split('|'):
        result_dic = inquiry_single_key_value(filepath, key, value_col)
        if not key == "别称":
            dic.update(result_dic)
        # 别称中使用 '；'分割多个别称，需要将字典的key分成多个，呃呃呃呃
        else:
            temp_dic = {}
            for k, v in result_dic.items():
                for sub_k in re.split('[;；]', k):
                    temp_dic[sub_k] = v
            dic.update(temp_dic)

    return dic


if __name__ == '__main__':
    filename = "../qa_database/人.csv"
    key_name = '姓名'
    value_name = '办公地点'

    # dic = inquiry_single_key_value(filename, '姓名', '办公地点')
    # for k, v in dic.items():
    #     print(k)
    #     print('\t', v)

    filename = "../qa_database/机构（属性信息）.csv"
    key_name = '机构名|别称'
    value_name = '特色文化'

    dic = inquiry_key_value(filename, key_name, value_name)
    for k, v in dic.items():
        print(k)
        print('\t', v)

    print('-------------------')

    dic = inquiry_institution_attribute(filename, key_name, value_name)
    for k, v in dic.items():
        print(k)
        print('\t', v)
