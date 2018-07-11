
from TotalPhrasebook_function import *
import opencc 
import synonyms
import copy

def simplify(text):
    return opencc.convert(text)

def traditionalize(text):
    return opencc.convert(text, config='s2t.json')

def get_synonyms(zh):
    simple = simplify(zh)

    simple_synonyms = synonyms.nearby(simple)[0]
    traditional_synonyms = [ traditionalize(i) for i in simple_synonyms]
    return traditional_synonyms


## 使用簡體詞林擴增同義詞
def get_closemeaning_word(zh_word,en_word):
    
    synonyms_cahe = dict()
    search_cache = dict()
    
    close_meaning_en = Counter()
    check_en = list()
    close_meaning_zh = [zh_word]
    for _ in range(10): 
        
        check_en = copy.copy(close_meaning_en)
        ## first tanslate.: zh2en
        for w in close_meaning_zh:
            if w in search_cache:
                search_result = search_cache[w]
            else:
                search_cache[w] = [ stemmed(word) for word in translation_search(w,'zh2en') 
                                                                 if stemmed(word) != en_word and 
                                                                    stemmed(word) not in not_include_word]
                search_result = search_cache[w]
            close_meaning_en.update(search_result)
            
        ## second translate.: en2zh
        for w,freq in close_meaning_en.most_common()[:50]:
            if w in search_cache:
                search_result = search_cache[w]
            else:
                search_cache[w] =[ word for word in translation_search(w,'en2zh',sampleNum= 3)]
                search_result =  search_cache[w]
            close_meaning_zh += search_result
            
        for zh in close_meaning_zh:
            if zh in synonyms_cahe:
                synonmys_words = synonyms_cahe[zh]
            else:
                synonyms_cahe[zh] = [stemmed(synonyms) for synonyms in get_synonyms(zh) 
                                       if stemmed(synonyms) not in close_meaning_zh]
                synonmys_words = synonyms_cahe[zh]
           
            if len(close_meaning_zh)<50:
                close_meaning_zh += synonmys_words
            else:
                break 
        if check_en == close_meaning_en:
            break 
    
    return close_meaning_en.most_common()[:50]
