# craft

機械判読性AIプラットフォームです。

既存の `miner` と `machine-readable-checker` は独立したAPIとして維持し、このプラットフォームからMCP経由でAI Agentが利用できるようにします。AIの処理結果はHuman Reviewで確認し、レビュー結果を将来のSkill改善につなげます。

## MVP Scope

- miner API Client
- machine-readable-checker API Client
- `analyze_table` 統合解析サービス
- MCP Server (`/mcp`)
- AnalysisResult共通モデル
- PostgreSQLへのAnalysis保存
- Human Review登録・保存

## Development

Docker Composeで起動します。

```bash
docker compose up --build
```

API:

- `GET /health`
- `POST /api/analyses`
- `GET /api/analyses`
- `GET /api/analyses/{analysis_id}`
- `DELETE /api/analyses/{analysis_id}`
- `POST /api/analyses/{analysis_id}/reviews`
- `PATCH /api/reviews/{review_id}`
- `GET /api/reviews`
- `POST /mcp`
- `GET /`

## Test

ライブラリのインストールはDocker内で行います。

```bash
docker compose run --rm app sh -lc "uv pip install --system --group dev && pytest"
```
