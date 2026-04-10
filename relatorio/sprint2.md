# Sprint 2 — Lab02: Experimentação de Software

## 1. O que foi pedido

A Sprint 2 tinha como objetivo executar a coleta completa de métricas e produzir a análise dos dados para responder às questões de pesquisa do laboratório. Os entregáveis exigidos foram:

- **Arquivo `.csv`** com o resultado das medições de todos os 1.000 repositórios
- **Hipóteses informais** sobre o que se espera encontrar em cada questão de pesquisa
- **Análise e visualização de dados** com medidas de tendência central (mediana, média, desvio padrão)
- **Relatório final** contendo introdução, metodologia, resultados e discussão para cada RQ
- **(Bônus)** Gráficos de correlação e teste estatístico de Spearman

---

## 2. O que foi feito

### 2.1 Atualização da coleta de métricas (`scripts/run_metrics.py`)

O script da Sprint 1 foi estendido para coletar também as **linhas de comentário** de cada repositório, exigidas como métrica de tamanho no enunciado. Como o CK não fornece esse dado, foi implementada a função `count_comment_lines()`, que percorre todos os arquivos `.java` do clone e contabiliza:

- Linhas com comentário de linha (`//`)
- Linhas dentro de blocos de comentário (`/* ... */`)

O campo `comment_lines` passa a ser salvo no CSV de resumo de cada repositório.

### 2.2 Consolidação dos resultados (`scripts/consolidate.py`)

Script Python que mescla todos os arquivos `data/metrics/<repo>.csv` individuais em um único arquivo `data/results.csv`. Além da mesclagem, calcula automaticamente o campo `age_years` — a idade do repositório em anos — a partir do campo `created_at`, para uso na análise de maturidade (RQ02).

### 2.3 Análise e visualização (`scripts/analyze.py`)

Script Python que, a partir do `data/results.csv`, responde às quatro questões de pesquisa:

| Questão | Variável de processo | Métricas de qualidade |
|---|---|---|
| RQ01 — Popularidade | Estrelas (`stars`) | CBO, DIT, LCOM |
| RQ02 — Maturidade | Idade em anos (`age_years`) | CBO, DIT, LCOM |
| RQ03 — Atividade | Nº de releases (`releases`) | CBO, DIT, LCOM |
| RQ04 — Tamanho | LOC mediana + linhas de comentário | CBO, DIT, LCOM |

Para cada par, o script:

1. Calcula a **correlação de Spearman** (ρ e p-value)
2. Gera um **gráfico de dispersão** com a anotação do ρ
3. Salva o resumo das correlações em `data/plots/correlations_summary.txt`

### 2.4 Ferramentas utilizadas

- **Python 3** com as bibliotecas `matplotlib` e `scipy`
- **CK 0.7.0** para análise estática dos repositórios Java
- **Teste de correlação de Spearman** (`scipy.stats.spearmanr`) para análise estatística
- **Matplotlib** para geração dos gráficos de dispersão

### 2.5 Estrutura do projeto ao final da Sprint 2

```
lab02-experimentacao-software/
├── data/
│   ├── repositories.csv        # Lista dos 1.000 repositórios coletados
│   ├── results.csv             # Consolidação de todos os repositórios analisados
│   ├── metrics/
│   │   └── <repo>.csv          # Métricas sumarizadas de cada repositório
│   └── plots/
│       ├── RQ01_stars_vs_cbo_median.png
│       ├── ...                 # Gráficos de dispersão por RQ
│       └── correlations_summary.txt
├── scripts/
│   ├── collect_repos.py        # Coleta os 1.000 repositórios via GitHub API
│   ├── run_metrics.py          # Clona repositório, conta comentários e executa o CK
│   ├── consolidate.py          # Mescla os CSVs individuais em results.csv
│   └── analyze.py              # Gera correlações e gráficos por RQ
└── relatorio/
    ├── sprint1.md
    └── sprint2.md              # Este documento
```

---

## 3. Como executar

```bash
# 1. Ativar o ambiente virtual
source .venv/bin/activate

# 2. Instalar dependências de análise
pip install matplotlib scipy

# 3. Processar todos os repositórios (pode demorar várias horas)
python scripts/run_metrics.py --all

# 4. Consolidar os CSVs individuais em data/results.csv
python scripts/consolidate.py

# 5. Gerar análise e gráficos
python scripts/analyze.py
```

---

## 4. Dificuldades encontradas

### 4.1 Ausência de linhas de comentário no CK

O enunciado define linhas de comentário como métrica de tamanho, mas a ferramenta CK não fornece esse dado em seu output. O arquivo `class.csv` gerado pelo CK contém diversas métricas por classe, mas nenhuma relacionada a comentários.

**Solução:** implementar a contagem diretamente no script `run_metrics.py`, percorrendo os arquivos `.java` do repositório clonado com expressões regulares para identificar comentários de linha (`//`) e blocos (`/* ... */`).

### 4.2 Dependências de análise não inclusas no ambiente original

O ambiente virtual criado na Sprint 1 continha apenas `requests` e `python-dotenv`. As bibliotecas `matplotlib` e `scipy`, necessárias para geração de gráficos e cálculo de Spearman, não estavam instaladas.

**Solução:** instalar as dependências adicionais dentro do mesmo ambiente virtual com `pip install matplotlib scipy`.
