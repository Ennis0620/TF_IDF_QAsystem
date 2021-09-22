import jieba
import re
import json
import time

print("model讀取中....")
s = time.time()
##讀進QA_model 和 IDF
with open('model.json', 'r',encoding='utf-8-sig') as jsonfile:
    QA_model = json.load(jsonfile)
with open('IDF.json', 'r',encoding='utf-8-sig') as jsonfile:
    IDF = json.load(jsonfile)
e = time.time()
print("model讀入時間",round(e-s,6),"秒")

#設定斷詞詞庫
jieba.load_userdict('lexicon_dict.txt')

 
    
while True:
    #使用者輸入    
    query_input = input("請輸入查詢問句(若要結束請輸入stop):")
    if query_input=="stop" :  break 
    
    query_input = "".join(query_input.split())#去掉問句中的空白
    
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
        
    print("query_TF_IDF",query_TF_IDF)
    
    
    #計算cos_similarity cos x = a dot b / |a||b|   
    #|b| =  query_TF_IDF[i]的內積 = query_TF_IDF[i]的平方相加 最後開根號
    absolute_b = 0
    for i in query_TF_IDF:
        absolute_b += query_TF_IDF[i]*query_TF_IDF[i]
    absolute_b = pow(absolute_b,0.5)
    
   
    
    
    '''
    這個速度較慢
    #每個document的 inner 
    for index,i in enumerate(QA_model):
        absolute_a = QA_model[index]["Inner_Production"]
        absolute_a = math.sqrt(absolute_a)
        
        
        # a_dot_b 的計算
        a_dot_b = 0
        for seg in QA_model[index]["Model"]:
            if seg in query_TF_IDF:
                a_dot_b += QA_model[index]["Model"][seg] * query_TF_IDF[seg]      
     ''' 
    #輸入都沒有匹配到答案就讓使用者重新輸入
    if absolute_b == 0.0 : 
        continue
    
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
        
    qe = time.time()    
    
    print("-----------------------------------------")
    print("斷詞結果:",seg_sentence)
    print("-----------------------------------------")
    print("|a|",absolute_a)
    print("|b|",absolute_b)
    
    print("最大可能")
    print("cos_X:",max_three_pro[0])
    print(QA_model[max_three_pro_index[0]])

    print("-----------------------------------------")
    print("第二大的可能")
    print("cos_X:",max_three_pro[1])
    print(QA_model[max_three_pro_index[1]])

    print("-----------------------------------------")
    print("第三大的可能")
    print("cos_X:",max_three_pro[2])
    print(QA_model[max_three_pro_index[2]])

    print("-----------------------------------------")
    print("回答耗時:",round(qe-qs,6),"秒")