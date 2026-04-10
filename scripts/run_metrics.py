import os
import csv
import re
import subprocess
import shutil
import statistics
import argparse

CK_JAR = "ck/ck.jar"
REPOS_CSV = "data/repositories.csv"
METRICS_DIR = "data/metrics"
CLONE_DIR = "data/repos"


def load_repositories():
    with open(REPOS_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dir_size_mb(path):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total / (1024 * 1024)


def count_comment_lines(repo_dir):
    """Conta linhas de comentário em arquivos .java (// e blocos /* */)."""
    total = 0
    for dirpath, _, filenames in os.walk(repo_dir):
        for fname in filenames:
            if not fname.endswith(".java"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Remove strings literais para não contar comentários dentro delas
                content = re.sub(r'"(?:[^"\\]|\\.)*"', '""', content)
                # Conta blocos /* ... */
                block_comments = re.findall(r'/\*.*?\*/', content, re.DOTALL)
                for block in block_comments:
                    total += block.count('\n') + 1
                # Remove blocos para não recontá-los
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                # Conta linhas com //
                for line in content.splitlines():
                    if re.search(r'//.*', line):
                        total += 1
            except Exception:
                continue
    return total


def clone_repo(repo_name, target_dir):
    url = f"https://github.com/{repo_name}.git"
    result = subprocess.run(
        ["git", "clone", "--depth=1", url, target_dir],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Erro ao clonar: {result.stderr}")


def run_ck(repo_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    result = subprocess.run(
        ["java", "-jar", CK_JAR, repo_dir, "false", "0", "false", output_dir + "/"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Erro ao rodar CK: {result.stderr}")


def parse_ck_class_csv(output_dir):
    class_csv = os.path.join(output_dir, "class.csv")
    if not os.path.exists(class_csv):
        raise Exception(f"Arquivo {class_csv} não encontrado.")

    with open(class_csv, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize_metrics(rows, repo_info, comment_lines=0):
    metrics = {"cbo": [], "dit": [], "lcom": [], "loc": []}

    for row in rows:
        try:
            metrics["cbo"].append(float(row["cbo"]))
            metrics["dit"].append(float(row["dit"]))
            metrics["lcom"].append(float(row["lcom"]))
            metrics["loc"].append(float(row["loc"]))
        except (KeyError, ValueError):
            continue

    summary = {
        "repo":          repo_info["name"],
        "stars":         repo_info["stars"],
        "forks":         repo_info["forks"],
        "created_at":    repo_info["created_at"],
        "releases":      repo_info["releases"],
        "num_classes":   len(rows),
        "comment_lines": comment_lines,
    }

    for metric, values in metrics.items():
        if values:
            summary[f"{metric}_median"] = round(statistics.median(values), 4)
            summary[f"{metric}_mean"]   = round(statistics.mean(values), 4)
            summary[f"{metric}_stdev"]  = round(statistics.stdev(values) if len(values) > 1 else 0, 4)
        else:
            summary[f"{metric}_median"] = None
            summary[f"{metric}_mean"]   = None
            summary[f"{metric}_stdev"]  = None

    return summary


def save_summary(summary, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary.keys())
        writer.writeheader()
        writer.writerow(summary)


def process_repo(repo_info, keep_clone=False, progress=""):
    repo_name = repo_info["name"]
    safe_name = repo_name.replace("/", "__")

    clone_target = os.path.join(CLONE_DIR, safe_name)
    ck_output    = os.path.join(METRICS_DIR, safe_name, "ck_output")
    summary_path = os.path.join(METRICS_DIR, f"{safe_name}.csv")

    prefix = f"[{progress}] " if progress else ""
    print(f"\n{prefix}{repo_name}")

    try:
        if os.path.exists(clone_target):
            print(f"  Já clonado, pulando clone.")
        else:
            print(f"  Clonando...", end=" ", flush=True)
            clone_repo(repo_name, clone_target)
            size_mb = dir_size_mb(clone_target)
            print(f"OK ({size_mb:.1f} MB em disco)")

        print(f"  Contando comentários...", end=" ", flush=True)
        comment_lines = count_comment_lines(clone_target)
        print(f"OK ({comment_lines} linhas)")

        print(f"  Rodando CK...", end=" ", flush=True)
        run_ck(clone_target, ck_output)
        print("OK")

        rows = parse_ck_class_csv(ck_output)
        summary = summarize_metrics(rows, repo_info, comment_lines)
        save_summary(summary, summary_path)

        print(f"  Classes: {len(rows)} | Comments: {comment_lines} | CBO={summary['cbo_median']} | DIT={summary['dit_median']} | LCOM={summary['lcom_median']} | LOC={summary['loc_median']}")

    finally:
        if not keep_clone and os.path.exists(clone_target):
            shutil.rmtree(clone_target)
            print(f"  Clone removido.")


def main():
    parser = argparse.ArgumentParser(description="Roda o CK em repositórios Java.")
    parser.add_argument("--index", type=int, default=None,
                        help="Índice do repositório no CSV (padrão: 0)")
    parser.add_argument("--all", action="store_true",
                        help="Processar todos os repositórios do CSV")
    parser.add_argument("--keep-clone", action="store_true",
                        help="Manter o repositório clonado após a análise")
    args = parser.parse_args()

    if not os.path.exists(CK_JAR):
        print(f"ERRO: '{CK_JAR}' não encontrado. Coloque o ck.jar em ck/ck.jar.")
        return

    repos = load_repositories()
    total = len(repos)

    if args.all:
        targets = list(enumerate(repos))
    else:
        idx = args.index if args.index is not None else 0
        if idx >= total:
            print(f"ERRO: índice {idx} inválido. O CSV tem {total} repositórios.")
            return
        targets = [(idx, repos[idx])]

    errors = []
    for i, (idx, repo) in enumerate(targets, start=1):
        progress = f"{idx + 1}/{total}"
        try:
            safe_name = repo["name"].replace("/", "__")
            summary_path = os.path.join(METRICS_DIR, f"{safe_name}.csv")
            if os.path.exists(summary_path):
                print(f"[{progress}] {repo['name']} — já processado, pulando.")
                continue
            process_repo(repo, keep_clone=args.keep_clone, progress=progress)
        except Exception as e:
            print(f"  ERRO: {e}")
            errors.append((repo["name"], str(e)))

    if args.all:
        print(f"\nConcluído. {total - len(errors)}/{total} repositórios processados.")
        if errors:
            print(f"Erros ({len(errors)}):")
            for name, err in errors:
                print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()
