import os
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"bearer {GITHUB_TOKEN}"}
OUTPUT_FILE = "data/repositories.csv"
TOTAL_REPOS = 1000
PAGE_SIZE = 50

QUERY = """
query($cursor: String) {
  search(query: "language:Java sort:stars", type: REPOSITORY, first: 50, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
        forkCount
        createdAt
        releases {
          totalCount
        }
        primaryLanguage {
          name
        }
      }
    }
  }
}
"""


def fetch_page(cursor=None, retries=5):
    variables = {"cursor": cursor}
    for attempt in range(1, retries + 1):
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": QUERY, "variables": variables},
            headers=HEADERS,
        )
        if response.status_code in (502, 503, 504):
            wait = 2 ** attempt
            print(f"  Erro {response.status_code}, tentativa {attempt}/{retries}. Aguardando {wait}s...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(f"Erro na API GraphQL: {data['errors']}")
        return data["data"]["search"]
    raise Exception(f"Falha após {retries} tentativas.")


def collect_repositories():
    os.makedirs("data", exist_ok=True)
    repos = []
    cursor = None
    page = 1

    print(f"Coletando top-{TOTAL_REPOS} repositórios Java do GitHub...")

    while len(repos) < TOTAL_REPOS:
        print(f"  Página {page} ({len(repos)}/{TOTAL_REPOS} repos coletados)...")

        result = fetch_page(cursor)
        nodes = result["nodes"]

        for node in nodes:
            repos.append({
                "name": node["nameWithOwner"],
                "stars": node["stargazerCount"],
                "forks": node["forkCount"],
                "created_at": node["createdAt"],
                "releases": node["releases"]["totalCount"],
                "language": node["primaryLanguage"]["name"] if node["primaryLanguage"] else "N/A",
            })

        if not result["pageInfo"]["hasNextPage"]:
            print("  Sem mais páginas disponíveis.")
            break

        cursor = result["pageInfo"]["endCursor"]
        page += 1

        # Respeitar rate limit da API
        time.sleep(1)

    # Limitar exatamente a 1000
    repos = repos[:TOTAL_REPOS]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "stars", "forks", "created_at", "releases", "language"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repos)

    print(f"\nPronto! {len(repos)} repositórios salvos em '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    collect_repositories()
