# Artefatos publicados em Releases

Release sugerido: **`v2026.10.26`** — "Relatório Técnico-Científico CERISE 2026 (versão de 26/10/2026)".

Os dois arquivos abaixo são cópias idênticas dos arquivos finais versionados na raiz deste repositório,
publicadas no Release apenas para download direto (sem clonar o repositório).

| Arquivo | Tamanho | SHA-256 | Conteúdo |
|---|---|---|---|
| `Relatorio_CERISE_2026_Eduardo_Caixeta.pdf` | 9.192.614 bytes (8,8 MiB) | `a87042e316e319af0b58af4c06e3c27f723644eab9385fdc0a3ec7148445ccfa` | Relatório final em PDF (74 páginas) |
| `Relatorio_CERISE_2026_Eduardo_Caixeta.docx` | 22.747.695 bytes (21,7 MiB) | `1a3ec6a921f1a72ff9f906c513551cb0bfa95dd3cecdf5d92260b58e5983448c` | Relatório final em Word |
| `SHA256SUMS.txt` | 217 bytes | — | Somas SHA-256 dos dois arquivos acima |

## Como baixar e conferir

Pela página de Releases do repositório no GitHub, ou com o GitHub CLI:

```bash
gh release download v2026.10.26 -R cerise-ufg/cerise-2026-relatorio
sha256sum -c SHA256SUMS.txt
```

No Windows (PowerShell):

```powershell
Get-FileHash .\Relatorio_CERISE_2026_Eduardo_Caixeta.pdf -Algorithm SHA256
```

Os arquivos não são compactados nem divididos em partes: basta abrir o PDF ou o `.docx` baixado.
