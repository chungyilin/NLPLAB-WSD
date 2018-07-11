# NLPLAB-WSD


## NetWSD.py 
DB_WSD(en_word, zh_word, postag='n')
傳入 英文中文pair (plant / 植物) 以及詞性。可以得到各個sense的機率（以wordnet sunset 為 分類）
（可以直接執行，有預先找好一些中英pair）

## Synonyms_function.py :
來源與詳情:https://github.com/huyingxi/Synonyms
利用w2v找同義詞（不過是簡體，裡面有opencc簡繁互轉）

## TotalPhrasebook_function.py：
TPB的工具程式，主要是讓code簡潔與方便調用
跟原版多的地方是根據db查到的alignment把字對齊了
可以輸入中或英，查到對應


## wordnet_function.py
Wordnet工具程式，主要是讓code簡潔與方便調用
有get_synset , get_lemma , get_wup_score
