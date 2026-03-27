# Sprint 1 — Lab02: Experimentação de Software

## 1. O que foi pedido

A Sprint 1 tinha como objetivo preparar a infraestrutura de coleta e medição de dados para o laboratório. Os entregáveis exigidos foram:

- **Lista dos top-1.000 repositórios Java** mais populares do GitHub
- **Script de automação** para clone de repositórios e coleta de métricas via ferramenta CK
- **Arquivo `.csv`** com o resultado das medições de ao menos 1 repositório

---

## 2. O que foi feito

### 2.1 Coleta dos repositórios (`scripts/collect_repos.py`)

Script Python que utiliza a **API GraphQL do GitHub** para buscar os 1.000 repositórios Java mais populares por número de estrelas.

Para cada repositório, são coletados:

| Campo | Descrição |
|---|---|
| `name` | Nome no formato `owner/repo` |
| `stars` | Número de estrelas (popularidade) |
| `forks` | Número de forks |
| `created_at` | Data de criação (maturidade) |
| `releases` | Número de releases (atividade) |
| `language` | Linguagem principal |

O resultado é salvo em `data/repositories.csv`.

### 2.2 Coleta de métricas (`scripts/run_metrics.py`)

Script Python que, dado um repositório da lista:

1. Clona o repositório localmente com `git clone --depth=1` (apenas o commit mais recente, sem histórico)
2. Executa o **CK** (`ck/ck.jar`) sobre o código clonado
3. Lê o arquivo `class.csv` gerado pelo CK
4. Calcula **mediana, média e desvio padrão** das métricas de qualidade por repositório
5. Salva o resumo em `data/metrics/<repo>.csv`
6. Remove o clone local automaticamente para economizar espaço

As métricas de qualidade coletadas pelo CK são:

| Métrica | Descrição |
|---|---|
| `CBO` | Coupling Between Objects — acoplamento entre classes |
| `DIT` | Depth Inheritance Tree — profundidade da árvore de herança |
| `LCOM` | Lack of Cohesion of Methods — falta de coesão entre métodos |
| `LOC` | Lines of Code — linhas de código por classe |

### 2.3 Ferramentas utilizadas

- **Python 3** com as bibliotecas `requests` e `python-dotenv`
- **GitHub GraphQL API** para coleta dos repositórios
- **CK 0.7.0** (ferramenta de análise estática para Java)
- **Git** para clonagem dos repositórios
- **Ambiente virtual Python** (`.venv`) para isolamento de dependências

### 2.4 Estrutura do projeto ao final da Sprint 1

```
lab02-experimentacao-software/
├── .env                        # Token de acesso ao GitHub
├── .venv/                      # Ambiente virtual Python
├── ck/
│   └── ck.jar                  # Ferramenta CK 0.7.0
├── data/
│   ├── repositories.csv        # Lista dos 1.000 repositórios coletados
│   └── metrics/
│       └── <repo>.csv          # Métricas sumarizadas de cada repositório
├── scripts/
│   ├── collect_repos.py        # Coleta os 1.000 repositórios via GitHub API
│   └── run_metrics.py          # Clona repositório e executa o CK
└── relatorio/
    └── sprint1.md              # Este documento
```

---

## 3. Como executar

```bash
# 1. Ativar o ambiente virtual
source .venv/bin/activate

# 2. Coletar os 1.000 repositórios
python scripts/collect_repos.py

# 3. Rodar o CK em um repositório (ex: índice 0 = mais popular)
python scripts/run_metrics.py --index 0

# Para rodar em todos os repositórios (Sprint 2)
python scripts/run_metrics.py --all
```

---

## 4. Dificuldades encontradas

### 4.1 Erro 502 na API GraphQL do GitHub

A primeira versão do script utilizava `first: 100` (100 repositórios por página). Isso causava erro **502 Bad Gateway** consistentemente, pois a query era muito pesada — o campo `releases { totalCount }` exige que o GitHub busque dados de releases para todos os 100 repositórios de uma vez.

**Solução:** reduzir o tamanho da página de 100 para 50 (`first: 50`), o que tornou a query leve o suficiente para ser processada sem erros.

### 4.2 Ambiente Python gerenciado pelo Homebrew

Ao tentar instalar as dependências com `pip3 install`, o sistema bloqueou a instalação com o erro `externally-managed-environment`, pois o Python estava sendo gerenciado pelo Homebrew no macOS.

**Solução:** criar um ambiente virtual com `python3 -m venv .venv` e instalar as dependências dentro dele.

### 4.3 Download do CK jar

O repositório oficial do CK no GitHub não disponibilizava o `.jar` diretamente nos releases via API.

**Solução:** localizar a versão mais recente (0.7.0) no **Maven Central** e fazer o download diretamente de lá.
