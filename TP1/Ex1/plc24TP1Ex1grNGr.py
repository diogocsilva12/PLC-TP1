import re
import json
from collections import Counter, defaultdict

def lerProcessos(ficheiro):
    processos = []
    padrao = r'(\d+)::(\d{4}-\d{2}-\d{2})::(.+?)::(.+?)::(.+?)::(.*)::'
    
    with open(ficheiro, 'r', encoding='utf-8') as f:
        next(f)  # Ignorar a primeira linha (cabeçalho)
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

def freqProcessosPorAno(processos):
    anos = [int(re.search(r'(\d{4})', processo['Data']).group(1)) for processo in processos]
    contador = {}  # Dicionário para contar as ocorrências dos anos

    for ano in anos:
        if ano in contador:
            contador[ano] += 1  # Se o ano já existe, aumenta a contagem
        else:
            contador[ano] = 1  # Se não existe, inicia a contagem em 1

    return contador

def freqNomesPorSeculo(processos):
    nomesSeculo = {}  # Usando um dicionário normal em vez de defaultdict
    for processo in processos:
        ano = int(re.search(r'(\d{4})', processo['Data']).group(1))
        seculo = (ano // 100) + 1

        # Captura os nomes do Confessado, Pai e Mãe
        for key in ['Confessado', 'Pai', 'Mae']:
            nomes = re.findall(r'\w+', processo[key])  # Captura todos os nomes
            
            if nomes:  # Se houver nomes
                primeiroNome = nomes[0]  # Primeiro nome
                ultimoNome = nomes[-1]  # Último nome
                # Inicializa se não existir
                if seculo not in nomesSeculo:
                    nomesSeculo[seculo] = {'nomes': {}, 'apelidos': {}}
                
                # Contagem dos nomes
                nomesSeculo[seculo]['nomes'][primeiroNome] = nomesSeculo[seculo]['nomes'].get(primeiroNome, 0) + 1
                # Contagem dos sobrenomes
                nomesSeculo[seculo]['apelidos'][ultimoNome] = nomesSeculo[seculo]['apelidos'].get(ultimoNome, 0) + 1

    return nomesSeculo

def freqProcessosComRecomendacaoTio(processos):
    counter = 0
    for processo in processos:
        if re.search(r'Tio', processo['Observacoes']):
            counter += 1
    return counter

def paisComMaisDeUmFilho(processos):
    counterPais = defaultdict(int)
    for processo in processos:
        pai = processo['Pai']
        counterPais[pai] += 1
    return [pai for pai, count in counterPais.items() if count > 1]

def primeiroRegistroJson(processos):
    if processos:
        return json.dumps(processos[0], ensure_ascii=False, indent=4)
    return None

def gerarHtml(freqAno, freqNomes, freqTios, paisMultiplicados, primeiroReg):
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="pt">\n')
        f.write('<head>\n')
        f.write('<meta charset="UTF-8">\n')
        f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        f.write('<title>Resultados do Processador de Róis de Confessados</title>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('<h1>Resultados do Processador de Róis de Confessados</h1>\n')

        f.write('<h2>Frequência de Processos por Ano</h2>\n')
        f.write('<ul>\n')
        for ano, freq in freqAno.items():
            f.write(f'<li>{ano}: {freq}</li>\n')
        f.write('</ul>\n')

        f.write('<h2>Frequência de Nomes Próprios e Apelidos por Século</h2>\n')
        for seculo, nomes in freqNomes.items():
            f.write(f'<h3>Século {seculo}</h3>\n')
            f.write('<h4>Nomes Próprios</h4>\n')
            f.write('<ul>\n')
            for nome, count in nomes['nomes'].items():
                f.write(f'<li>{nome}: {count}</li>\n')
            f.write('</ul>\n')
            f.write('<h4>Apelidos</h4>\n')
            f.write('<ul>\n')
            for apelido, count in nomes['apelidos'].items():
                f.write(f'<li>{apelido}: {count}</li>\n')
            f.write('</ul>\n')

        f.write(f'<h2>Frequência de Processos com Recomendação de Tio:</h2>\n')
        f.write(f'<p>{freqTios}</p>\n')

        f.write('<h2>Pais com mais de um Filho Confessado:</h2>\n')
        f.write('<ul>\n')
        for pai in paisMultiplicados:
            f.write(f'<li>{pai}</li>\n')
        f.write('</ul>\n')

        f.write('<h2>Primeiro Registo em JSON</h2>\n')
        f.write('<pre>\n')
        f.write(primeiroReg)
        f.write('</pre>\n')

        f.write('</body>\n')
        f.write('</html>\n')

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

if __name__ == "__main__":
    main()
