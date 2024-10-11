import re
import json
import pandas as pd
from collections import defaultdict

##-------------------------------------------------------------------Parsing do ficheiro ----------------------------------------------------------------

def lerProcessos(ficheiro):
    #cria uma lista de dicionários... Cada dicionário vai conter um processo com as informações do mesmo da forma key:value
    processos = []
    #Expressõe Regex para identificar um processo:
    
    
    '''
    A expressão começa com (\d+) -> procura uma sequência de 1 ou mais números referentes ao número do processo (Num_Proc), em cada intervalo de expressão regex está presente
    :: para separar as "categorias". A seguir procura uma data de nascimento representada em Regex por (\d{4}-\d{2}-\d{2}) pois é do tipo YYYY-MM-DD. De seguida utiliza
    3 vezes (.+?) para procurar por 1 ou mais caracteres para as "categorias" "Confessado", "Pai" e "Mae". Por fim, como o ficherio pode ter ou não observações, utiliza
    (.*) para procurar qualquer tipo de caracter.
    '''
    
    
    padrao = r'(\d+)::(\d{4}-\d{2}-\d{2})::(.+?)::(.+?)::(.+?)::(.*)::'
    
    #abre o ficheiro de entrada no mode de escrita, neste caso específico "processos.txt"
    #Optamos por uma abordagem mais dinâmica, visando o funcionamento do programa com vários ficheiros deste género.
    with open(ficheiro, 'r', encoding='utf-8') as f:
        # Ignora a primeira linha. Não tem informações pertinentes para a análise dos dados.
        next(f)  
        #O programa itera por todas as linhas do ficheiro, removendo todos os espaçoes em branco da mesma.
        '''
        Usa o método match() da biblioteca re para encontrar em cada linha uma expressão do tipo que foi definida anteriormente. Se fizer match com o pattern definido anteriormente
        utilizamos o método groups() para capturar num tuplo as informações de cada linha nas "categorias" pretendidas...
        Ex.: 575::1894-11-08::Aarao Pereira Silva::Antonio Pereira Silva::Francisca Campos Silva:::: -> ('575', '1894-11-08', 'Aarao Pereira Silva', 'Antonio Pereira Silva', 'Francisca Campos Silva', '')
        Após este processo, adicionamos cada informação dos tuplos à categoria correspondente no dicionário na lista processos. 
        No fim de iterar sobre todos os registos, devolvemos a lista de processos na forma de dicionários.
        '''
        for linha in f:
            linha = linha.strip()
            if linha:  # Ignorar linhas vazias
                resultado = re.match(padrao, linha)
                if resultado:
                    num_proc, data, confessado, pai, mae, observacoes = resultado.groups()
                    processo = {
                        'NumProc': num_proc,
                        'Data': data,
                        'Confessado': confessado,
                        'Pai': pai,
                        'Mae': mae,
                        'Observacoes': observacoes
                    }
                    processos.append(processo)
    return processos


##-------------------------------------------------------------------Funções Tratemento dos Dados  ----------------------------------------------------------------
##----a) Calcular a frequência de Processos por ano (primeiro elemento da data);

def freqProcessosPorAno(processos):
    anos = []
    #Itera sobre cada processo para extrair o ano
    for processo in processos:
        #Utila regex para procurar um número de 4 digitos que representa um ano qualquer na chave "Data" do dicionário "processo" da lista "processos".
        resultado = re.search(r'(\d{4})', processo['Data'])
        #se encontrar um match, o método group(1) retorna a 1ª correspondencia capturada pelo regex e adiciona esse ano à lista de anos.
        #Converte o match encontrada para int pois este está armazenado como string
        if resultado:
            ano = int(resultado.group(1))
            anos.append(ano)
    
    # Inicializa um dicionário para contar a frequência de cada ano.
    '''Itera sobre a lista de anos. Se um ano já estiver no counter, incrementa 1 à sua contagem.
    Se não estiver na lista de anos, cria a sua entrada no dicionário.
    '''
    counter = {}
    for ano in anos:
        if ano in counter:
            counter[ano] += 1
        else:
            counter[ano] = 1

    #Ordena os anos por ordem crescente
    dados_ordenados = sorted(counter.items())
    #Pretty print dos dados, com recurso a tabelas do pandas
    return pd.DataFrame(dados_ordenados, columns=["Ano", "Frequência"])


