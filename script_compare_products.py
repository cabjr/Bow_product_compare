from pandas_ods_reader import read_ods
import numpy as np
import re
import csv

itens_pedido = []
vocab = []
array_of_sentences = []
auxStr = ''

def extraction_word(sentence):
    ignorar = [',', 'e','com', 'de', 'para', 'com']
    palavras = re.sub("[^\w]", " ",  sentence).split()
    texto = [w.lower() for w in palavras if w not in ignorar]
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
    #print(aux)
    listPossible = []
    for j in itens_pedido:
        #listPossible.append( (1 - np.mean(aux!=j)) * 100)
        listPossible.append( count_words(j, aux) * 100)
    #print(len(listPossible))
    #print(listPossible)
    auxStr = auxStr + descricao + ', ' + str(max(listPossible)) + ', ' + str(listPossible.index(max(listPossible))) + ', ' + array_of_sentences[listPossible.index(max(listPossible))] + '\n'
    #print (descricao + ' - ' + str(max(listPossible)) + ' - ' + str(listPossible.index(max(listPossible))) + ' - ' + array_of_sentences[listPossible.index(max(listPossible))])
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
    print('Itens pedido: ' + str(items_pedido))
    print('Itens Orçamento: ' + str(items_orcamento))
    aux = 'Item, Descrição, quantidade, Descrição Item orçamento, quantidade item orçamento, probabilidade acerto \n'
    for i in range(0,len(items_pedido)):
        for j in range(0,len(itens)):
            if (i == itens[j][1]):
                vlr = 0
                if (pedido['quantidade'][i] == orcamento['quantidade'][itens[j][3]]):
                    vlr = 50
                aux = aux + str(i+1)+ ',' + items_pedido[i] + ','+ str(pedido['quantidade'][i]) +' , ' + itens[j][0] + ', '+ str(orcamento['quantidade'][itens[j][3]]) +' , ' + str(itens[j][2]+vlr) + ' %\n'
                break
            elif j == len(itens)-1:
                aux = aux + str(i+1) +' ,' + items_pedido[i]+', , , , \n'
    return aux

path = "./pedido.ods"
path2 = "./orcamento.ods"
pedido = read_ods(path, 1, columns=["Item", "Descrição", "quantidade"])
orcamento = read_ods(path2, 1, columns=["Item", "Descrição", "quantidade"])

print('****** PEDIDO ******')
print (pedido)
print('****** ORÇAMENTO ******')
print (orcamento)


for i in range(len(pedido['Descrição'])):
    array_of_sentences.append(pedido['Descrição'][i])

generate_bow(array_of_sentences)

print ( ' --------------------------------- ')
result = generate_comparison(array_of_sentences, orcamento['Descrição'])

print(result)
#print(auxStr)

file1 = open("test.csv","w") 
file1.writelines(result)
file1.close() 

