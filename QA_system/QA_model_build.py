import re 
import time
import jieba
import math
import json

#設定斷詞詞庫
jieba.load_userdict('lexicon_dict.txt')


len_Q = 0 #存下共有多少問題
IDF={}                 #字詞庫中所有詞彙

s = time.time()

QA_model = [] #要儲存的model 以[{},{},...]的形式儲存
#進行問題的斷詞
with open("Gossiping-QA-Dataset.txt","r",encoding='utf-8-sig') as fp:
    all_ =  fp.readlines()
    for index,row in enumerate(all_):
        
        dic = {} #存每一個document的
        
        row_split = row.split("\t") #用tab來分割 問題 和 回答
        Q_row = "".join(row_split[0].split())#去除document問題的空白
        ID = '{0:06d}'.format(index)
        dic.setdefault("ID",ID) #設置document的ID
        dic.setdefault("Question",row_split[0]) #問題
        dic.setdefault("Answer",row_split[1].strip("\n"))   #回答
        
        seg = {} #將斷詞的結果存成字典形式
        count = 0 #計算斷詞共斷了幾項
        TF_table={} #紀錄目前的TF_table
        #進行jieba斷詞
        for Hyphenation in jieba.cut(Q_row):
                  
            #將斷詞的詞彙 寫到IDF中 代表出現的 詞彙
            count+=1 #統計斷詞 數量
            seg.setdefault(Hyphenation,0)#先設置成0
            
            if Hyphenation not in TF_table: #如果 "為什麼" 沒在TF_table中 代表第一次出現
                TF_table.setdefault(Hyphenation,1) #設置出現次數=1
                IDF.setdefault(Hyphenation,0) #先設置IDF=0 代表documnet的斷詞 並 更新在IDF中
            else:
                TF_table[Hyphenation] += 1#若有出現在字典中 代表之前就有出現過 直接+=1
                
        
        #進行TF_normalization  TF_table/count
        for i in TF_table:
            seg[i] = round(TF_table[i]/count,6)
            
            #IDF 不管出現過幾次 同一個document中 只計算1次
            #因為TF_table已經整理過 字彙的出現次數 例如:"為什麼":2 因此若 跑到"為什麼":2 就將 該筆的IDF 直接加1 
            IDF[i]+=1
            
        dic.setdefault("Model",seg) #將斷完的詞存到字典中 
        
        QA_model.append(dic) #將此document的資訊添加到QA_model中
    
        if index%50000==0:
            print("目前處理筆數:",index)
    
    len_Q = index

       
#計算IDF
#取log是為了不要讓權重太大 將差距拉小
#因為在TF中彼此差距很小 但是在IDF中 有可能 某詞在所有document中出現其IDF會超級小  某詞只在單一document出現其IDF超級大
for i in IDF:
    if IDF[i] == 0 :
        IDF[i] = round(math.log10(len_Q/1),6)
    else:
        IDF[i] = round(math.log10(len_Q/IDF[i]),6)

#計算TF_IDF
for index in range(0,len_Q+1):
    
    #計算內積"Inner_Production"
    inner_production = 0
    
    #從model中儲存的TF 和 IDF 計算成TF-IDF
    for i in QA_model[index]["Model"]:
        #QA_model中的每一筆資料 進行 TF 和 IDF 的乘法
        QA_model[index]["Model"][i] = round(QA_model[index]["Model"][i]*IDF[i],6)
        #內積相當於 自己的平方
        inner_production += QA_model[index]["Model"][i]*QA_model[index]["Model"][i]
    
    #將計算完的內積加入這筆model當中
    QA_model[index].setdefault("Inner_Production",inner_production)
    

e = time.time()

print("共花費秒數:",round(e-s,6))

#要儲存的有 IDF、QA_model
#存成json格式
with open('model.json',"w",encoding='utf-8-sig') as jsonfile:    
    json.dump(QA_model,jsonfile,separators=(',\n', ': '),indent=4,ensure_ascii=False)

with open('IDF.json',"w",encoding='utf-8-sig') as jsonfile:    
    json.dump(IDF,jsonfile,separators=(',\n', ': '),indent=4,ensure_ascii=False)

e2 = time.time()

print("建立model到儲存model所有耗時:",round(e2-s,6))

 
