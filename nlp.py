# Credit to Assoc.Prof. Wirote Aroonmanakun (Ph.D.)
# Director, The Siridhorn Thai Language Institute, Chulalongkorn University
# Orignal code from https://github.com/attapol/tltk/blob/master/tltk/nlp.py
# http://pioneer.chula.ac.th/~awirote/resources/thai-romanization.html

#########################################################
## Thai Language Toolkit : version  1.1.7
## Chulalongkorn University
## word_segmentation, syl_segementation written by Wirote Aroonmanakun
## Implemented :
##      chunk, ner_tag, segment, word_segment, syl_segment, word_segment_mm, word_segment_nbest,
##      g2p, th2roman, pos_tag_wordlist, 
##      read_thaidict, reset_thaidict, check_thaidict
##      spell_candidates,
#########################################################
import re
import math
import os
from copy import deepcopy
from collections import defaultdict
import pickle

####################################################################
##  spelling correction modified from Peter Norvig  http://norvig.com/spell-correct.html
####################################################################

def spell_candidates(word): 
#    return (known([word]) or known(edits1(word)) or known(edits2(word)) )
    return ( known(edits1(word)) )

def known(words):
    global TDICT
    return list(w for w in words if w in TDICT)

def edits1(word):
#    letters    = 'abcdefghijklmnopqrstuvwxyz'
    letters = [chr(i) for i in range(ord('ก'),ord('์')+1)]
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return list(deletes + transposes + replaces + inserts)

##########################################################################
## POS tagging using nltk.tag.perceptron
#########################################################################    
## named entity recognition for Person, Location, Organization
## Input = list 0f (w,pos)
## Output = list of (w,pos,ner_tag)
## adapted from http://sklearn-crfsuite.readthedocs.io/en/latest/tutorial.html
def ner(sent):
    lx = []
    if sent[-1][0] == ' ': del(sent[-1]) 
    lx = sent2features(sent)
    try:
      ner_tagger
    except NameError:
      ner_load()

    p = ner_tagger.predict_single(lx)
    r = []
    for i in range(len(sent)):
        r.append(( sent[i][0], sent[i][1], p[i]))
    return (r)

def ner_load():
    global ner_tagger
    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    filehandler = open(ATA_PATH +'/' + 'ner-tagger.pick', 'rb') 
    ner_tagger = pickle.load(filehandler)

def wrd_len(word):
    if len(word) > 20:
        return('l')
    elif len(word) > 10:
        return('m')
    else:
        return('s')
    
def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word': word,
        'postag': postag,
        'len': wrd_len(word)
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word': word1,
            '-1:postag': postag1,
        })
    else:
        features['BOS'] = True
    if i > 2:
        word1 = sent[i-2][0]
        postag1 = sent[i-2][1]
        features.update({
            '-2:word': word1,
            '-2:postag': postag1,
        })
    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word': word1,
            '+1:postag': postag1,
        })
    else:
        features['EOS'] = True
    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]

def pack_ner(sent):
    out = ''
    flag = 'O'
    for (w,p,t) in sent:
        if re.match(r'[BI]-P',t) and flag == 'O':
            out += '<NEp>'+w+'/'+p+'|'
            flag = 'NEp'
            continue
        elif t == 'O' and flag == 'NEp':
            out += '</NEp>'+w+'/'+p+'|'
            flag = 'O'
            continue
        elif re.match(r'[BI]-O',t) and flag == 'O':
            out += '<NEo>'+w+'/'+p+'|'
            flag = 'NEo'
            continue
        elif t == 'O' and flag == 'NEo':
            out += '</NEo>'+w+'/'+p+'|'
            flag = 'O'
            continue
        elif re.match(r'[BI]-L',t) and flag == 'O':
            out += '<NEl>'+w+'/'+p+'|'
            flag = 'NEl'
            continue
        elif t == 'O' and flag == 'NEl':
            out += '</NEl>'+w+'/'+p+'|'
            flag = 'O'
            continue
        else:     
            out += w+'/'+p+'|'
    if flag == 'NEp':
        out += '</NEp>'
    elif flag == 'NEo':
        out += '</NEo>'
    elif flag == 'NEl':
        out += '</NEl>'
        
    return(out)

