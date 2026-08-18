# craft

機械判読性AIプラットフォームです。

既存の `miner` と `machine-readable-checker` は独立したAPIとして維持し、このプラットフォームからMCP経由でAI Agentが利用できるようにします。AIの処理結果はHuman Reviewで確認し、レビュー結果を将来のSkill改善につなげます。

## MVP Scope

- miner API Client
- machine-readable-checker API Client
- `analyze_table` 統合解析サービス
- Chat UI上のAIがMCP経由で判断案を記録する協業フロー
- MCP Server (`/mcp`)
- AnalysisResult共通モデル
- PostgreSQLへのAnalysis保存
- Human Review登録・保存

## Development

Docker Composeで起動します。

```bash
docker compose up --build
```

MCPクライアント接続手順は [docs/mcp-client.md](docs/mcp-client.md) を参照してください。

API:

- `GET /health`
- `POST /api/analyses`
- `GET /api/analyses`
- `GET /api/analyses/{analysis_id}`
- `DELETE /api/analyses/{analysis_id}`
- `PATCH /api/analyses/{analysis_id}/agent`
- `POST /api/analyses/{analysis_id}/reviews`
- `PATCH /api/reviews/{review_id}`
- `GET /api/reviews`
- `POST /mcp`
- `GET /`

AIとの協業:

- craftはLLM APIを直接呼びません。
- ChatGPT/CodexなどのChat UI上のAIがMCP経由で`analyze_table`を実行します。
- AIは返ってきたAnalysisResultを会話内で人と確認し、判断案を`record_agent_judgement`または`PATCH /api/analyses/{analysis_id}/agent`で保存します。
- APIが返した事実、AIが行った判断、人が行ったReviewを分離して保持します。

## Test

ライブラリのインストールはDocker内で行います。

```bash
docker compose run --rm app sh -lc "uv pip install --system --group dev && pytest"
```
