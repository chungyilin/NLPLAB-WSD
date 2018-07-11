# from Synonyms_function import *
from Ehowent_function import *
from time import time
import copy


def DB_WSD(en_word, zh_word, postag='n'):
    return_dict = dict()
    #### Initialize
    answer = Counter()
    Possible_synsets = [syn for syn in get_synset(en_word, postag)]
    #if sum([le.count() for le in syn.lemmas()]) != 0
    ### Find the translation
    close_meaning_en = EHownet_get_closemeaning_word(zh_word, en_word)
    if close_meaning_en == []:
        ## 拆解成字
        for w in zh_word:
            close_meaning_en += EHownet_get_closemeaning_word(w, en_word)
    # if close_meaning_en == []:
    #     close_meaning_en = get_closemeaning_word(zh_word,en_word)
        
    #### Find if word is the lemma : if so , tag it : or using the wup_similarity to score
    answer = match_lemma(close_meaning_en, Possible_synsets, en_word)
    if answer != []:
        f = 1
    else:
        f = 0
        close_meaning_en = [stemmed(word) for word, freq in close_meaning_en if  wn.synsets(word) != []]
        answer = Calculate_synsets_score(Possible_synsets, close_meaning_en, postag)
    
    answer_sum = sum([y for x,y in answer])
    answer = [(x, y/answer_sum) for x, y in answer] 
    
    return_dict['synonmys'] = close_meaning_en
    return_dict['enword'] = en_word
    return_dict['zhword'] = zh_word
    return_dict['predict'] = answer
    return_dict['predict_way'] = 'Lemmas word' if f else "Wordnet similarity"
    return return_dict

if __name__ == "__main__":
    search_pair = [('plant', '工業'), ('plant', '核電廠'), ('plant', '處理廠'), ('plant', '植物'), ('plant', '廠房'), ('plant', '廠'), ('plant', '機器'), ('plant', '裝置'),
               ('duty', '職責'), ('duty', '稅款'), ('duty', '當值'), ('duty', '責任'), ('duty', '稅率'), ('duty', '職務'), ('duty', '稅項'),
               ('taste', '品嚐'), ('taste', '趣味'), ('taste', '口味'), ('taste', '偏好'), ('taste', '味道'), ('taste', '滋味'), ('taste', '品味'),
               ('star', '巨星'), ('star', '星'), ('star', '明星'), ('star', '衛星'), ('star', '天星'), ('star', '星光'),
               ('slug', '蠕蟲'), ('slug', '軟體動物'), ('slug', '鉛彈'), ('slug', '子彈'), ('slug', '彈殼'), ('slug', '流彈'), ('slug', '彈頭'), ('slug', '霰彈'), ('slug', '鎗彈'), ('slug', '偽幣'), ('slug', '醉漢'), ('slug', '禁治產人'),
               ('bass', '鱸'), ('bass', '金目鱸'), ('bass', '低音'), ('bass', '男低音'), 
               ('bow','弓箭'), ('bow','弩'), ('bow','弓形'),('bow','拱狀'),('bow','致敬'),('bow','致')]

    for x,y in search_pair:
        r = DB_WSD(x,y)
        
        print(x,y)
        for x,y in r['predict']:
            print('\t', x, " : ", round(y, 2)*100, "% ,", wn.synset(x).definition())
        print()
    
