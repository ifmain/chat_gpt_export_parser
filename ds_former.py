from datetime import datetime
from os import system
from proc_j import *
import time

# Get Date
current_date = datetime.now()
formatted_date = f"{current_date.strftime('%Y')[2:]}W{current_date.strftime('%U')}"

# Prepare Dataset
dataset=chatGPT_proc(len(lss('x1/chats')),'x1/chats')
cleaned_dataset=cleanDS(dataset)

#print('"role": "dall-e"' in dataset)
#print('"role": "dall-e"' in cleaned_dataset)


system(f'cd dss && mkdir {formatted_date} && cd ..')

#Write Dataset
s=open(f'dss/{formatted_date}/gpt2.5_{formatted_date}_gpt4.txt','w',encoding='utf-8')
s.write(cleaned_dataset)
s.write('\n')
s.write(open(r'x1\math.jsonl',encoding='UTF-8').read())
s.write(open(r'x1\transalte.jsonl',encoding='UTF-8').read())
s.write(open(r'x1\remove_obj.jsonl',encoding='UTF-8').read())
s.write(open(r'x1\yolo.jsonl',encoding='UTF-8').read())

#Add alpaca dataset (legacy)
add_llama=False

if add_llama:
    s.write(open(r'x1\alpaca_gpt4_data.jsonl',encoding='UTF-8').read())
    s.write(open(r'x1\gpt4alpaca.json',encoding='UTF-8').read())

s.close()
time.sleep(4)
# Prepare Dataset (fine turing)
dataset=chatGPT_proc(len(lss('x1/chats2')),'x1/chats2')
cleaned_dataset=cleanDS(dataset)

#Write Dataset (fine turing)
s=open(f'dss/{formatted_date}/gpt2.5_{formatted_date}_fineturn.txt','w',encoding='utf-8')
s.write(cleaned_dataset)
s.write('\n')
s.close()
