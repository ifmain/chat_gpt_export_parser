from datetime import datetime
from os import system
from proc_j import *
import time

# Get Date
current_date = datetime.now()
formatted_date = f"{current_date.strftime('%Y')[2:]}W{current_date.strftime('%U')}"


# Prepare Dataset (fine turing)
dataset=chatGPT_proc(len(lss('x1/poly')),'x1/poly')
cleaned_dataset=cleanDS(dataset)

#Write Dataset (fine turing)
s=open(f'dss/testnet_{formatted_date}.txt','w',encoding='utf-8')
s.write(cleaned_dataset)
s.write('\n')
s.close()