#############################################################################################################
### Thai grapheme to phoneme
### Input = a chunk of Thai texts
### orginal written in Perl, ported to Python on May 17, 2018
#############################################################################################################
def g2p(Input):
    global SegSep
    global SSegSep
    output = ""
    out = ""
    
    Input = preprocess(Input)
    sentLst = Input.split(SegSep)
    for s in sentLst:
        inLst = s.split(SSegSep)
        for inp in inLst:
            if inp == '': continue            
            objMatch = re.match(r"[^ก-์]+",inp)
            if objMatch:
                out = inp+'<tr/>'+inp
            else:
                y = sylparse(inp)
                out = wordparse(y)
            output = output+out+WordSep
        output = output+'<s/>'    ####write <s/> output for SegSep   
    return(output)        

#############################################################################################################
####### Segment syllable using trigram statistics, only strings matched with a defined syllable pattern will be created
###### all pronunciations of each syllable
def sylparse(Input):
    global SylSep
    global PRON
    global PRONUN
    
    PRONUN = defaultdict(list)
    schart = defaultdict(dict)
    probEnd = defaultdict(float)
    schartx = {}
    schart.clear()
    probEnd.clear()
    tmp = []
    
    EndOfInput = len(Input)
    for f in PRON:
        for i in range(EndOfInput):
            Inx = Input[i:]
            matchObj = re.match(f,Inx)
            if matchObj:
                keymatch = matchObj.group()
                try:
                    matchObj.group(3)
                    charmatch = matchObj.group(1) + ' ' + matchObj.group(2) + ' ' + matchObj.group(3)
                except IndexError:
                    try:
                        matchObj.group(2)
                        charmatch = matchObj.group(1) + ' ' + matchObj.group(2) 
                    except IndexError:
                        try:
                            matchObj.group(1)
                            charmatch = matchObj.group(1) 
                        except IndexError:
                            PRONUN[matchObj.group()].append(PRON[f])
                k=i+len(matchObj.group())
                schart[i][k] = [matchObj.group()]
                codematch = PRON[f]
                codematch = re.sub(r"[^AKYDZCRX]","",codematch)
                if codematch:
#                    print("code char",codematch,charmatch)            
                    phone = ReplaceSnd(PRON[f],codematch,charmatch)
                    if  NotExceptionSyl(codematch,charmatch,keymatch,phone):
                        (phone,tone) = ToneAssign(keymatch,phone,codematch,charmatch)
#                        print('assign tone',tone,' to',keymatch)
                        if (tone < '5'): phone = re.sub(r'8',tone,phone)          
                        (keymatch,phone) = TransformSyl(keymatch,phone)         
                    PRONUN[''.join(schart[i][k])].append(phone)
#                    print("Add",PRON[f],''.join(schart[i][k]), phone)
                    if  re.match(r'ทร',keymatch)  and  re.match(r"thr",phone):            #### gen more syllable  ทร   thr => s
                        phone=re.sub(r"thr","s",phone) 
                        PRONUN[''.join(schart[i][k])].append(phone)
#                        print("Add2",PRON[f],''.join(schart[i][k]), phone)
                    probEnd[(i,k)] = prob_trisyl(schart[i][k])
    
    for j in range(EndOfInput):
        schartx = deepcopy(schart)
        if j in schart[0]:
            s1 = schart[0][j]
            for k in schart[j]:
                    s2 = schart[j][k]
                    tmp = mergekaran1(s1+s2)
                    if k not in schart[0]:                        
                        schartx[0][k] = tmp
                        probEnd[(0,k)] = prob_trisyl(tmp)
                    else:
                        p = prob_trisyl(tmp)
                        if p > probEnd[(0,k)]:
                            schartx[0][k] = tmp 
                            probEnd[(0,k)] = p
        schart = deepcopy(schartx)
    if EndOfInput in schart[0]:    
        return(SylSep.join(schart[0][EndOfInput]))
    else:
        return('<Fail>'+Input+'</Fail>')

