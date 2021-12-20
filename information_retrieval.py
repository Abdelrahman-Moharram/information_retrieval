import os
import re
import glob
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
import string
from collections import Counter
import numpy as np
from collections import OrderedDict
from tabulate import tabulate

##################################              utils               ####################################
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
    
        
    
    # for file in files_names:
    #     if file not in list_result:
    #         list_result[file] = "Not Availble !"
            
    print("list_result: ",list_result)
    return list_result


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
    text = txt.lower().split()
    if len(text) < 2:  
        print("\nplease enter 2 words or more!\n")
        return Control(list_files, files_names)
    
    print("\nMaking Positional Index ...\n")
    indexs = positionalIndex(list_files)
    
    #########################################################################################################
    phrase = phrase_query(indexs, text, files_names)
    for index in phrase:
        print("-->",index, " : ",phrase[index])
    print("\n")
    return indexs, phrase, txt

def query(txt, idf):
    tf_idf = {}
    sum = 0
    weights = Weights(termFrequency(txt.split(" ")))
    for w in weights:
        tf_idf[w] = idf[w] * weights[w]
    for word in tf_idf:
        sum += tf_idf[word]
    print("\n\n\nquery_weights",weights,"\n\nquery_tf_idf",tf_idf,"\nquery_tf_idf_sum:", sum)
    return tf_idf, sum

def vectorSpaceModel(tf_dict, idf, s):
    file_tf_weight = {}
    file_tf_idf = {}
    files_weights_sums = {}
    similarity_doc_query = {}
    for file in tf_dict:
        f_weight = Weights(tf_dict[file])
        file_tf_weight[file] = f_weight
    print("\n\n\nf_weight ",file_tf_weight," \n\n")
    
    for file in file_tf_weight:
        file_tf_idf[file] = {}
        sum = 0
        for word in file_tf_weight[file]:
            file_tf_idf[file][word] = file_tf_weight[file][word] * idf[word]
            sum += file_tf_idf[file][word]
        files_weights_sums[file] = sum
    
    for w in files_weights_sums:
        similarity_doc_query[w] = files_weights_sums[w] * s
    print("\n\n\nfile_tf_idf ",file_tf_idf," \n\n files_weights_sums: ", files_weights_sums, "\n\nsimilarity_doc_query: ",similarity_doc_query)
    
    return file_tf_weight, file_tf_idf, files_weights_sums, similarity_doc_query
        


def controller(list_files, files_names):
    p_index, phrase, txt = Control(list_files, files_names)
    docs = []
    for file in list_files:
        docs +=file
    
    print("docs: ", docs,"\n\nlist_files : ",list_files,"\n\nfiles_names: ", files_names,"\n\npositional index: ", p_index,"\n\nPhrase : ", phrase)
    
    
    
    
    
    # M = len(docs)

    unique_words = list(set(docs))
    
    tf = termFrequency(docs)
    print("\n\n=>tf: ", tf)
    
    tf_dict = termFrequencyInDoc([list_files,files_names])
    print("\n\n\n\ntf_dict: ",tf_dict)
    weight = Weights(tf) 
    print("\n\n\nWeights: ",weight)
    

    # print("\n\n\ntf_idf: ",tf_idf,"\n\n\n")
    df = DocFreq(list_files, unique_words)
    print("\n\n\n\n\n\ndf",df)
    idf = inverseDocFre(files_names, df)
    print("\n\n\n\nidf",idf,"\n")
    query_tf_idf, s = query(txt, idf)
    file_tf_weight, file_tf_idf, files_weights_sums, similarity_doc_query = vectorSpaceModel(tf_dict, idf, s)
    tf_idf = tfidf(weight, idf) 
    print("\n\n\n\ntf_idf",tf_idf,"\n")
    
    
    view_list = []
    for x  in tf:
        view_list.append([x, tf[x], weight[x], idf[x]])
    print(tabulate(view_list, headers=['word', 'tf','Weights', 'idf'], tablefmt='orgtbl'))
    
    for file in file_tf_weight:
        view_list = []
        print("_"*100,"\n\n",file,"\n")
        for x  in file_tf_weight[file]:
            view_list.append([x, file_tf_weight[file][x], file_tf_idf[file][x], tf_dict[file][x]])
        print(tabulate(view_list, headers=['word', 'df_dict','idf_dict', 'tf_dict'], tablefmt='orgtbl'), "\n\n",files_weights_sums[file], " * ", s, " = ",  similarity_doc_query[file],"\n","_"*100)
    


files = read_files("files")


controller(preprocess(files[0]), files[1])
# control1(files)