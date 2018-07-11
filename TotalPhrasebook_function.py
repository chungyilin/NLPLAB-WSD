from flask import Flask, Response, jsonify, request, render_template
from collections import defaultdict
import re
import os
import sqlite3
import string

from wordnet_function import *
#### Some ignore word


PROJECT_DIR = '/home/yee0/TotalPhraseBook/phrasebook'
pch = re.compile(u"^[\u4E00-\u9FA5 *,\d]+$")



def isChinese(s):
    if pch.findall(s) == []:
        return False
    else:
        return True


def sqlite_query(sqlcmd, params=None, db_path=''):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sqlcmd, params)
        for row in cursor:
            yield row


def gen_condition(query, operator):
    conditions = []
    params = (query.strip(), )
    if "," in query:
        ch, en = [item.strip() for item in query.split(',', 1)]
        conditions.append("cphrasekey {} ?".format(operator))
        conditions.append("ephrase {} ?".format(operator))
        params = (ch, en)
    else:
        if isChinese(query.replace("%", "")):
            conditions.append("cphrasekey {} ?".format(operator))
        else:
            conditions.append("ephrase {} ?".format(operator))
    return ' and '.join(conditions), params


def get_phrase(query, offset=0,sampleNum=8):
    db_path = os.path.join(PROJECT_DIR, 'phrase_table.db')
    operator = 'like' if "%" in query else '='
    condition, params = gen_condition(query, operator)
    sqlcmd = "select * from phrase_table where {} order by min(pec, pce) desc limit {} offset {};".format(condition,sampleNum,offset)
    result = [row for row in sqlite_query(sqlcmd, params, db_path)]
    return result


def get_sentence(ch, en):
    db_path = os.path.join(PROJECT_DIR, 'hkpt.alg.db')
    #sqlcmd = "select * from alignment where ' ' || chsent || ' ' like '% ' || ? || ' %' and ' ' || ensent || ' ' like '% ' || ? || ' %' limit 8;"
    sqlcmd = "select * from alignment where ' ' || chsent || ' ' like '% ' || ? || ' %' and ' ' || ensent || ' ' like '% ' || ? || ' %';"
    result = [row for row in sqlite_query(sqlcmd,  (ch, en), db_path)]
    return result


def alignment(zh,en,cealign,ecalign):
    zh = zh.split()
    en = en.split()
    zh2en = list()
    en2zh = list()
    
    cealign = cealign.split(' ')
    for key,i in enumerate(cealign):
        cealign[key] = [int(w) if w != "" else "" for w in i.strip(string.punctuation).split(",")]
    ecalign = ecalign.split(' ')
    for key,i in enumerate(ecalign):
        ecalign[key] = [int(w) if w != "" else "" for w in i.strip(string.punctuation).split(",")]
    
    
    for word_align in cealign:
        zh2en += [en[index] if index != "" else "" for index in word_align]
    for word_align in ecalign:
        en2zh += [zh[index] if index != "" else "" for index in word_align]
    
    
    zh2en , en2zh = list(set(zh2en)) ,list(set(en2zh))
        
    zh_return = [ i for i in zh if i in en2zh]
    en_return = [ i for i in en if i in zh2en]
    
    return  en_return ,zh_return

def sentence_alignment(r):

    zh = r[0].split()
    en = r[1].split()
    
    en2zh = defaultdict(lambda :[])
    zh2en = defaultdict(lambda :[])
    for pair in r[2].split():
        zhindex , enindex =  [int(x) for x in pair.split('-')]
        en2zh[en[enindex]] += [zh[zhindex]]
        zh2en[zh[zhindex]] += [en[enindex]]
#     list(map(print,[(en,en2zh[en]) for en in en2zh]))
#     list(map(print,[(zh,zh2en[zh]) for zh in zh2en]))
    return en2zh,zh2en
    



def translation_search(word,search_way,sampleNum = 8):
    if search_way != 'en2zh' and search_way != 'zh2en':
        print("choice a translation type on ",word)
        return False
    ## Translate from en2zh or zh2en
    results = get_phrase(word, 0 ,sampleNum)
    
    if results == []:
        #print("Cann't be find in the DB : ",word)
        return []
    
    target = list()
    for r in results:
        zh,en,cealign,ecalign,probce,_,probec = r[0:7]
        zh2en,en2zh = alignment(zh,en,cealign,ecalign)
        if search_way == 'en2zh':
            target += en2zh 
        if search_way == 'zh2en':
            target += zh2en
    return list(set([i for i in target if i not in not_include_word]))