def ReplaceSnd(phone,codematch,charmatch):
     global stable
     snd = phone
     tmp1Lst = charmatch.split(' ')   #get character
     i=0
     for x in list(codematch):
          s = stable[x][tmp1Lst[i]]
          snd = re.sub(x,s,snd)
          i += 1 
     snd += '8'
     return(snd)

def NotExceptionSyl(codematch,charmatch,form,phone):
    if re.search(r'\.',form):  return(1)
##  check pronunciation marked in syllable dict, if it exists and it is different from the current phone, disregard current phone.
    if 'CR' in codematch:        
#exception for CR = ถร  ผร  ดล  ตล ถล ทล บล ดว ตว ถว ทว บว ปว ผว สว
        if re.match(r'ผ ร|ด ล|ต ล|ท ล|ด ว|ต ว|ท ว|บ ว|ป ว|พ ว|ฟ ว|ผ ว|ส ล|ส ว|ร ร|ศ ล|ศ ว',charmatch):  return(-1)
#exception for AK = กย กง ขง คง คม จง จน จก ฉย ชง ดย ดง ดน ดม ถย บย บง บน บม ปง ผม พง ฟย ฟง ฟน ฟม ซย ซง ซน ซม  ถร บล บว ปว พร พว นน ยด คว
    if 'AK' in codematch:  #check for leadnng and followinf consinant
        clst = charmatch.split(' ')
        if clst[1] not in AK[clst[0]]: return(-1)

#Case 1 xัว with sound like "..aw"
    if re.search(r'\u0E31[\0E48-\u0E4B]?ว]',form) and 'aw' in phone: return(-1)
#Case 5 check for speller ข Only 3 vowel forms can be used  ัุ   เ
    if re.search(r'[ก-ฮ] ข',charmatch) and not re.search(r'[\u0E38\u0E31\u0E40]',form): return(-1)
# Case  xร - xon   except  Xรน (กรน ปรน)
    if re.search(r'[ก-ฮ] ร$',charmatch) and re.search(r'.an',phone): return(-1)
    return(1)

#######################################
# Tone assign :  ม้าน, maan, codematch XY,  charmatch  ม น,  => return 3
# ToneAssign($keymatch,$phone,$codematch,$charmatch); 
#######################################
def ToneAssign(keymatch,phone,codematch,charmatch):
#print "ToneAssign: $_[0] : $_[1] : $_[2] : $_[3]\n";
    if phone == '' : return('','9')
    lead = ''
    init = ''
    final = ''
    if re.search(r'[0-4]8',phone):   # tone is already assigned
        phone = re.sub(r'([0-4])8',r'\1',phone)
        return(phone,'')
    if 'X' in codematch or codematch == 'GH' or codematch == 'EF':
        lx = charmatch.split(' ')
        lead = ''
        init = lx[0]
        if len(lx) > 1:
            final = lx[1]
        else: final = ''    
    elif re.search(r'AK',codematch) or re.search(r'CR',codematch):
#        (lead, init, final) = charmatch.split(' ')
        lx = charmatch.split(' ')
        lead = lx[0]
        if len(lx) > 2:
            final = lx[2]
            init = lx[1]
        elif len(lx) >1:    
            init = lx[1]
            final = ''

    deadsyll = DeadSyl(phone)

### change + for leading syllable
    if "+'" in phone:
#        print('found leading',phone,lead)
        if lead in 'ผฝถขสหฉศษ':
            phone = re.sub(r'\+','1',phone)
        elif lead in 'กจดตบปอ':
            phone = re.sub(r'\+','1',phone)
        else:    
            phone = re.sub(r'\+','3',phone)

