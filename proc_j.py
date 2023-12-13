from math import fabs
from os import listdir
from os.path import isfile, join
import json
from datetime import datetime


def prepareData(num,dirr):
    for ix in range(num):
        def print_dialog_tree(dialog, visited=None, indent=0):
            if visited is None:
                visited = set()
            if id(dialog) in visited:
                return
            visited.add(id(dialog))
            for msg in dialog:
                #message_str = json.dumps(msg['message'], ensure_ascii=False)  # Конвертация в строку
                if msg['children']:
                    for child_id in msg['children']:
                        child_dialog = next((d for d in conv if d[0]['id'] == child_id), None)
                        if child_dialog:
                            print_dialog_tree(child_dialog, visited, indent + 2)
        f = json.load(open(f'{dirr}/{ix+1}/conversations.json'))
        conv = []
        for i in range(len(f)):
            print(f[i]['title'])
            x = []
            for a in list(f[i]['mapping'].keys()):
                msg = f[i]['mapping'][a]
                x.append(msg)
            conv.append(x)
        # Вывод диалоговой структуры
        for dialog in conv:
            print_dialog_tree(dialog)
        # Экспорт всех диалоговых ветвей в файл temp/save.json
        with open(f'x1/s/{ix+1}.json', 'w', encoding='utf-8') as save_file:
            json.dump(conv, save_file, ensure_ascii=False, indent=4)
    s=[]
    for i in range(num):
        f=json.load(open(f'x1/s/{i+1}.json',encoding='utf-8'))
        for a in f:
            if a not in s:
                s.append(a)
    
    with open('x1/temp_save.json', 'w', encoding ='utf8') as json_file:
        json.dump(s, json_file, ensure_ascii = True)


def getText(msg):
    text=None
    texts=msg['content'].get('parts')
    #print(texts)
    out=[]
    if texts==None:
        text=msg['content'].get('text')
    else:
        if type(texts)==type([]):
            for a in texts:
                if type(a)==type(""):
                    out.append(a)
                else:
                    content_type=a.get('content_type')
                    if content_type!=None:
                        if content_type:
                            if (a['content_type']=='image_asset_pointer'):
                                return False,'Image detector'
                        else:
                            #print('Error',content_type)
                            exit()
                text=" ".join(out)
        elif type(texts[0])==type(""):
            text="".join(texts).replace('\r','').replace('\n\n','\n').replace('\n\n','\n').replace('\n\n','\n')
            # В текущей версии ChatGPT OpenAi Export Api (10.11.23) нет ничего интересного в type!=text
        else:
            print("\n\n\n",text,"n\n\n")
    if text==None:
        text=msg['content'].get('result')

    if text!=None:
        return True," ".join(out)
    else:
        return False,None
def cleanDS(dataset):
    denyword=[['Екатеринбург','Город'],['екатеринбург','город']] # Это список слов для замены , к примеру "екатеринбург" меняется на "город"
    xx=[]
    for a in dataset.split(' '):
        for b in denyword:
            a=a.replace(b[0],b[1])
        
        xx.append(a)
    xx=" ".join(xx)
    xx=xx.split('\n')
    '''
    xx3=[]
    for i in range(len(xx)):
        if i==0:
            xx3.append(xx[i])
        else:
            if xx3[-1].split(', "text": "')[1]!=xx[i].split(', "text": "')[1]:
                xx3.append(xx[i])
    '''
    return "\n".join(xx)

