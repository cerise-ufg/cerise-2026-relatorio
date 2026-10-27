# Artefatos publicados em Releases

Release sugerido: **`v2026.10.26`** — "Relatório Técnico-Científico CERISE 2026 (versão de 26/10/2026)".

Os arquivos abaixo são cópias idênticas dos arquivos finais versionados neste repositório (raiz e pasta
`roteiro/`), publicadas no Release apenas para download direto (sem clonar o repositório).

| Arquivo | Tamanho | SHA-256 | Conteúdo |
|---|---|---|---|
| `Relatorio_CERISE_2026_Eduardo_Caixeta.pdf` | 9.213.895 bytes (8,8 MiB) | `ed98627abaa2684867413deef34827da8f772230da5a6e31eb495587386c5232` | Relatório final em PDF (77 páginas) |
| `Relatorio_CERISE_2026_Eduardo_Caixeta.docx` | 22.751.131 bytes (21,7 MiB) | `5d75550e4f20d4de55a51b774989f59593b0fa4990f853a79337e44422c0c109` | Relatório final em Word |
| `Roteiro_CERISE_2026_Eduardo_Caixeta.pdf` | 3.806.827 bytes (3,6 MiB) | `bc9dc9e441e46d62f68f4595cdabce3643a6e85069a8fb69f65163408c75f986` | Roteiro de Implementação CERISE 2026 em PDF (69 páginas) |
| `Roteiro_CERISE_2026_Eduardo_Caixeta.docx` | 8.730.257 bytes (8,3 MiB) | `46cbcd694a3b1c30b8b4760faf028b8acf1a29cef9e1203a6a6d35f01895de34` | Roteiro de Implementação CERISE 2026 em Word |
| `SHA256SUMS.txt` | 430 bytes | — | Somas SHA-256 dos quatro arquivos acima |

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

Os arquivos não são compactados nem divididos em partes: basta abrir os PDFs ou os `.docx` baixados.
