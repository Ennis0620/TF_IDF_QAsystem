import asyncio
import websockets
import jieba
import json

from Websocket_user_query import user_query,model_read


#讀進model
QA_model,IDF= model_read()
#設定斷詞詞庫
jieba.load_userdict('QA_system/lexicon_dict.txt')

async def response(websocket, path):
    
    #接收客戶端的訊息
    message = await websocket.recv()
    print(f"收到一則詢問:{message}")
    await websocket.send(message)

    answer1,answer2,answer3,three_pro_json,seg_and_cost = user_query(message,QA_model,IDF)
    
    print("耗時:",seg_and_cost["cost_time"])
    print("斷詞:",seg_and_cost["seg_sentence"])
    print("可能機率:",three_pro_json)

    print(answer1)
    print(answer2)
    print(answer3)
    #因為websocket無法傳json要先變成字串形式
    
    
    await websocket.send(json.dumps(answer1))
    await websocket.send(json.dumps(answer2))
    await websocket.send(json.dumps(answer3))
    await websocket.send(json.dumps(seg_and_cost))
    await websocket.send(json.dumps(three_pro_json)) 


start_server = websockets.serve(response, "192.168.1.33", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
