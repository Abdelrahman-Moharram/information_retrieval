import os
import re
def remove_white_spaces(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()


def read_files(path):
    list_files = []
    files = os.listdir(path)
    for file in files:
        filename = os.fsdecode(file)
        with open(path+"/"+filename) as f:
            Str = ''
            for a in f.read().split("\n"):
                if a:
                    Str += a
            list_files.append(Str)
            Str = ''            
        
    # for i in range(1,size+1,1):
    #     with open("file/"+str(i)+".txt") as f:
    #         for a in f.read().split("\n"):
    #             Str = ''
    #             if a != "":
    #                 Str += a
    #         list_files.append(Str)
    return list_files, files



def preprocess(list_files):
    new_list = []
    for _file in list_files:
        for p in "!.,:@#$%^&?<>*()[}{]-=;/\"\\\t\n":
            String = ''
            if p in '\n;?:!.,.':
                _file = _file.replace(p,' ')
            else:
                _file = _file.replace(p,'')
        new_list.append(remove_white_spaces(_file.lower()).split())
    return new_list


def positionalIndex(list_files):
    indexs = {}
    indexs_iteration = {}
    for file in range(len(list_files)):
        for word in range(len(list_files[file])):
            if not list_files[file][word] in indexs:
                indexs[list_files[file][word]] = [(file,word)]
            else:
                indexs[list_files[file][word]].append((file,word))
    
    for index in indexs:
        indexs_iteration[index] = len(indexs[index])
    for index in indexs_iteration:
        print("-->",index, " : ", "repeated ->",indexs_iteration[index], " Times in indexes ",indexs[index])
    print("\n")
    return indexs, indexs_iteration

def phrase_query(indexs, text, files_names):
    rows = []
    list_result = {}
    indexs = indexs[0]
    for file in indexs:
        for word in range(len(text)-1):
            if text[word] == file:
                for nested_index in indexs[file]:
                    nested_row = []
                    for index_word in range(len(text)):
                        if (nested_index[0], nested_index[1]+index_word) in indexs[text[index_word]]:
                            nested_row.append(nested_index[1]+index_word)
                        else:
                            nested_row = []
                    if len(nested_row) == len(text):
                            if not files_names[nested_index[0]] in list_result:
                                list_result[files_names[nested_index[0]]] = [tuple(nested_row)]
                            else:
                                list_result[files_names[nested_index[0]]].append(tuple(nested_row))
    
        
    
    for file in files_names:
        if file not in list_result:
            list_result[file] = "Not Availble !"
            
                
    return list_result
                        
                    
        
                



def Control(list_files, files_names):
    len_files = len(files_names)
    if len_files > 1:
        print(len_files, " Files Found")
    elif len_files == 1:
        print("1 File Found")
    else:
        return "\nNo Files in this directory\n"
    ##################################          get text from user      ####################################
    
    txt = input("--> ")
    for p in "!.,:@#$%^&?<>*()[}{]-=;/\"\\\t\n":
            String = ''
            if p in '\n;?:!.,.':
                txt = txt.replace(p,' ')
            else:
                txt = txt.replace(p,'')
    txt = remove_white_spaces(txt)
    print(txt)
    text = txt.lower().split()
    if len(text) < 2:       # if text is less than 2 words will restart this function
        print("\nplease enter 2 words or more!\n")
        return Control(list_files, files_names)
    
    print("\nMaking Positional Index ...\n")
    indexs = positionalIndex(list_files)
    # print("indexs -->",indexs,"\n\n\n")
    
    #########################################################################################################
    phrase = phrase_query(indexs, text, files_names)
    for index in phrase:
        print("-->",index, " : ",phrase[index])
    print("\n")
    return phrase


files = read_files("files")

Control(preprocess(files[0]), files[1])