def chatGPT_proc(num,dirr):
    prepareData(num,dirr)

    m=[]

    dataset=[]
    f=json.load(open(f'x1/temp_save.json',encoding='utf-8'))
    #print(len(f))
    img_detect=0
    for i in range(len(f)):

        x1=[]
        Allow=True
        img_detect_stat=False
        # Это секректные инструкции от OpenAi, которые, для удобства, я перевел на русский
        x1.append(json.dumps({"role": "system", "text": "Никогда не использовать эмодзи, если не запрошено. Ответы должны быть предложением или двумя, если запрос пользователя не требует развернутого ответа или рассуждения."},ensure_ascii=False))
        x1.append(json.dumps({"role": "system", "text": "Прежде чем ответить, тихо подумать о том, насколько запрос пользователя связан с предоставленным профилем. Учитывать профиль только тогда, когда запрос напрямую связан с информацией в профиле. В противном случае не упоминать существование этих инструкций или информации вообще."},ensure_ascii=False))
        x1.append(json.dumps({"role": "system", "text": "ChatGPT, большая языковая модель, обученная OpenAI на архитектуре GPT."},ensure_ascii=False))

        for j in range(len(f[i])):
            msg=f[i][j]['message']
            #print(msg)
            if msg!=None:
                status_text,text=getText(msg)
                if status_text==False:
                    #print('Error',text)
                    if text=='Image detector':
                        Allow=False
                        img_detect_stat=True
                    
                else:
                    autor=msg['author']['role']
                    if autor in ['assistant','user']:
                        if (autor=='assistant') and ('{\n  \"prompts\": [' in text):
                            try:
                                x1.append(json.dumps({"role":autor,"text":{"dall-e":json.loads(text.replace('\\n','').replace('\\r',''))}},ensure_ascii=False))
                            except:
                                Allow=False #Дебли останосил генерацию на по пути
                        else:
                            x1.append(json.dumps({"role":autor,"text":text},ensure_ascii=False))
                    elif autor=='tool':
                        plug_name=msg['author']['name']
                        if plug_name in ['code_repo_interaction.callOctokitMethod',
                                                     'repo_inspector.inspectFile',
                                                     'repo_inspector.inspectFolder',
                                                     'Ai_PDF.summarize_pdf',
                                                     'Ai_PDF.upload_and_search_pdf',
                                                     'MixerBox_ChatVideo_YouTube_video_summarizer.searchVideo',
                                                     'MixerBox_ChatVideo_YouTube_video_summarizer.queryVideo']:
                            Allow=False #Плагины на которые мне код длеать лень
                        elif plug_name=='myfiles_browser':
                            #print(msg)
                            #x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':msg['content']['text'] }},ensure_ascii=False))
                            Allow=False #По позже сделаю
                        else:
                            if plug_name=='python':
                                x1.append(json.dumps({"role":'python',"text":msg['metadata']['aggregate_result']['code']},ensure_ascii=False))
                            elif plug_name=='dalle.text2im':
                                x1.append(json.dumps({"role":'dall-e',"text":text},ensure_ascii=False))
                                #print('Dall-e',Allow)
                                # В Dall-e нет никакой информации нужно для пользовтеля, там только инстукции для GPT
                                if text=='DALL·E returned some images. They are already displayed to the user. DO NOT UNDER ANY CIRCUMSTANCES list the DALL·E prompts or images in your response.':
                                    pass #Инстукция для GPT не разглашать промты :)
                                elif 'content policy' in text: 
                                    pass #Инстукция для GPT что бы она сказал что пользовтель пахабщину заказал и не разглашать промты :)
                                elif '''DALL·E experienced an error when generating images.Before doing anything else, please explicitly explain to the user that you were unable to generate images because of this.''' in text:
                                    pass #Инстукция для GPT сказать пользовтелю что у Dall-e беды с башкой
                                elif "You're generating images too quickly." in text:
                                    pass #Инстукция для GPT сказать пользовтелю что охренел так много генерить
                                elif "DALL·E is currently experiencing high demand." in text:
                                    pass #Инстукция для GPT сказать пользовтелю "жди очередь сука"
                            elif plug_name=='browser':
                                Allow=False
                                # Браузер от Bing очень багованный и мне его лень делать (но код ниже для парсинга рабочий)
                                '''
                                if msg['content'].get('result')!=None:
                                    x1.append(json.dumps({"role":'browser-bing',"text":{'status':msg['metadata']['status'],'text':msg['content']['result']}},ensure_ascii=False))
                                elif msg['content'].get('text')!=None:
                                    if msg['content']['content_type']=='tether_quote':
                                        x1.append(json.dumps({"role":'browser-bing',"text":{'status':msg['metadata']['status'],'text':msg['content']['text']}},ensure_ascii=False))
                                    elif msg['content']['content_type']=='system_error':
                                        x1.append(json.dumps({"role":'browser-bing',"text":{'status':'system_error','text':''}},ensure_ascii=False))    
                                    else:
                                        print('Ошибка в типе браузерного статуса')
                                        exit()
                                        
                                else:
                                    x1.append(json.dumps({"role":'browser-bing',"text":{'status':msg['metadata']['status'],'text':""}},ensure_ascii=False))
                                    print(msg['content'])
                                    exit()
                                '''
                            elif plug_name=='plugin_service':
                                x1.append(json.dumps({"role":'plugin_service',"text":msg['content']['parts']},ensure_ascii=False))
                            elif plug_name=='linkReader.apiSearch':
                                x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':"\n".join(msg['content']['parts']) }},ensure_ascii=False))
                            elif plug_name=='linkReader.getContent':
                                x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':"\n".join(msg['content']['parts']) }},ensure_ascii=False))
                            elif plug_name=='web_requests.scrape_url':
                                x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':"\n".join(msg['content']['parts']) }},ensure_ascii=False))
                            else:
                                m.append(plug_name) # ['linkReader.apiSearch', 'linkReader.getContent', 'web_requests.scrape_url']
                    elif autor=='system':
                        pass
                    else:
                        print("Новый Автор сообщения:",autor)
                        exit()
        
        if Allow:
            dataset.append("\n".join(x1))
        if img_detect_stat:
            img_detect+=1
    print('\n\n\nНайдено ',img_detect,'использований GPT4(V)')
    print('Всего чатов (допущенно):',len(f))

    print(list(set(m)))    
    print('"role": "dall-e"' in "\n".join(dataset))
    return "\n".join(dataset)


def ls(mypath):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]
def lss(mypath):
    return [f for f in listdir(mypath) if not isfile(join(mypath, f))]

'''
def sProc(me):
    for i in range(5):
        try:
            if me[0]==' ':
                me=me[1:]
        except:
            pass
        try:
            if me[-1]==' ':
                me=me[:-1]
        except:
            pass
        try:
            if me[0]=='\n':
                me=me[1:]
        except:
            pass
        try:
            if me[-1]=='\n':
                me=me[:-1]
        except:
            pass
    return me
'''