#### normal syllable 
    if init in 'กจดตฎฏบปอ':   # middle consonant
        if deadsyll == 'L':
            if re.search(r'\u0E48',keymatch): return(phone,'1')   #Maiaek
            elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
            elif re.search(r'\u0E4A',keymatch): return(phone,'3')  #Maitri
            elif re.search(r'\u0E4B',keymatch): return(phone,'4')  #Maijatawa
            else: return(phone,'0')
        else:
            if re.search(r'\u0E48',keymatch): return(phone,'9')   #Maiaek
            elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
            elif re.search(r'\u0E4A',keymatch): return(phone,'3')  #Maitri
            elif re.search(r'\u0E4B',keymatch): return(phone,'4')  #Maijatawa
            else: return(phone,'1')
    elif init in 'ขฃฉฐถผฝสศษห':   # high consonant
        if deadsyll == 'L':
            if re.search(r'\u0E48',keymatch): return(phone,'1')   #Maiaek
            elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
            elif re.search(r'\u0E4A',keymatch): return(phone,'9')  #Maitri
            elif re.search(r'\u0E4B',keymatch): return(phone,'9')  #Maijatawa
            else: return(phone,'4')
        else:
            if re.search(r'\u0E48',keymatch): return(phone,'9')   #Maiaek
            elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
            elif re.search(r'\u0E4A',keymatch): return(phone,'9')  #Maitri
            elif re.search(r'\u0E4B',keymatch): return(phone,'9')  #Maijatawa
            else: return(phone,'1')
    elif init in 'งญณนมยรลวฬ' and lead != '' and lead in 'ขฃฉฐถผฝสศษห':  #low consonant single
#        if lead in 'ขฃฉฐถผฝสศษห':   # lead by high consonant
            if deadsyll == 'L':
                if re.search(r'\u0E48',keymatch): return(phone,'1')   #Maiaek
                elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
                elif re.search(r'\u0E4A',keymatch): return(phone,'9')  #Maitri
                elif re.search(r'\u0E4B',keymatch): return(phone,'9')  #Maijatawa
                else: return(phone,'4')
            else:
                if re.search(r'\u0E48',keymatch): return(phone,'9')   #Maiaek
                elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
                elif re.search(r'\u0E4A',keymatch): return(phone,'9')  #Maitri
                elif re.search(r'\u0E4B',keymatch): return(phone,'9')  #Maijatawa
                else: return(phone,'1')
    elif init in 'งญณนมยรลวฬ' and lead != '' and lead in 'กจดตฎฏบปอ':  #low consonant single
#        elif lead in 'กจดตฎฏบปอ':  #lead by middle consonant
            if deadsyll == 'L':
                if re.search(r'\u0E48',keymatch): return(phone,'1')   #Maiaek
                elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
                elif re.search(r'\u0E4A',keymatch): return(phone,'3')  #Maitri
                elif re.search(r'\u0E4B',keymatch): return(phone,'4')  #Maijatawa
                else: return(phone,'0')
            else:
                if re.search(r'\u0E48',keymatch): return(phone,'9')   #Maiaek
                elif re.search(r'\u0E49',keymatch): return(phone,'2')  #Maitoo
                elif re.search(r'\u0E4A',keymatch): return(phone,'3')  #Maitri
                elif re.search(r'\u0E4B',keymatch): return(phone,'4')  #Maijatawa
                else: return(phone,'1')
    elif init in 'คฅฆชฌซฑฒทธพภฟฮงญณนมยรลวฬ': #low consonant
        if deadsyll == 'L':
            if re.search(r'\u0E48',keymatch): return(phone,'2')   #Maiaek
            elif re.search(r'\u0E49',keymatch): return(phone,'3')  #Maitoo
            elif re.search(r'\u0E4A',keymatch): return(phone,'9')  #Maitri
            elif re.search(r'\u0E4B',keymatch): return(phone,'9')  #Maijatawa
            else: return(phone,'0')        
        elif re.search(r'[aeiouxOU\@][aeiouxOU\@]+',phone):  # long vowel
            if re.search(r'\u0E48',keymatch): return(phone,'9')   #Maiaek
            elif re.search(r'\u0E49',keymatch): return(phone,'3')  #Maitoo
            elif re.search(r'\u0E4A',keymatch): return(phone,'9')  #Maitri
            elif re.search(r'\u0E4B',keymatch): return(phone,'4')  #Maijatawa
            else: return(phone,'2')
        else:    # short vowel
            if re.search(r'\u0E48',keymatch): return(phone,'2')   #Maiaek
            elif re.search(r'\u0E49',keymatch): return(phone,'9')  #Maitoo
            elif re.search(r'\u0E4A',keymatch): return(phone,'9')  #Maitri
            elif re.search(r'\u0E4B',keymatch): return(phone,'4')  #Maijatawa
            else: return(phone,'3')

