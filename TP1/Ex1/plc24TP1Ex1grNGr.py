import re
import pandas as pd

##-------------------------------------------------------------------Parsing do ficheiro ----------------------------------------------------------------
def lerProcessos(ficheiro):
    #cria uma lista de dicionários... Cada dicionário vai conter um processo com as informações do mesmo da forma key:value
    processos = []
    
    #Expressões Regex para identificar um processo:
    
    '''
    A expressão começa com (\d+) -> procura uma sequência de 1 ou mais números referentes ao número do processo (Num_Proc), em cada intervalo de expressão regex está presente
    :: para separar as "categorias". A seguir procura uma data de nascimento representada em Regex por (\d{4}-\d{2}-\d{2}) pois é do tipo YYYY-MM-DD. De seguida utiliza
    3 vezes (.+?) para procurar por 1 ou mais caracteres para as "categorias" "Confessado", "Pai" e "Mae". Por fim, como o ficheiro pode ter ou não observações, utiliza
    (.*) para procurar qualquer tipo de caracter.
    '''
    padrao = r'(\d+)::(\d{4}-\d{2}-\d{2})::(.+?)::(.+?)::(.+?)::(.*)::'
    
    #abre o ficheiro de entrada no mode de escrita, neste caso específico "processos.txt"
    #Optamos por uma abordagem mais dinâmica, visando o funcionamento do programa com vários ficheiros deste género.
    with open(ficheiro, 'r', encoding='utf-8') as f:
        # Ignora a primeira linha. Não tem informações pertinentes para a análise dos dados.
        next(f)
        #O programa itera por todas as linhas do ficheiro, removendo todos os espaços em branco da mesma.
        '''
        Usa o método match() da biblioteca re para encontrar em cada linha uma expressão do tipo que foi definida anteriormente. Se fizer match com o pattern definido anteriormente
        utilizamos o método groups() para capturar num tuplo as informações de cada linha nas "categorias" pretendidas...
        Ex.: 575::1894-11-08::Aarao Pereira Silva::Antonio Pereira Silva::Francisca Campos Silva:::: -> ('575', '1894-11-08', 'Aarao Pereira Silva', 'Antonio Pereira Silva', 'Francisca Campos Silva', '')
        Após este processo, adicionamos cada informação dos tuplos à categoria correspondente no dicionário na lista processos. 
        No fim de iterar sobre todos os registos, devolvemos a lista de processos na forma de dicionários.
        '''
        for linha in f:
            linha = linha.strip() # Ignora linhas vazias
            if linha: 
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

##-------------------------------------------------------------------Funções Tratamento dos Dados  ----------------------------------------------------------------
##----a) Calcular a frequência de Processos por ano (primeiro elemento da data);

def freqProcessosPorAno(processos):
    anos = []
    #Itera sobre cada processo para extrair o ano
    for processo in processos:
        #Utiliza regex para procurar um número de 4 digitos que representa um ano qualquer na chave "Data" do dicionário "processo" da lista "processos".
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
    data.sort(key=lambda x: x[0])
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
            idProcessosTio.append(processo['NumProc'])
    # Retorna a contagem e os IDs dos processos
    return len(idProcessosTio)

##----Calcula a frequencia de pais com mais de um filho

def paisComMaisDeUmFilho(processos):
    # Cria um dicionário para contar quantos filhos cada pai tem
    counterPais = {}
    for processo in processos:
        pai = processo['Pai']
        # Adiciona uma contagem para o pai, usando regex para garantir que o nome esteja formatado corretamente
        if re.match(r'^[A-Za-zÀ-ÿ\s]+$', pai):# Regex para permitir apenas letras e espaços
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


