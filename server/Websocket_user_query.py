import jieba
import re
import math
import json
import time

def model_read():

    print("model讀取中....")
    s = time.time()
    ##讀進QA_model 和 IDF
    with open('QA_system/model.json', 'r',encoding='utf-8-sig') as jsonfile:
        QA_model = json.load(jsonfile)
    with open('QA_system/IDF.json', 'r',encoding='utf-8-sig') as jsonfile:
        IDF = json.load(jsonfile)
    e = time.time()
    print("model讀入時間",round(e-s,6),"秒")
    
    
    return QA_model,IDF


def user_query(query_input,QA_model,IDF):
        
    
    
    
    #使用者輸入    
    
    #if query_input=="stop" :  break 
    
    query_input = "".join(query_input.split())#去掉問句中的符號
    
    qs = time.time()
    
    
    query_TF = {} #query斷詞後出現次數
    query_TF_IDF = {}#根據 normalization後的query_TF 和 儲存的IDF model 進行權重相乘
    
    count = 0 #計算出現次數
    seg_sentence = "" #記下斷詞後的句子
    #斷詞 並計算query的TF
    for i in jieba.cut(query_input):
        
        seg_sentence += i+" "
        
        #如果有在 字詞庫中 且 是第一次出現
        if i in IDF and i not in query_TF:
            query_TF.setdefault(i,1)
            count+=1
        #已經出現過一次以上 直接+1
        elif i in IDF and i in query_TF:
            query_TF[i] += 1
            count+=1
        #若都沒出現在IDF中 代表該 詞彙沒有在model裡面 直接忽略    
        elif i not in IDF:
            continue
        
    #將query_TF 進行 normalization
    for i in query_TF:
        query_TF[i] = round(query_TF[i]/count,6)
    
    #計算query_TF_IDF 
    for i in query_TF:   
        query_TF_IDF.setdefault(i,round(query_TF[i]*IDF[i],6))
        
    
    #計算cos_similarity cos x = a dot b / |a||b|
    
    #|b| =  query_TF_IDF[i]的內積 = query_TF_IDF[i]的平方相加 最後開根號
    absolute_b = 0
    for i in query_TF_IDF:
        absolute_b += query_TF_IDF[i]*query_TF_IDF[i]
    absolute_b =pow(absolute_b,0.5)
    
    #輸入都沒有匹配到答案就讓使用者重新輸入
    if absolute_b == 0.0 : 
        return "請重新輸入"
        
    
    
    absolute_a = 0
    
    
    #判斷哪個是最有可能的
    max_three_pro  = [0,0,0]
    max_three_pro_index = [0,0,0]
    
        
        
       
    #每個document的 inner 
    for index,i in enumerate(QA_model):
        absolute_a = QA_model[index]["Inner_Production"]
        absolute_a = pow(absolute_a,0.5)
         
        # a_dot_b 的計算
        a_dot_b = 0
        for seg in query_TF_IDF:
            if seg in QA_model[index]["Model"]:
                a_dot_b += QA_model[index]["Model"][seg] * query_TF_IDF[seg]

        #文章中有沒切分好的 index = 87319 沒有問題輸入
        if absolute_a == 0.0 : continue
        
        cos_X = round(a_dot_b / (absolute_a * absolute_b),6)
        
        
        
        #找出最有關聯的三個回答
        for len_,i in enumerate(max_three_pro):
            if cos_X > i:
                max_three_pro[len_] = cos_X                    
                max_three_pro_index[len_] = index
                break
    
    three_pro_json={}
    for index,i in enumerate(max_three_pro):
        pro = str(round(i*100,2))+"%"
        three_pro_json.setdefault("cosx"+str(index+1),pro)
            
    
    qe = time.time()
    cost_time = round(qe-qs,6)

    seg_and_cost = {}
    seg_and_cost.setdefault("cost_time",cost_time)
    seg_and_cost.setdefault("seg_sentence",seg_sentence)    
    
    #回傳的有 最有可能、第二可能、第三可能、三種可能的cosx、花費時間、斷詞結果
    return QA_model[max_three_pro_index[0]],QA_model[max_three_pro_index[1]],QA_model[max_three_pro_index[2]],three_pro_json,seg_and_cost
    
