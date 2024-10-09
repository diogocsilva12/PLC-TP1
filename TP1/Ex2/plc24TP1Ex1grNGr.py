import re
import json

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
    idades = [int(linha[5]) for linha in dados if re.match(r'^\d+$', linha[5])]
    return min(idades), max(idades) if idades else (None, None)

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
        distribuicaoModalidade[ano] = dict(sorted(distribuicaoModalidade[ano].items()))
    
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
            
    # Calcular porcentagens
    for ano, contagens in distribuicaoAprovacao.items():
        total = contagens['aprovado'] + contagens['nao_aprovado']
        contagens['percentagem_aprovado'] = (contagens['aprovado'] / total) * 100 if total > 0 else 0
        contagens['percentagem_nao_aprovado'] = (contagens['nao_aprovado'] / total) * 100 if total > 0 else 0

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
    with open('index.html', 'w') as f:
        f.write('<html><body>')
        f.write('<h1>Relatório de Exames Médicos Desportivos</h1>')
        f.write(f'<h2>Idades Extremas: {idadesExtremas[0]} - {idadesExtremas[1]}</h2>')
        
        f.write('<h2>Distribuição por Gênero:</h2>')
        for genero, contagem in distribuicaoGenero.items():
            f.write(f'<p>{genero}: {contagem}</p>')

        f.write('<h2>Distribuição por Modalidade por Ano:</h2>')
        for ano, modalidades in distribuicaoModalidade.items():
            f.write(f'<h3>Ano {ano}</h3><ul>')
            for modalidade, contagem in modalidades.items():
                f.write(f'<li>{modalidade}: {contagem}</li>')
            f.write('</ul>')

        f.write('<h2>Porcentagem de Aptos e Não Aptos por Ano:</h2>')
        for ano, percentagens in distribuicaoAprovacao.items():
            f.write(f'<h3>Ano {ano}</h3>')
            f.write(f'<p>Aptos: {percentagens["percentagem_aprovado"]:.2f}%</p>')
            f.write(f'<p>Não Aptos: {percentagens["percentagem_nao_aprovado"]:.2f}%</p>')

        f.write('</body></html>')

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
