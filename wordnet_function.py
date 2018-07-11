from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer as WNL
from collections import Counter

 
from difflib import SequenceMatcher
from math import log
import re
import requests , json

#### Some ignore word
not_include_word =[
 '<unk>',
 'a',
 'an',
 'and',
 'and',
 'any',
 'are',
 'as',
 'at',
 'be',
 'begin',
 'but',
 'by',
 'every',
 'for',
 'from',
 'go',
 'he',
'she','his','her','will','who','which','where','what'
 'i',
 'in',
 'into',
 'is',
 'it',
 'its',
 'itself',
 'john',
 'jr',
 'not',
 'of',
 'often',
 'on',
 'one',
 'or',
 's',
 'so',
 'she',
 'that',
 'the',
 'their',
 'they',
 'they',
 'this',
 'to',
 'was',
 'we',
 'were',
 'when',
 'where',
 'which',
 'which',
 'with',
 'without',
 'you']

# Function to find Longest Common Sub-string
def longestSubstring(str1,str2): 
    LS = ""
    if str1 == str2:
        return True 
     # initialize SequenceMatcher object with 
     # input string
    seqMatch = SequenceMatcher(None,str1,str2)

    # find match of longest sub-string
    # output will be like Match(a=0, b=0, size=5)
    match = seqMatch.find_longest_match(0, len(str1), 0, len(str2))
     
    # print longest substring
    if (match.size!=0):
        LS = str1[match.a: match.a + match.size]
    else:
        return False

    #if (str1.startswith(LS) and str2.startswith(LS) and len(LS) >= 5) or len(LS) >= 6 or ( LS == str1 or LS == str2):
    if len(LS) >= 5:
        if str1.startswith(LS) and str2.startswith(LS):
            return True
        if str1.startswith(LS) and str2.endswith(LS):
            return True
        if str1.endswith(LS) and str2.startswith(LS):
            return True
        if str1.endswith(LS) and str2.endswith(LS):
            return True
    if  LS == str1 or LS == str2:
        return True
    return False



## only english
def stemmed(word):
    word = re.sub(r'\W+', '', word)
    
    if word != "" and word.isalpha():
        return WNL().lemmatize(WNL().lemmatize(word.lower(),pos='v'),pos='n')
    else:
        return "<unk>"

def get_synset(word,pos = 'n'):
    return [s for s in wn.synsets(word) if s.name().split(".")[1] == pos]
def get_wup_score(target_synset,held_out_word_synset):
    sense_score = Counter()
    
    if held_out_word_synset == []:
        return Counter() 
    
    for ts in target_synset:
        for hs in held_out_word_synset:
            sim_score = wn.wup_similarity(ts,hs)  
            
            if sim_score > 0.4:
                weight = sum([le.count() for le in hs.lemmas()]) 
                weight = weight if weight else 1

                sense_score[ts.name()] += sim_score * weight 
        
        #print(ts,held_out_word_synset,best_score)
    return sense_score


def get_lemmas(syn,word):
    temp = list()
    
    hyper_synsets = syn.hypernyms()
    hypo_synsets = syn.hyponyms()
    bro_synsets = syn.hypernyms()[0].hyponyms()
    target_synsets = hypo_synsets + hyper_synsets +[syn] + bro_synsets
    ## synset lemma word
    for syn in target_synsets:
        for lemma in syn.lemma_names():
            lemma = [stemmed(i) for i in lemma.split('_') if stemmed(i) not in not_include_word]   
            if word in lemma:
                lemma.remove(word)
            temp += lemma
    
    
    check_lemma = list()
    for cmw in temp:
        x = get_synset(word)
        y = get_synset(cmw)
        
        if x and y:
            t = get_wup_score(x,y).most_common()
            if t:
                top1 = [0][0]
            else:
                top1 = x[0].name()
            if top1 == syn.name():
                check_lemma += [cmw]
            
        
    check_lemma += [stemmed(i) for i in check_lemma if stemmed(i) not in not_include_word]
    return list(set(temp))



    
def match_lemma(match_word, Possible_synsets ,en_word):
    x  = Counter()
    
    match_pair = dict(dict())
    for syn in Possible_synsets:
        lemmas = sorted(get_lemmas(syn,en_word))
        for m_word,freq in match_word:
            if m_word in lemmas:
                x[syn.name()] += freq
                
    return x.most_common()



def Calculate_synsets_score(Possible_synsets,Possible_heldout,postag):
    
    wsd_score = Counter()
    
    for word in Possible_heldout:
        if word not in not_include_word:
            score = get_wup_score(Possible_synsets,get_synset(word,postag))
            wsd_score.update(score)
    
    wsd_score = wsd_score.most_common()
    
    if wsd_score != []:
        return wsd_score
    else:
        return [(Possible_synsets[0].name(),1)]
    
    
    
### Score Function
def LM_API(query):
    a = [{ "src" : query}]
    headers = {'Content-type': 'application/json'}
    r = requests.post('http://nlp-ultron.cs.nthu.edu.tw:7276/translator/translate', data = json.dumps(a) , headers=headers).json()
    possible_held_out_word = [[i['tgt'],exp(i['pred_score'])] for i in r[0] if i['tgt'].isalpha() and i['tgt'].lower() not in not_include_word ]
    
    possible_held_out_word = [[i[0],i[1]/sum([i[1] for i in possible_held_out_word])] for i in possible_held_out_word if wn.synsets(stemmed(i[0]))!=[]]
    possible_held_out_word = [i for i in sorted(possible_held_out_word,key=lambda x:x[1],reverse = True)]
    
    return possible_held_out_word


    
    
    