#########################################
# Check whether it's a dead syllable : input is a pronunciation, return 'D' or 'L'
##########################################
def DeadSyl(phone):
    inx = phone
    inx = re.sub('ch','C',inx)
    inx = re.sub(r'[0-4]','',inx)
    if re.search(r'[mnwjlN]8?$',inx):
        return('L')
    elif re.search(r'[pktfscC]8?$',inx):
        return('D')
    elif re.search(r'([aeiouxOU\@])\1',inx):  # vowel length > 1
        return('L')
    else:
        return('D')
    
def TransformSyl(form,phone):
# xxY[12]  eeY[12] @@Y[12]  => ลดสระสั้น  ใน Y = [nmN]
    if re.search(r'xx[nmN][12]',phone):
        phone = re.sub(r'xx','x',phone)
    elif re.search(r'ee[nmN][12]',phone):
        phone = re.sub(r'ee','e',phone)
    elif re.search(r'\@\@[nmN][12]',phone):
        phone = re.sub(r'\@\@','\@',phone)
#Case 1 อยxxx change sound "?a1'jxxx" to "jxxx"
    if re.search(r'^อย่า$|^อยู่$|^อย่าง$|^อยาก$',form) and "'" in phone:
        x = phone.split("'")
        phone = x[-1]
#Case 2 หxxx change spund "ha1'xxx" to "xxx"
    elif 'ห' in form and 'ha1' in phone and not re.search(r'หนุ$|หก|หท|หพ|หฤ|หโ',form):
        x = phone.split("'")
        phone = x[-1]
#Case 3 arti-cluster sound, sound "r" is deleted
    elif re.search(r'[จซศส]ร',form) and re.search(r'[cs]r',phone) and re.search(r"[^']",phone):
        phone = re.sub('r','',phone)
    return (form,phone)
    
#### word segment and select the most likely pronunciation in a word    
def wordparse(Input):
    global TDICT
    global EndOfSent
    global chart
    global SegSep
    global WordSep
    global CollocSt
    
    part = []
    chart = defaultdict(dict)
    SylSep = '~'
    outx = ""
    chart.clear()
    CollocSt = defaultdict(float)
    
    part = Input.split(SegSep)
    for inx in part:
        SylLst = inx.split(SylSep)
        EndOfSent = len(SylLst)
        ######### Gen unknown word by set each syllable as a potential word
#        gen_unknown_thaiw(SylLst)
        for i in range(EndOfSent):
            chart[i][i+1] = [SylLst[i]]
        ############################################################
        for i in range(EndOfSent):
            for j in range(i,EndOfSent+1):
                wrd = ''.join(SylLst[i:j])
                if wrd in TDICT:
#                    chart[i][j] = [wrd]
                    chart[i][j] = ['~'.join(SylLst[i:j])]
                    if j > i+1:   ### more than one syllable, compute St
                        St = 0.0
                        NoOfSyl = len(SylLst[i:j])
                        for ii in range(i,j-1):
                            St += compute_colloc("mi",SylLst[ii],SylLst[ii+1])
                        CollocSt[(i,j)] = St    #### Compute STrength of the word
                    else:   ### one sylable word St = 0
                        CollocSt[(i,j)] = 0.0
        if chart_parse():
            outx += WordSep.join(chart[0][EndOfSent])
            outx += '<tr/>'
            outp = []
            for  wx in chart[0][EndOfSent]:
                tmp = wx.split(SylSep)
                op = SelectPhones(tmp)    
                outp.append(op)
            outx += WordSep.join(outp)
            return(outx)
        else:
            return("<Fail>"+Input+"</Fail>")
    
## input = list of syllables
## output = syl/pron-syl/pron-syl/pron
def SelectPhones(slst):
   global PRONUN 
   p=''
   out = []
   prmax = 0.

   slst = ['|'] + slst + ['|']
