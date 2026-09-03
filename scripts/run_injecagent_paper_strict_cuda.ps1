$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
.\.venv\Scripts\python.exe scripts\train_wami_paper_strict.py `
  --data data\injecagent_wami.jsonl `
  --epochs 20 `
  --batch-size 64 `
  --device cuda `
  --save wami_paper_strict_injecagent_e20_cuda.pt `
  --output-md data\wami_paper_strict_injecagent_e20_cuda.md `
  --output-csv data\wami_paper_strict_injecagent_e20_cuda.csv `
  --log-file data\wami_paper_strict_injecagent_e20_cuda.progress.csv `
  *> data\wami_paper_strict_injecagent_e20_cuda.combined.log