##----b) Calcular a frequência de Nomes Próprios (o primeiro em cada nome) e Apelidos (o último em cada nome) por séculos, analisando o nome do Confessado, do seu pai e da sua mãe;
def freqNomesPorSeculo(processos):
    #é criado um dicionário para fazer a contagem de nomes e apelidos por século
    nomesPorSeculo = {}

    #itera por cada processo no dicionário de processos
    for processo in processos:
        #Utiliza a expressão regular r'(\d{4})' para encontrar um qualquer ano 
        resultado = re.search(r'(\d{4})', processo['Data'])
        '''
        Se tiver algum match, converte o valor da string para inteiro. Após isso converte o ano para século (Ano//100 + 1)
        '''
        if resultado:
            ano = int(resultado.group(1))
            seculo = (ano // 100) + 1

            #Itera sobre sobre as keys dos nomes no dicionário
            #Guarda na lista numa lista de nomes os nome que encontrar
            for key in ['Confessado', 'Pai', 'Mae']:
                nomes = re.findall(r'\w+', processo[key])
                #Verifica se a lista nao esta vazia, e guarda o primeiro e ultimo nome recorrendo à indexação de listas
                if nomes:
                    nome = nomes[0]
                    apelido = nomes[-1]
                    #Introduz no dicionário criado no inicio da função os dados
                    if seculo not in nomesPorSeculo:
                        nomesPorSeculo[seculo] = {'nomes': {}, 'apelidos': {}}

                    #Contagem da frequencia de nomes por seculo
                    if nome in nomesPorSeculo[seculo]['nomes']:
                        nomesPorSeculo[seculo]['nomes'][nome] += 1
                    else:
                        nomesPorSeculo[seculo]['nomes'][nome] = 1
                    
                    #Contagem da frequencia de apelidos por seculo
                    if apelido in nomesPorSeculo[seculo]['apelidos']:
                        nomesPorSeculo[seculo]['apelidos'][apelido] += 1
                    else:
                        nomesPorSeculo[seculo]['apelidos'][apelido] = 1

    data = []
    for seculo, nomes in nomesPorSeculo.items():
        for nome, count in nomes['nomes'].items():
            data.append([seculo, "Nome Próprio", nome, count])
        for apelido, count in nomes['apelidos'].items():
            data.append([seculo, "Apelido", apelido, count])
            
    #Ordena a lista por ordem crescente
    #lambda utiliza o x como criterio de ordenação para o método sort
    data.sort(key=lambda x: x[0])  # x[0] refere-se ao século na lista
    return pd.DataFrame(data, columns=["Século", "Tipo", "Nome/Apelido", "Frequência"])


##----Calcular a frequência de processos que são Recomendados por, pelo menos, um Tio (referido no campo Observações quando este está presente);
## A nossa função retorna também quais os processos que têm essa recomendação
def freqProcessosComRecomendacaoTio(processos):
    # Cria uma lista para armazenar os IDs dos processos que têm a recomendação de "Tio"
    idProcessosTio = []

    # Itera sobre cada processo na lista de processos
    for processo in processos:
        # Verifica se "Tio" está presente nas observações (ignora case)
        if re.search(r'tio', processo['Observacoes'], re.IGNORECASE):
            idProcessosTio.append(processo['NumProc'])  # Adiciona o ID do processo à lista

    # Retorna a contagem e os IDs dos processos
    return len(idProcessosTio)


def paisComMaisDeUmFilho(processos):
    # Cria um dicionário para contar quantos filhos cada pai tem
    counterPais = {}
    
    for processo in processos:
        pai = processo['Pai']
        # Adiciona uma contagem para o pai, usando regex para garantir que o nome esteja formatado corretamente
        if re.match(r'^[A-Za-zÀ-ÿ\s]+$', pai):  # Regex para permitir apenas letras e espaços
            if pai in counterPais:
                counterPais[pai] += 1
            else:
                counterPais[pai] = 1

    # Filtra os pais que têm mais de um filho
    pais_multiplicados = []
    for pai, count in counterPais.items():
        if count > 1:
            pais_multiplicados.append(pai)

    # Ordena os nomes dos pais em ordem crescente
    pais_multiplicados.sort()

    # Retorna um DataFrame com os nomes dos pais
    return pd.DataFrame(pais_multiplicados, columns=["Pai"])

def primeiroRegistroJson(processos):
    if processos:
        return json.dumps(processos[0], ensure_ascii=False, indent=4)
    return None

from jinja2 import Environment, FileSystemLoader

def gerarHtml(freqAno, freqNomes, freqTios, paisMultiplicados, primeiroReg):
    # Configura o ambiente do Jinja2
    env = Environment(loader=FileSystemLoader('.'))  # Diretório atual
    template = env.get_template('template.html')  # Carrega o template

    # Renderiza o template com os dados
    html_content = template.render(
        freqAno=freqAno.to_html(index=False, classes='dataframe'),
        freqNomes=freqNomes.to_html(index=False, classes='dataframe'),
        freqTios=freqTios,
        paisMultiplicados=paisMultiplicados.to_html(index=False, classes='dataframe'),
        primeiroReg=primeiroReg
    )

    # Salva o conteúdo renderizado em um arquivo HTML
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    nomeFicheiro = input("Insira o nome do ficheiro de entrada (ex: processos.txt): ")
    processos = lerProcessos(nomeFicheiro)

    freqAno = freqProcessosPorAno(processos)
    freqNomes = freqNomesPorSeculo(processos)
    freqTios = freqProcessosComRecomendacaoTio(processos)
    paisMultiplicados = paisComMaisDeUmFilho(processos)
    primeiroReg = primeiroRegistroJson(processos)

    # Gerar a página HTML
    gerarHtml(freqAno, freqNomes, freqTios, paisMultiplicados, primeiroReg)

    # Imprimir apenas o primeiro registro em JSON no console
    print("Primeiro Registo em JSON:", primeiroReg)

main()
