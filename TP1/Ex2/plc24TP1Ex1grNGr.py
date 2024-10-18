import re
import json
from jinja2 import Environment, FileSystemLoader


#TODO -> Comentar código


def lerDados(caminhoArquivo):
    with open(caminhoArquivo, 'r') as arquivo:
        cabecalho = arquivo.readline().strip().split(',')
        dados = []
        for linha in arquivo:
            # Usando regex para dividir a linha em colunas
            linhaDividida = re.split(r',(?=(?:[^"]|"[^"]*")*$)', linha.strip())
            dados.append(linhaDividida)
    return cabecalho, dados

def calcularIdadesExtremas(dados):
    idades = []
    for linha in dados:
        if re.match(r'^\d+$', linha[5]):
            idades.append(int(linha[5]))
    
    if idades:
        return min(idades), max(idades)
    else:
        return None, None

def calcularDistribuicaoGenero(dados):
    contagemGenero = {'M': 0, 'F': 0}
    for linha in dados:
        genero = linha[6]
        if genero in contagemGenero:
            contagemGenero[genero] += 1
    return contagemGenero

def calcularDistribuicaoModalidade(dados):
    distribuicaoModalidade = {}
    for linha in dados:
        anoCorrespondente = re.search(r'(\d{4})-(\d{2})-(\d{2})', linha[2])
        if anoCorrespondente:
            ano = anoCorrespondente.group(1)
            modalidade = linha[8]
            if ano not in distribuicaoModalidade:
                distribuicaoModalidade[ano] = {}
            if modalidade not in distribuicaoModalidade[ano]:
                distribuicaoModalidade[ano][modalidade] = 0
            distribuicaoModalidade[ano][modalidade] += 1

    # Ordenar modalidades alfabeticamente dentro de cada ano
    for ano in distribuicaoModalidade:
        modalidadesOrdenadas = sorted(distribuicaoModalidade[ano].items())
        distribuicaoModalidade[ano] = {}
        for modalidade, contagem in modalidadesOrdenadas:
            distribuicaoModalidade[ano][modalidade] = contagem

    return distribuicaoModalidade

def calcularPercentagemAprovacao(dados):
    distribuicaoAprovacao = {}
    for linha in dados:
        anoCorrespondente = re.search(r'(\d{4})-(\d{2})-(\d{2})', linha[2])
        if anoCorrespondente:
            ano = anoCorrespondente.group(1)
            aprovado = re.match(r'true', linha[11].strip(), re.IGNORECASE)
            if ano not in distribuicaoAprovacao:
                distribuicaoAprovacao[ano] = {'aprovado': 0, 'nao_aprovado': 0}
            if aprovado:
                distribuicaoAprovacao[ano]['aprovado'] += 1
            else:
                distribuicaoAprovacao[ano]['nao_aprovado'] += 1
            
    # Calcular percentagens
    for ano in distribuicaoAprovacao:
        total = distribuicaoAprovacao[ano]['aprovado'] + distribuicaoAprovacao[ano]['nao_aprovado']
        if total > 0:
            distribuicaoAprovacao[ano]['percentagem_aprovado'] = (distribuicaoAprovacao[ano]['aprovado'] / total) * 100
            distribuicaoAprovacao[ano]['percentagem_nao_aprovado'] = (distribuicaoAprovacao[ano]['nao_aprovado'] / total) * 100
        else:
            distribuicaoAprovacao[ano]['percentagem_aprovado'] = 0
            distribuicaoAprovacao[ano]['percentagem_nao_aprovado'] = 0

    return distribuicaoAprovacao

def normalizarNomes(dados):
    nomesIncorretos = []
    for linha in dados:
        primeiroNome = linha[3].strip()
        ultimoNome = linha[4].strip()
        genero = linha[6]

        if genero == 'M' and primeiroNome and ultimoNome:
            nomesIncorretos.append((ultimoNome, primeiroNome))  # Eles estão trocados
        elif genero == 'F' and primeiroNome and ultimoNome:
            nomesIncorretos.append((primeiroNome, ultimoNome))  # Ordem correta
    return nomesIncorretos

def escreverJson(nomesIncorretos, caminhoArquivo):
    with open(caminhoArquivo, 'w') as arquivoJson:
        json.dump(nomesIncorretos, arquivoJson, indent=4)

def gerarRelatorioHtml(idadesExtremas, distribuicaoGenero, distribuicaoModalidade, distribuicaoAprovacao):
    # Carregar o template Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')

    # Renderizar o template com os dados
    output = template.render(
        idadesExtremas=idadesExtremas,
        distribuicaoGenero=distribuicaoGenero,
        distribuicaoModalidade=distribuicaoModalidade,
        distribuicaoAprovacao=distribuicaoAprovacao
    )

    # Escrever o conteúdo renderizado no arquivo HTML
    with open('index.html', 'w') as f:
        f.write(output)

def main():
    cabecalho, dados = lerDados('emd.csv')
    idadesExtremas = calcularIdadesExtremas(dados)
    distribuicaoGenero = calcularDistribuicaoGenero(dados)
    distribuicaoModalidade = calcularDistribuicaoModalidade(dados)
    distribuicaoAprovacao = calcularPercentagemAprovacao(dados)
    nomesIncorretos = normalizarNomes(dados)

    escreverJson(nomesIncorretos, 'nomes_incorretos.json')
    gerarRelatorioHtml(idadesExtremas, distribuicaoGenero, distribuicaoModalidade, distribuicaoAprovacao)

if __name__ == "__main__":
    main()