#   print('slist',slst)
   i = 1
   for i in range(1,len(slst)-1):
        outp = ''
#        if slst[i] == '|': continue
        if len(PRONUN[slst[i]]) == 1:
            out.append(PRONUN[slst[i]][0])
            continue
        else:
            for p in PRONUN[slst[i]]:
                pr = ProbPhone(p, slst[i-1],slst[i],slst[i+1])
#                print(slst[i],' pronounce ',p,pr)
                if pr > prmax:
                   prmax = pr
                   outp = p
                elif pr == prmax:
                   if re.search(r"'",p)  and len(p) > len(outp):
                      prmax = pr
                      outp = p
        out.append(outp)
#        print('out',slst[i],out)
        i += 1
#   print('Select Phone',out)       
   return('~'.join(out))


####################
def ProbPhone(p,pw,w,nw):
    global PhSTrigram
    global FrmSTrigram
    global PhSBigram
    global FrmSBigram
    global PhSUnigram
    global FrmSUnigram
    p3=0.
    p2=0.
    p1=0.
    if PhSTrigram[(pw,w,nw,p)] > 0.:
        p3 = (1. + math.log(PhSTrigram[(pw,w,nw,p)])) / (1. + math.log(FrmSTrigram[(pw,w,nw)]))
#        print('Trigram',PhSTrigram[(pw,w,nw,p)])
    if PhSBigram[(pw,w,p)] > 0.:
#        print('Bigram1',PhSBigram[(pw,w,p)])
        p2 = (1. + math.log(PhSBigram[(pw,w,p)])) / (1. + math.log(FrmSBigram[(pw,w)])) * 0.25
### check w and next w because following syllable is important to determine the linking sound  give it more weigth x 3/4
    if PhSBigram[(w,nw,p)] > 0.:
#        print('Bigram2',PhSBigram[(w,nw,p)])
        p2 = p2 + (1. + math.log(PhSBigram[(w,nw,p)])) / (1. + math.log(FrmSBigram[(w,nw)])) * 0.75
    if PhSUnigram[(w,p)] > 0.:
        p1 = (1 + math.log(PhSUnigram[(w,p)])) / (1. + math.log(FrmSUnigram[w]))
    prob =  0.8 * p3 + 0.16 * p2 + 0.03 * p1 + .00000000001
    return(prob)
        
def th2roman(txt):
    out = ''
    NORMALIZE_ROM = [ ('O', 'o'), ('x', 'ae'), ('@', 'oe'), ('N', 'ng'), ('U','ue'), ('?',''), ('|',' '), ('~','-'),('^','-'),("'",'-')]
    inx = g2p(txt)
    for seg in inx.split('<s/>'):
        if seg == '': continue
        (th, tran) = seg.split('<tr/>')
        tran = re.sub(r"([aeiouUxO@])\1",r"\1",tran)
        tran = re.sub(r"[0-9]",r"",tran)
        for k, v in NORMALIZE_ROM:
            tran = tran.replace(k, v)
        tran = re.sub(r"([aeiou])j",r"\1i",tran)
        tran = tran.replace('j','y')
        tran = re.sub(r"\-([^aeiou])",r"\1",tran)
        out += tran+'<s/>'
    return(out)
    
### end of modules used in g2p  ###############    
###################################################################

#############################################################################################################
#########  Chart Parsing, ceate a new edge from two connected edges, always start from 0 to connect {0-j} + {j+k}
#########  If maximal collocation appraoch is chosen, the sequence with highest score will be selected
def chart_parse():
    global chart
    global CollocSt
    
    for j in range(EndOfSent):
        chartx = deepcopy(chart)
        if j in chart[0]:
            s1 = chart[0][j]
            for k in chart[j]:
                    s2 = chart[j][k]
                    if k not in chart[0]:                        
                        chartx[0][k] = s1+s2
