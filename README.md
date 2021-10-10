Q&A問答系統
===




## Introduction
透過TF-IDF演算法建立model，讓使用者透過網頁輸入問題，並根據餘弦相似度來計算輸入問題和語料庫中的相似程度，回覆給使用者相似度最高的前3句。

---

## Detail

**model train**

計算TF(詞頻):將語料庫中的問題，用jieba進行斷詞，統計在該句中，每個詞出現的頻率。

計算IDF(逆向文件頻率):統計一個詞在所有語料庫的問題中出現次數，算出其頻率，存成json檔案。

計算TD-IDF:根據TF和IDF的結果，相乘可以得出每個問句當中各詞的TF-IDF，並計算該問句的內積，存成json格式的model。

**cos similarity**

餘弦相似度:將使用者輸入的問題也進行斷詞計算TF，並根據所存的IDF算出其TF-IDF，並算出輸入問題的內積，比對model中每一筆資料，算出相似度最接近的3句。





---
## Demo

### model儲存格式

![](https://i.imgur.com/j9i0oya.png)
---
### 前端詢問&得到回答

![](https://i.imgur.com/6TZpEev.png)
---
### 後端收到的訊息

![](https://i.imgur.com/Y23jpvD.png)

---



## Front End & Back End

![](https://i.imgur.com/HUnZWeN.png)


---

## Requirement
    jieba
    json
    asyncio
    websockets

---

## Package

    ├─QA_system
    │      Gossiping-QA-Dataset.txt     問答資料集
    │      IDF.json                     IDF模型
    │      lexicon_dict.txt             常用單字辭典
    │      model.json                   TF-IDF模型
    │      QA_model_build.py            建立模型
    │      user query return 3 ans.py   回饋3組答案
    │      
    ├─server
    │      server.py                    後端
    │      Websocket_user_query.py      後端回饋模組
    │      
    └─web
            Websocket_client3.html      前端
            
---
## Problems

1.要如何解決TF-IDF稀疏矩陣問題

2.如何加速計算相似度速度

## Solve

1.使用字典來儲存，如此一來沒有出現的不會像陣列一樣要佔空間

2.在建立TF-IDF的model時就欲先存入該問題的內積，如此一來就可以少去每次計算自身內積的耗時

