import os

def getFileInfo(cur_path):
    cur_filename = cur_path.split(os.sep)[-1]
    file_parts = cur_filename.split(".")
    file_prefix = file_parts[0]
    ch_num = int(file_prefix.replace("ch","").replace("_clean",""))
    file_lang = file_parts[1]
    return cur_filename, file_prefix, file_lang, ch_num