#                        CollocSt[(0,k)] = (CollocSt[(0,j)] + CollocSt[(j,k)])/2.0
                        CollocSt[(0,k)] = CollocSt[(0,j)] + CollocSt[(j,k)]
                    else:
                        if CollocSt[(0,j)]+CollocSt[(j,k)] > CollocSt[(0,k)]:
#                            CollocSt[(0,k)] = (CollocSt[(0,j)] + CollocSt[(j,k)])/2.0
                            CollocSt[(0,k)] = CollocSt[(0,j)] + CollocSt[(j,k)]
                            chartx[0][k] = s1+s2
        chart = deepcopy(chartx)
    if EndOfSent in chart[0]:
        return(1)
    else:
        return(0)

#############################################################################################################

######################
def mergekaran(Lst):
####  reconnect karan part to the previous syllable for SylSegment
   rs = []
   Found = 'n'
   Lst.reverse()
   for s in Lst:
        if re.search(r"(.+)[ิุ]์",s):    # anything + i or u + Karan
            if len(s) < 4:
                Found = 'y'
                x = s
                continue
        elif  re.search(r"(.+)์",s):  # anything + Karan
            if len(s) < 4:
                Found = 'y'
                x = s
                continue
        if Found == 'y':
            s += x
            rs.append(s)
            Found = 'n'
        else:
            rs.append(s)
   rs.reverse()
   return(rs)

def mergekaran1(Lst):
####  reconnect karan part to the previous syllable for SylSegment
#### include merhing pronunciation
   rs = []
   global MKaran
   MKaran.clear()
   Found = 'n'
   Lst.reverse()
   for s in Lst:
        if re.search(r"(.+)[ิุ]์",s):    # anything + i or u + Karan
            if len(s) < 4:
                Found = 'y'
                x = s
                continue
        elif  re.search(r"(.+)์",s):  # anything + Karan
            if len(s) < 4:
                Found = 'y'
                x = s
                continue
        if Found == 'y':
            for ph in PRONUN[s]:
                if (s+x,ph) not in MKaran:
                    PRONUN[s+x].append(ph)
                    MKaran[(s+x,ph)] = 1 
            s += x
            rs.append(s)
            Found = 'n'
        else:
            rs.append(s)
   rs.reverse()
   return(rs)

########################################
# calculate proability of each possible output
#  Version 1.6>  expect input = list of forms
########################################
def prob_trisyl(SylLst):
    global TriCount
    global BiCount
    global Count
    global BiType
    global Type
    global NoTrigram
    global TotalWord
    global TotalLex
    global SegSep
    Prob = defaultdict(float)
    
#    SegSep = chr(127)

    pw2 = SegSep
    pw1 = SegSep
    Probx = 1.0
    
    for w in SylLst:
        if (w,pw1,pw2) in Prob:
            Proba = Prob[(w,pw1,pw2)]
        else:
            Prob[(w,pw1,pw2)] = prob_wb(w,pw1,pw2)
            Proba = Prob[(w,pw1,pw2)]
#        Probx *= Proba
        Probx += Proba    ## prob is changed to log
        pw2 = pw1
        pw1 = w
#    print("prob ",Probx)
    
    return(Probx)

########################################
# p(w | pw2 pw1)   Smoothing trigram prob  Witten-Bell
#######################################
def prob_wb(w,pw1,pw2):
    global TriCount
    global BiCount
    global Count
    global BiType
    global Type
    global NoTrigram
    global TotalWord
    global TotalLex
    
    p3 = 0.0
    p2 = 0.0
    p1 = 0.0
    p = 0.0
    px1 = 0.0
    
#    print "trigram ", pw2,pw1,w
#    print "count ",TriCount[(pw2,pw1,w)],BiCount[(pw1,w)],Count[w]
    if TriCount[(pw2,pw1,w)] > 0:
        p3 = float(TriCount[(pw2,pw1,w)]) / float( BiCount[(pw2,pw1)] + BiType[(pw2,pw1)])
    if BiCount[(pw1,w)] > 0:
        p2 = float( BiCount[(pw1,w)]) / float((Count[pw1] + Type[pw1]) )
    if Count[w] > 0:
        p1 = float( Count[w]) / float(TotalWord + TotalLex)
    p = 0.8 * p3 + 0.15 * p2 + 0.04 * p1 + 1.0 / float((TotalWord + TotalLex)**2)
