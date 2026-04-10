import os
import csv
from datetime import datetime, timezone

METRICS_DIR = "data/metrics"
OUTPUT_FILE = "data/results.csv"
REFERENCE_DATE = datetime.now(timezone.utc)


def calculate_age_years(created_at_str):
    """Calcula a idade do repositório em anos a partir de created_at (ISO 8601)."""
    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    delta = REFERENCE_DATE - created_at
    return round(delta.days / 365.25, 2)


def load_summary_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[0] if rows else None


def consolidate():
    csv_files = [
        f for f in os.listdir(METRICS_DIR)
        if f.endswith(".csv") and os.path.isfile(os.path.join(METRICS_DIR, f))
    ]

    if not csv_files:
        print(f"Nenhum CSV encontrado em '{METRICS_DIR}'.")
        return

    print(f"Consolidando {len(csv_files)} arquivos de métricas...")

    rows = []
    errors = []

    for fname in sorted(csv_files):
        path = os.path.join(METRICS_DIR, fname)
        try:
            row = load_summary_csv(path)
            if row is None:
                continue
            row["age_years"] = calculate_age_years(row["created_at"])
            rows.append(row)
        except Exception as e:
            errors.append((fname, str(e)))
            print(f"  AVISO: erro ao ler {fname}: {e}")

    if not rows:
        print("Nenhuma linha consolidada.")
        return

    fieldnames = list(rows[0].keys())
    # Garante que age_years aparece logo após created_at
    if "age_years" in fieldnames and "created_at" in fieldnames:
        fieldnames.remove("age_years")
        idx = fieldnames.index("created_at") + 1
        fieldnames.insert(idx, "age_years")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nPronto! {len(rows)} repositórios consolidados em '{OUTPUT_FILE}'.")
    if errors:
        print(f"Erros em {len(errors)} arquivo(s):")
        for fname, err in errors:
            print(f"  - {fname}: {err}")


if __name__ == "__main__":
    consolidate()
