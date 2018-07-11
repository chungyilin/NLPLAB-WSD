from EHowNetAPI.ehownet import *
from TotalPhrasebook_function import *
from collections import Counter
import copy
tree=EHowNetTree("./EHowNetAPI/db/ehownet_ontology.sqlite")



## 使用Ehownet 擴增同義詞
def EHownet_getword(word):
    zh_list = list()
    en_list = list()
   

    for r in tree.searchWord(word):
        catagory = r.getSemanticTypeList()[0]
        catagory = catagory.data['label']
        for sb in r.getDescendantWordList():
        #for sb in r.getSiblingWordList():
            if catagory in sb.data['ehownet']:
                zh_list += [sb.data['word']]
                en_list += [stemmed(i) for i in sb.data['meaning'].replace(',',' ').replace(', ',' ').split(' ')  if stemmed(i) not in not_include_word]
                
                
    return list(set(zh_list)) , list(set(en_list))


def EHownet_get_closemeaning_word(zh_word,en_word):
    close_meaning_en = Counter()
    check_en = list()
    close_meaning_zh = list()
    
    Ehownet_cahe = dict()
    search_cache = dict()
    
    zh,en = EHownet_getword(zh_word)
    close_meaning_zh += zh
    close_meaning_en.update([stemmed(e) for e in en 
                                        if stemmed(e)!=en_word and 
                                           stemmed(e) not in not_include_word])
    
    
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
                search_cache[w] = [ stemmed(word) for word in translation_search(w,'en2zh',sampleNum= 3)]
                search_result = search_cache[w]
            close_meaning_zh += search_result
        
        for zh in close_meaning_zh:    
            if zh in Ehownet_cahe:
                ehownet_zh,ehownet_en = Ehownet_cahe[w]
            else:
                ehownet_zh,ehownet_en = EHownet_getword(zh) 
                ehownet_en =  [ stemmed(word) for word in ehownet_en
                                              if stemmed(word) != en_word and 
                                                 stemmed(word) not in not_include_word]
                Ehownet_cahe[w] = (ehownet_zh,ehownet_en)
            
            close_meaning_en.update(ehownet_en)
            
            if len(close_meaning_zh)<50:
                close_meaning_zh += ehownet_zh
            else:
                break 
        if check_en == close_meaning_en:
            break 
    
    return close_meaning_en.most_common()[:50]