### change to log to prevent underflow value which can cause incorrect syllable segmentation
    p = math.log(p)

    return(p)

########## Preprocess Thai texts  #### adding SegSep and <s> for speocal 
def preprocess(input):
    global SegSep
    global SSegSep

    input = re.sub(u" +ๆ",u"ๆ",input)

#    input = re.sub(u"เเ",u"แ",input)
####### codes suggested by Arthit Suriyawongkul #####
    NORMALIZE_DICT = [
        ('\u0E40\u0E40', '\u0E41'), # Sara E + Sara E -> Sara AE
        ('\u0E4D\u0E32', '\u0E33'), # Nikhahit + Sara AA -> Sara AM
        ('\u0E24\u0E32', '\u0E24\u0E45'), # Ru + Sara AA -> Ru + Lakkhangyao
        ('\u0E26\u0E32', '\u0E26\u0E45'), # Lu + Sara AA -> Lu + Lakkhangyao
    ]
    for k, v in NORMALIZE_DICT:
        input = input.replace(k, v)
########################################################        
#    print input.encode('raw_unicode_escape')

  ##### change space\tab between [ET][ET] and [ET]  to be SegSep
#    input = re.sub(r"([^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*[^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*)[\s\t\u00A0]+([^\s\t\u00A0])",r"\1"+SegSep+r"\2",input)
    input = re.sub(r"([^\s\t\u00A0]{3,})[\s\t\u00A0]+([^\s\t\u00A0]+)",r"\1"+SegSep+r"\2",input)

    
   ##### change space\tab between [ET] and [ET][ET]  to be SegSep
#    input = re.sub(r"([^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*)[\s\t\u00A0]+([^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*[^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*)",r"\1"+SegSep+r"\2",input)
    input = re.sub(r"([^\s\t\u00A0]+)[\s\t\u00A0]+([0-9]+)",r"\1"+SegSep+r"\2",input)
    input = re.sub(r"([^\s\t\u00A0]+)[\s\t\u00A0]+([^\s\t\u00A0]{3,})",r"\1"+SegSep+r"\2",input)

  ###  handle Thai writing one character one space by deleting each space
    pattern = re.compile(r'([ก-ฮเแาำะไใโฯๆ][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*) +([ก-ฮเแาำะไใโฯๆ\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]{,2}) +|([ก-ฮเแาำะไใโฯๆ][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*) +([ก-ฮเแาำะไใโฯๆ\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]{,2})$')
    while re.search(pattern, input):
        input = re.sub(pattern, r"\1\2", input,count=1)



        ### handle English and Thai mixed without a space inside $s by adding SSegSep (softSegSep)
    input = re.sub(r"([ก-์][ฯๆ])",r"\1"+SSegSep,input)
    input = re.sub(r"([\u0E01-\u0E5B]+\.?)([^\.\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
#    input = re.sub(r"([\u0E01-\u0E5B]+)([^\.\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
    input = re.sub(r"([^\.\u0E01-\u0E5B]+)([\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
    input = re.sub(r"(<.+?>)",SSegSep+r"\1",input)
    input = re.sub(r"([0-9a-zA-Z\.\-]{2,})([\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
    input = re.sub(r"(\.\.\.+)",r""+SSegSep+r"\1"+SSegSep,input)    #  ....  add SSegSep after that
#    print "3. ",input

    return(input)

#############################################################################################################
### initialization by read syllable patterns, syllable trigrams, and satndard dictionary
def initial():
    global SylSep
    global WordSep
    global SegSep
    global SSegSep
    global TDICT
    global PRON
    global CProb

    PRON = {}    
    TDICT = {}
    CProb = defaultdict(float)
    
    SylSep = chr(126)
    WordSep = chr(124)
    SSegSep = chr(30)
    SegSep = chr(31)

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    
#    try:
#        ATA_PATH = pkg_resources.resource_filename('tltk', '/')


    return(1)

############ END OF GENERAL MODULES ##########################################################################

initial()