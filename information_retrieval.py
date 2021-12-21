import os
import re
import numpy as np
from tabulate import tabulate






##################################              utils               ####################################

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

    return list_files, files

def word_str_count(word, string):
    if word not in string:
        return 0
    counter = 0
    for w in string.split(" "):
        if word == w:
            counter +=1
    return counter

def remove_white_spaces(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()

def clear_str(string):
    for p in "!.,:@#$%^&?<>*()[}{]-=;/\"\\\t\n":
        String = ''
        if p in '\n;?:!.,.':
            string = string.replace(p,' ')
        else:
            string = string.replace(p,'')
    return remove_white_spaces(string).lower()
def preprocess(list_files):
    new_list = []
    for _file in list_files:
        if isinstance(_file, list):
            _file=" ".join(_file)
        new_list.append(clear_str(_file).split())
    return new_list

#########################################################################################################

##################################              phase-2               ####################################

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
    
        
    
    # for file in files_names:
    #     if file not in list_result:
    #         list_result[file] = "Not Availble !"
            
    return list_result
#########################################################################################################

##################################              phase-3               ####################################

def DocFreq(list_files, unique_words):
    df = {}
    for word in unique_words:
        counter = 0
        for file in list_files:
            if word in file:
                counter +=1
        df[word] = counter
    return df



def termFrequency(docs):
    df_docs = {}
    for word in docs:
        word = word.strip()
        if not word:
            continue
        df_docs[word] = word_str_count(word, " ".join(docs))
    return df_docs

def termFrequencyInDoc(docs):
    files = {}
    for doc, file in zip(docs[0], docs[1]):
        files[file] = termFrequency(doc)
    return files

    

def Weights(tf):
    tf_weights= {}
    for word in tf:
        tf_weights[word] = 1+np.log10(tf[word])
    return tf_weights

def inverseDocFre(files_names, df):
    idf = {}
    len_files = len(files_names)
    for term in df:
        idf[term] = np.log10(len_files/df[term])
    return idf
    

def tfidf(weight, idf):
    tf_idf = {}
    for word in weight:
        tf_idf[word] = weight[word] * idf[word]
    return tf_idf        




def Control(list_files, files_names):
    txt = clear_str(input("--> ")).lower()
    text = txt.split()
    if len(text) < 2:  
        print("\nplease enter 2 words or more!\n")
        return Control(list_files, files_names)
    flag = True
    for file in list_files:
        if  txt in " ".join(file):
            flag = False
    if flag:
         print("\nthis text not available please try again with different words !\n")
         return Control(list_files, files_names)
    
    
    len_files = len(files_names)
    if len_files > 1:
        print(len_files, " Files Found")
    elif len_files == 1:
        print("1 File Found")
    else:
        return "\nNo Files in this directory\n"
    ##################################          get text from user      ####################################


    
    print("\nMaking Positional Index ...\n")
    indexs = positionalIndex(list_files)
    
    #########################################################################################################
    phrase = phrase_query(indexs, text, files_names)
    # for index in phrase:
    #     print("-->",index, " : ",phrase[index])
    # print("\n")
    print("_"*150, "\n\t\t\t\t\t\t\t\tphrase query\n","_"*150,"\n")
    
    view_list = []
    for x  in phrase:
        view_list.append([x, phrase[x]])
    print(tabulate(view_list, headers=['word', 'phrase'], tablefmt='orgtbl'), "\n\n\n")
    return indexs, phrase, txt

def query(txt, idf):
    tf_idf = {}
    sum = 0
    weights = Weights(termFrequency(txt.split(" ")))
    for w in weights:
        tf_idf[w] = idf[w] * weights[w]
    for word in tf_idf:
        sum += tf_idf[word]
    return weights, tf_idf, sum

def vectorSpaceModel(tf_dict, idf, s):
    file_tf_weight = {}
    file_tf_idf = {}
    files_weights_sums = {}
    similarity_doc_query = {}
    for file in tf_dict:
        f_weight = Weights(tf_dict[file])
        file_tf_weight[file] = f_weight
    # print("\n\n\nf_weight ",file_tf_weight," \n\n")
    
    for file in file_tf_weight:
        file_tf_idf[file] = {}
        sum = 0
        for word in file_tf_weight[file]:
            file_tf_idf[file][word] = file_tf_weight[file][word] * idf[word]
            sum += file_tf_idf[file][word]
        files_weights_sums[file] = sum
    
    for w in files_weights_sums:
        similarity_doc_query[w] = files_weights_sums[w] * s
    # print("\n\n\nfile_tf_idf ",file_tf_idf," \n\n files_tfidf_sums: ", files_weights_sums, "\n\nsimilarity_doc_query: ",similarity_doc_query)
    
    return file_tf_weight, file_tf_idf, files_weights_sums, similarity_doc_query
        


def printer(title,unique_words, files):
    print("_"*150, "\n\t\t\t\t\t\t\t\t", title,"\n","_"*150,"\n")
    
    files_names = ["word"]
    
    for file in files:
        files_names.append(file)
    row = []
    rows = []
    for word in unique_words:
        
        row = []
        row.append(word)
        for file in files:
            if word in files[file]:
                row.append(files[file][word])
            else:
                row.append(0)
        rows.append(row)
    print(tabulate(rows, headers=files_names, tablefmt='orgtbl'),"\n\n")
#########################################################################################################
        

def controller(list_files, files_names):
    p_index, phrase, txt = Control(list_files, files_names)
    docs = []
    for file in list_files:
        docs +=file
    
    # print("docs: ", docs,"\n\nlist_files : ",list_files,"\n\nfiles_names: ", files_names,"\n\npositional index: ", p_index,"\n\nPhrase : ", phrase)
    
    
    
    
    
    # M = len(docs)
    # print("\n\n=>docs: ", docs)

    unique_words = list(set(docs))
    
    tf = termFrequency(docs)
    
    tf_dict = termFrequencyInDoc([list_files,files_names])
    printer("tf_dict",unique_words, tf_dict)
    weight = Weights(tf) 
    

    # print("\n\n\ntf_idf: ",tf_idf,"\n\n\n")
    df = DocFreq(list_files, unique_words)
    idf = inverseDocFre(files_names, df)
    query_weights, query_tf_idf, query_sum = query(txt, idf)
    file_tf_weight, file_tf_idf, files_weights_sums, similarity_doc_query = vectorSpaceModel(tf_dict, idf, query_sum)
    printer("file tf weight",unique_words, file_tf_weight)
    tf_idf = tfidf(weight, idf) 
    # print("\n\n\n\ntf_idf",tf_idf,"\n")
    # print("\n\n\nWeights: ",weight)
    
    # print("\n\n\nfiles_weights_sums: ",files_weights_sums)
    # print("\n\n\nsimilarity_doc_query: ",similarity_doc_query,"\n\n")
    



    
    # for file in file_tf_weight:
    #     view_list = []
    #     print("_"*100,"\n\n",file,"\n")
    #     for x  in file_tf_weight[file]:
    #         view_list.append([x, file_tf_weight[file][x], file_tf_idf[file][x], tf_dict[file][x]])
    #     print(tabulate(view_list, headers=['word', 'df_dict','idf_dict', 'tf_dict'], tablefmt='orgtbl'), "\n\n",files_weights_sums[file], " * ", s, " = ",  similarity_doc_query[file],"\n","_"*100)
    
    print("_"*150, "\n\t\t\t\t\t\t\t\tdf - idf\n","_"*150,"\n")
    
    view_list = []
    for x  in tf:
        view_list.append([x, df[x], idf[x]])
    print(tabulate(view_list, headers=['word', 'df','idf'], tablefmt='orgtbl'),"\n\n\n")
    
    
    printer("file tf idf",unique_words, file_tf_idf)
    
    print("query_weights",query_weights,"\n\nquery_tf_idf",query_tf_idf,"\nquery_tf_idf_sum:", query_sum,"\n\n\n")

    view_list = []
    for x  in files_weights_sums:
        view_list.append([x, files_weights_sums[x]])
    print(tabulate(view_list, headers=['word', 'files_weights_sums'], tablefmt='orgtbl'), "\n\n\n")
    

    view_list = []
    for x  in similarity_doc_query:
        view_list.append([x, str(files_weights_sums[x]) + " * " + str(query_sum) + " = "+ str(similarity_doc_query[x])])
    print(tabulate(view_list, headers=['word', 'similarity_doc_query'], tablefmt='orgtbl'), "\n\n\n")

files = read_files("files")

controller(preprocess(files[0]), files[1])