#Processamento opcional/adicional: calcula a frequência por parentesco de recomendação
def freqRecomendacoesFamiliares(processos):
    parentescos = {
        'Tio': 0,
        'Tia': 0,
        'Avô': 0,
        'Avó': 0,
        'Primo': 0,
        'Prima': 0,
        'Irmão': 0,
        'Irmã': 0
    }
    
    for processo in processos:
        observacoes = processo['Observacoes']
        
        for parentesco in parentescos.keys():
            if re.search(fr'\b{parentesco}\b', observacoes, re.IGNORECASE):
                parentescos[parentesco] += 1

    # Retornar a contagem dos tipos de recomendações em formato de DataFrame
    data = [{'Parentesco': k, 'Frequência': v} for k, v in parentescos.items() if v > 0]
    return pd.DataFrame(data, columns=['Parentesco', 'Frequência'])

#Gera um ficheiro HTML
def gerarHtml(freqAno, freqNomes, freqTios, paisMultiplicados, recomendacoesFamiliares, primeiroReg):
    primeiroReg_json = (
        "{\n"
        f'    "NumProc": "{primeiroReg["NumProc"]}",\n'
        f'    "Data": "{primeiroReg["Data"]}",\n'
        f'    "Confessado": "{primeiroReg["Confessado"]}",\n'
        f'    "Pai": "{primeiroReg["Pai"]}",\n'
        f'    "Mae": "{primeiroReg["Mae"]}",\n'
        f'    "Observacoes": "{primeiroReg["Observacoes"]}"\n'
        "}"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultados do Processador de Róis de Confessados</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
            h1, h2 {{ color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #fff; }}
            th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            pre {{ background-color: #f4f4f4; padding: 10px; border: 1px solid #ccc; overflow: auto; }}
            #topButton {{ position: fixed; bottom: 20px; right: 20px; background-color: #333; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; display: none; }}
            #topButton:hover {{ background-color: #555; }}
        </style>
    </head>
    <body>
        <h1>Resultados do Processador de Róis de Confessados</h1>

        <h2>Índice</h2>
        <ul>
            <li><a href="#freqAno">a) Frequência de Processos por Ano</a></li>
            <li><a href="#freqNomes">b) Frequência de Nomes Próprios e Apelidos por Século</a></li>
            <li><a href="#freqTios">c) Frequência de Processos com Recomendação de Tio</a></li>
            <li><a href="#paisMultiplicados">d) Pais com mais de um Filho Confessado</a></li>
            <li><a href="#recomendacoesFamiliares">e) Recomendações de Familiares</a></li>
            <li><a href="#primeiroReg">f) Primeiro Registo em JSON</a></li>
        </ul>

        <h2 id="freqAno">Frequência de Processos por Ano</h2>
        {freqAno.to_html(index=False, classes='dataframe')}

        <h2 id="freqNomes">Frequência de Nomes Próprios e Apelidos por Século</h2>
        {freqNomes.to_html(index=False, classes='dataframe')}

        <h2 id="freqTios">Frequência de Processos com Recomendação de Tio:</h2>
        <p>{freqTios}</p>

        <h2 id="paisMultiplicados">Pais com mais de um Filho Confessado:</h2>
        {paisMultiplicados.to_html(index=False, classes='dataframe')}

        <h2 id="recomendacoesFamiliares">Recomendações de Familiares e Tipos de Tios</h2>
        <h3>Recomendações de Familiares</h3>
        {recomendacoesFamiliares.to_html(index=False, classes='dataframe')}
        

        <h2 id="primeiroReg">Primeiro Registo em JSON</h2>
        <pre>{primeiroReg_json}</pre>

        <button id="topButton" onclick="scrollToTop()">Voltar ao Topo</button>

        <script>
            window.onscroll = function() {{scrollFunction()}};
            function scrollFunction() {{
                const topButton = document.getElementById("topButton");
                if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {{
                    topButton.style.display = "block";
                }} else {{
                    topButton.style.display = "none";
                }}
            }}
            function scrollToTop() {{
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            }}
        </script>
    </body>
    </html>
    """

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
    recomendacoesFamiliares = freqRecomendacoesFamiliares(processos)
    
    #Primeiro registo como dicionário para o primeiro registo do json
    primeiroReg = processos[0] if processos else {}

    gerarHtml(freqAno, freqNomes, freqTios, paisMultiplicados, recomendacoesFamiliares, primeiroReg)
    print("Operação realizada!")

main()

