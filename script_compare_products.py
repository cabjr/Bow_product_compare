from pandas_ods_reader import read_ods
import numpy as np
import re
import csv
from pyexcel_ods import save_data
from collections import OrderedDict
import sys
import unicodedata

itens_pedido = []
vocab = []
array_of_sentences = []
auxStr = ''
pedido = []
orcamento = []

def remove_accents(word):
    replaces = [('é','e'), ('ç','c'), ('ó','o'), ('ê', 'e'),('ã', 'a'),('.',''),(',','')]
    for a,b in replaces:
        word = word.replace(a,b)
    return word

def extraction_word(sentence):
    ignorar = [',', 'e','com', 'de', 'para', 'com', '.']
    palavras = re.sub("[^\w]", " ",  sentence).split()
    texto = [ remove_accents(w.lower()) for w in palavras if w not in ignorar]
    return texto

def tokenize(sentences):
    palavras = []
    for sentence in sentences:
        w = extraction_word(sentence)
        palavras.extend(w)
    palavras = sorted(list(set(palavras)))
    return palavras

def generate_bow(allsentences):
    global itens_pedido, vocab
    itens_pedido =[]
    vocab = []
    vocab = tokenize(allsentences)
    for sentence in allsentences:
        words = extraction_word(sentence)
        bag_vector = np.zeros(len(vocab))
        for w in words:
            for i,word in enumerate(vocab):
                if word == w: 
                    bag_vector[i] += 1   
        itens_pedido.append(np.array(bag_vector))            
        
def generate_vector(descricao):
    words = extraction_word(descricao)
    bag_vector = np.zeros(len(vocab))
    for w in words:
        for i,word in enumerate(vocab):
            if word == w: 
                bag_vector[i] += 1
    return bag_vector

def count_words(sent1, sent2):
    count_sent1 = 0
    count_sent2 = 0
    for x in range(0,len(sent1)):
        if (sent1[x] > 0):
            count_sent1 = count_sent1 + 1
    for x in range(0,len(sent1)):
        if (sent1[x] > 0 and sent2[x] > 0):
            count_sent2 = count_sent2 + 1
    percent = count_sent2 / count_sent1
    
    return percent
            
def test_sentence(descricao):
    global array_of_sentences, auxStr
    aux = generate_vector(descricao)
    listPossible = []
    for j in itens_pedido:
        listPossible.append( count_words(j, aux) * 100)
    auxStr = auxStr + descricao + ', ' + str(max(listPossible)) + ', ' + str(listPossible.index(max(listPossible))) + ', ' + array_of_sentences[listPossible.index(max(listPossible))] + '\n'
    return listPossible.index(max(listPossible)), max(listPossible)

def check_items(listOfItems):
    listOfResults = []
    ind = 0
    for i in listOfItems:
        match,percent = test_sentence(i)
        listOfResults.append([i, match, percent, ind])
        ind += 1
    return listOfResults

def generate_comparison(items_pedido, items_orcamento):
    aux = ''
    itens = check_items(items_orcamento)
    aux = 'Item, Descrição, quantidade, Descrição Item orçamento, quantidade item orçamento, probabilidade acerto \n'
    for i in range(0,len(items_pedido)):
        for j in range(0,len(itens)):
            if (i == itens[j][1]):
                vlr = 0
                if (pedido['quantidade'][i] == orcamento['quantidade'][itens[j][3]]):
                    vlr = 40
                aux = aux + str(i+1)+ ',' + items_pedido[i] + ','+ str(pedido['quantidade'][i]) +' , ' + itens[j][0] + ', '+ str(orcamento['quantidade'][itens[j][3]]) +' , ' + str(itens[j][2]+vlr) + ' %\n'
                break
            elif j == len(itens)-1:
                aux = aux + str(i+1) +' ,' + items_pedido[i]+', , , , \n'
    return aux

def splitString_to_list(varStr):
    varStr = varStr.splitlines()
    listData = []
    for line in varStr:
        aux = []
        auxStr = line.split(',')
        for item in auxStr:
            aux.append(item)
        listData.append(aux)
    return listData

def generate_odsFile(listOrcamentos):
    data = OrderedDict()
    for item in range(len(listOrcamentos)):
        data.update({"Orçamento "+str(item+1): listOrcamentos[item]})
    save_data("resultado.ods", data)


def main(inputPedido, inputOrcamentos):
    global pedido, orcamento
    path = inputPedido
    auxResults = []
    pedido = read_ods(path, 1, columns=["Item", "Descrição", "quantidade"])
    for i in range(len(pedido['Descrição'])):
        array_of_sentences.append(pedido['Descrição'][i])
    generate_bow(array_of_sentences)
    for item in inputOrcamentos:
        orcamento = read_ods(item, 1, columns=["Item", "Descrição", "quantidade"])
        result = generate_comparison(array_of_sentences, orcamento['Descrição'])
        print(result)
        auxResults.append((result))

    auxList = []
    print (auxResults)
    for item in auxResults:
        auxList.append(splitString_to_list(item))
    generate_odsFile(auxList)

if (len(sys.argv)==1):
    print('Favor inserir nome do arquivo de pedido e nomes dos arquivos de orçamento.')
elif (len(sys.argv)==2):
    print('Favor inserir nome dos arquivos de orçamento')
elif (len(sys.argv)>=3):
    listOrcamentos = [ sys.argv[item] for item in range(len(sys.argv)) if item > 1 ]
    main(sys.argv[1], listOrcamentos)
    print('Arquivo resultado.ods gerado com sucesso.')
    print(vocab)