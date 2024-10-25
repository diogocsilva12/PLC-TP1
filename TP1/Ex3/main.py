import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader

# Carregar o dataset
dataset = pd.read_csv('myheart.csv')

# a) Calcular a percentagem da Doença no total da amostra e por Género
doentes = dataset[dataset['temDoença'] == 1]
percentagem_total = len(doentes) / len(dataset) * 100
percentagem_genero = doentes['sexo'].value_counts(normalize=True) * 100

# b) Calcular a distribuição da Doença por Escalões Etários
escaloes = pd.cut(dataset['idade'], bins=range(30, 75, 5))
distribuicao_idade = doentes['idade'].groupby(escaloes).count()

# c) Calcular a distribuição da Doença por níveis de colesterol
colesterol_bins = range(0, 401, 10)  # Alterar conforme necessário
distribuicao_colesterol = doentes['colesterol'].groupby(pd.cut(doentes['colesterol'], bins=colesterol_bins)).count()

# d) Determinar se há alguma correlação significativa entre a Tensão ou o Batimento e a ocorrência de doença
correlacao_tensao = dataset['tensão'].corr(dataset['temDoença'])
correlacao_batimento = dataset['batimento'].corr(dataset['temDoença'])

# e) Criar gráficos para as distribuições
plt.figure(figsize=(12, 6))

# Gráfico da distribuição por Género
plt.subplot(1, 3, 1)
percentagem_genero.plot(kind='bar', color=['blue', 'pink'])
plt.title('Distribuição por Género')
plt.xlabel('Género')
plt.ylabel('Percentagem')

# Gráfico da distribuição por Idade
plt.subplot(1, 3, 2)
distribuicao_idade.plot(kind='bar', color='lightgreen')
plt.title('Distribuição por Escalões Etários')
plt.xlabel('Escalões Etários')
plt.ylabel('Número de Doentes')

# Gráfico da distribuição por Colesterol
plt.subplot(1, 3, 3)
distribuicao_colesterol.plot(kind='bar', color='salmon')
plt.title('Distribuição por Níveis de Colesterol')
plt.xlabel('Níveis de Colesterol')
plt.ylabel('Número de Doentes')

plt.tight_layout()
plt.savefig('distribuicoes.png')
plt.close()

# Gerar HTML com Jinja2
idades_extremas = (dataset['idade'].min(), dataset['idade'].max())
template_loader = FileSystemLoader('.')
template_env = Environment(loader=template_loader)
template = template_env.get_template('template.html')

# Criar contexto para o template
contexto = {
    'idadesExtremas': idades_extremas,
    'distribuicaoGenero': percentagem_genero.to_dict(),
    'distribuicaoIdade': distribuicao_idade.to_dict(),
    'distribuicaoColesterol': distribuicao_colesterol.to_dict(),
    'correlacaoTensao': correlacao_tensao,
    'correlacaoBatimento': correlacao_batimento
}

# Gerar o HTML
html_output = template.render(contexto)
with open('index.html', 'w') as f:
    f.write(html_output)

print("Processamento concluído. Verifique o arquivo index.html.")
