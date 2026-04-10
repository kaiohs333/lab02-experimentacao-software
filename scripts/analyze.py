"""
Análise e visualização de dados — Lab02: Experimentação de Software

Questões de pesquisa:
  RQ01 — Popularidade (stars)    vs qualidade (CBO, DIT, LCOM)
  RQ02 — Maturidade (age_years)  vs qualidade
  RQ03 — Atividade (releases)    vs qualidade
  RQ04 — Tamanho (loc, comments) vs qualidade

Execução:
  python scripts/analyze.py
  python scripts/analyze.py --results data/results.csv --output data/plots
"""

import os
import csv
import argparse
import statistics

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("AVISO: matplotlib não encontrado. Instale com: pip install matplotlib")

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("AVISO: scipy não encontrado. Instale com: pip install scipy")


RESULTS_CSV = "data/results.csv"
PLOTS_DIR   = "data/plots"

QUALITY_METRICS = ["cbo_median", "dit_median", "lcom_median"]
QUALITY_LABELS  = {
    "cbo_median":  "CBO (mediana)",
    "dit_median":  "DIT (mediana)",
    "lcom_median": "LCOM (mediana)",
}

RESEARCH_QUESTIONS = [
    {
        "id":       "RQ01",
        "title":    "Popularidade vs Qualidade",
        "process":  [("stars", "Estrelas")],
    },
    {
        "id":       "RQ02",
        "title":    "Maturidade vs Qualidade",
        "process":  [("age_years", "Idade (anos)")],
    },
    {
        "id":       "RQ03",
        "title":    "Atividade vs Qualidade",
        "process":  [("releases", "Nº de Releases")],
    },
    {
        "id":       "RQ04",
        "title":    "Tamanho vs Qualidade",
        "process":  [("loc_median", "LOC (mediana)"), ("comment_lines", "Linhas de Comentário")],
    },
]


def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    clean = []
    for row in rows:
        try:
            clean.append({
                "repo":          row["repo"],
                "stars":         float(row["stars"]),
                "releases":      float(row["releases"]),
                "age_years":     float(row["age_years"]),
                "comment_lines": float(row.get("comment_lines", 0) or 0),
                "loc_median":    float(row["loc_median"]) if row.get("loc_median") else None,
                "cbo_median":    float(row["cbo_median"]) if row.get("cbo_median") else None,
                "dit_median":    float(row["dit_median"]) if row.get("dit_median") else None,
                "lcom_median":   float(row["lcom_median"]) if row.get("lcom_median") else None,
            })
        except (KeyError, ValueError):
            continue
    return clean


def safe_pairs(data, x_key, y_key):
    """Retorna pares (x, y) sem None/NaN."""
    pairs = []
    for row in data:
        x = row.get(x_key)
        y = row.get(y_key)
        if x is not None and y is not None:
            pairs.append((x, y))
    return pairs


def spearman(xs, ys):
    """Correlação de Spearman e p-value."""
    if not HAS_SCIPY:
        return None, None
    if len(xs) < 3:
        return None, None
    rho, pvalue = scipy_stats.spearmanr(xs, ys)
    return round(float(rho), 4), round(float(pvalue), 6)


def print_stats(label, values):
    if not values:
        print(f"    {label}: sem dados")
        return
    med  = statistics.median(values)
    mean = statistics.mean(values)
    std  = statistics.stdev(values) if len(values) > 1 else 0
    print(f"    {label}: mediana={med:.4f}  média={mean:.4f}  dp={std:.4f}")


def plot_scatter(xs, ys, xlabel, ylabel, title, filepath, rho=None, pvalue=None):
    if not HAS_MATPLOTLIB:
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(xs, ys, alpha=0.4, s=15, color="steelblue")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if rho is not None:
        sig = "p<0.05" if pvalue is not None and pvalue < 0.05 else f"p={pvalue}"
        ax.annotate(f"Spearman ρ={rho} ({sig})",
                    xy=(0.05, 0.93), xycoords="axes fraction", fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray"))
    plt.tight_layout()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.savefig(filepath, dpi=120)
    plt.close()


def analyze(results_path, plots_dir):
    data = load_results(results_path)
    print(f"\n{len(data)} repositórios carregados de '{results_path}'.\n")

    report_lines = []

    for rq in RESEARCH_QUESTIONS:
        print(f"{'='*60}")
        print(f"{rq['id']} — {rq['title']}")
        print(f"{'='*60}")
        report_lines.append(f"\n## {rq['id']} — {rq['title']}\n")

        for proc_key, proc_label in rq["process"]:
            print(f"\n  Variável de processo: {proc_label} ({proc_key})")
            report_lines.append(f"### {proc_label}\n")

            proc_values = [row[proc_key] for row in data if row.get(proc_key) is not None]
            print_stats(proc_label, proc_values)

            for q_key in QUALITY_METRICS:
                q_label = QUALITY_LABELS[q_key]
                pairs   = safe_pairs(data, proc_key, q_key)
                if not pairs:
                    print(f"    {q_label}: sem dados suficientes")
                    continue

                xs, ys = zip(*pairs)
                rho, pvalue = spearman(xs, ys)

                sig_str = ""
                if rho is not None:
                    sig_str = f"  (Spearman ρ={rho}, p={pvalue})"
                    sig_tag = " *SIGNIFICATIVO*" if pvalue is not None and pvalue < 0.05 else ""
                    print(f"    {q_label}{sig_str}{sig_tag}")
                    report_lines.append(
                        f"- **{q_label}**: ρ={rho}, p={pvalue}{sig_tag}\n"
                    )
                else:
                    print(f"    {q_label}: {len(pairs)} pares (scipy não disponível)")

                if HAS_MATPLOTLIB:
                    plot_name = f"{rq['id']}_{proc_key}_vs_{q_key}.png"
                    plot_path = os.path.join(plots_dir, plot_name)
                    title     = f"{rq['id']}: {proc_label} vs {q_label}"
                    plot_scatter(xs, ys, proc_label, q_label, title, plot_path, rho, pvalue)

    # Salva resumo das correlações
    summary_path = os.path.join(plots_dir, "correlations_summary.txt")
    os.makedirs(plots_dir, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Resumo das Correlações de Spearman\n")
        f.writelines(report_lines)
    print(f"\nResumo salvo em '{summary_path}'.")

    if HAS_MATPLOTLIB:
        print(f"Gráficos salvos em '{plots_dir}/'.")


def main():
    parser = argparse.ArgumentParser(description="Análise e visualização — Lab02")
    parser.add_argument("--results", default=RESULTS_CSV,
                        help=f"Caminho do CSV consolidado (padrão: {RESULTS_CSV})")
    parser.add_argument("--output", default=PLOTS_DIR,
                        help=f"Diretório de saída dos gráficos (padrão: {PLOTS_DIR})")
    args = parser.parse_args()

    if not os.path.exists(args.results):
        print(f"ERRO: '{args.results}' não encontrado. Execute consolidate.py primeiro.")
        return

    analyze(args.results, args.output)


if __name__ == "__main__":
    main()
