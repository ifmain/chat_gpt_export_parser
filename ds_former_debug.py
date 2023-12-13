from datetime import datetime
from os import system
from proc_j import *

# Get Date
current_date = datetime.now()
formatted_date = f"{current_date.strftime('%Y')[2:]}W{current_date.strftime('%U')}"



# Prepare Dataset (fine turing)
dataset=chatGPT_proc(len(lss('x1/ds_gpt4v')),'x1/ds_gpt4v')

cleaned_dataset=cleanDS(dataset)
