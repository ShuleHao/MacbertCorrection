# -*- coding: utf-8 -*-
# Author: XuMing(xuming624@qq.com)
# Brief: 汉字处理的工具:判断unicode是否是汉字，数字，英文，或者其他字符。以及全角符号转半角符号。
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re

import pypinyin
import six
from pypinyin import pinyin

from utils.langconv import Converter


def convert_to_unicode(text):
    """Converts `text` to Unicode (if it's not already), assuming utf-8 input."""
    if six.PY3:
        if isinstance(text, str):
            return text
        elif isinstance(text, bytes):
            return text.decode("utf-8", "ignore")
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    elif six.PY2:
        if isinstance(text, str):
            return text.decode("utf-8", "ignore")
        elif isinstance(text, unicode):
            return text
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    else:
        raise ValueError("Not running on Python2 or Python 3?")


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    return '\u4e00' <= uchar <= '\u9fa5'


def is_chinese_string(string):
    """判断是否全为汉字"""
    return all(is_chinese(c) for c in string)


def is_number(uchar):
    """判断一个unicode是否是数字"""
    return '\u0030' <= uchar <= '\u0039'


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    return '\u0041' <= uchar <= '\u005a' or '\u0061' <= uchar <= '\u007a'


def is_alphabet_string(string):
    """判断是否全部为英文字母"""
    return all(is_alphabet(c) for c in string)


def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    return not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar))


def B2Q(uchar):
    """半角转全角"""
    inside_code = ord(uchar)
    if inside_code < 0x0020 or inside_code > 0x7e:  # 不是半角字符就返回原来的字符
        return uchar
    if inside_code == 0x0020:  # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return chr(inside_code)


def Q2B(uchar):
    """全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)


def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])


def uniform(ustring):
    """格式化字符串，完成全角转半角，大写转小写的工作"""
    return stringQ2B(ustring).lower()


def remove_punctuation(strs):
    """
    去除标点符号
    :param strs:
    :return:
    """
    return re.sub("[\s+\.\!\/<>“”,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "", strs.strip())


def traditional2simplified(sentence):
    """
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    """
    return Converter('zh-hans').convert(sentence)


def simplified2traditional(sentence):
    """
    将sentence中的简体字转为繁体字
    :param sentence: 待转换的句子
    :return: 将句子中简体字转换为繁体字之后的句子
    """
    return Converter('zh-hant').convert(sentence)


def get_homophones_by_char(input_char):
    """
    根据汉字取同音字
    :param input_char:
    :return:
    """
    result = []
    # CJK统一汉字区的范围是0x4E00-0x9FA5,也就是我们经常提到的20902个汉字
    for i in range(0x4e00, 0x9fa6):
        if pinyin([chr(i)], style=pypinyin.NORMAL)[0][0] == pinyin(input_char, style=pypinyin.NORMAL)[0][0]:
            result.append(chr(i))
    return result


def get_homophones_by_pinyin(input_pinyin):
    """
    根据拼音取同音字
    :param input_pinyin:
    :return:
    """
    result = []
    # CJK统一汉字区的范围是0x4E00-0x9FA5,也就是我们经常提到的20902个汉字
    for i in range(0x4e00, 0x9fa6):
        if pinyin([chr(i)], style=pypinyin.TONE2)[0][0] == input_pinyin:
            # TONE2: 中zho1ng
            result.append(chr(i))
    return result


if __name__ == "__main__":
    a = 'nihao'
    print(a, is_alphabet_string(a))
    # test Q2B and B2Q
    for i in range(0x0020, 0x007F):
        print(Q2B(B2Q(chr(i))), B2Q(chr(i)))
    # test uniform
    ustring = '中国 人名ａ高频Ａ  扇'
    ustring = uniform(ustring)
    print(ustring)
    print(is_other(','))
    print(uniform('你干么！ｄ７＆８８８学英 语ＡＢＣ？ｎｚ'))
    print(is_chinese('喜'))
    print(is_chinese_string('喜,'))
    print(is_chinese_string('丽，'))

    traditional_sentence = '憂郁的臺灣烏龜'
    simplified_sentence = traditional2simplified(traditional_sentence)
    print(traditional_sentence, simplified_sentence)
    print(is_alphabet_string('Teacher'))
    print(is_alphabet_string('Teacher '))
