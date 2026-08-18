# MCP Client Setup

craftはStreamable HTTPのMCP Serverを提供します。ChatGPT/CodexなどのChat UI上のAIは、このMCP Serverへ接続して解析ツールを実行します。craftサーバー側ではLLM APIを直接呼びません。

## 起動

```bash
APP_PORT=8010 docker compose up --build -d
```

接続先URL:

```text
http://127.0.0.1:8010/mcp
```

## Tunnel Client

Chat UIからローカルComposeネットワークへ直接接続できない場合は、`tunnel-client`サービスを起動します。

準備:

```bash
cp .env.tunnel.example .env.tunnel
```

`.env.tunnel` にControl PlaneのTunnel IDを設定します。

```env
CONTROL_PLANE_TUNNEL_ID=...
```

起動:

```bash
docker compose up --build -d app tunnel-client
```

Compose内では、tunnel-clientがappサービスと同じnetwork namespaceで動作し、craft MCP Serverへ次のURLで接続します。

```text
http://127.0.0.1:8000/mcp
```

tunnel-clientのprofile名は `craft` です。Compose起動時は`--force`付きで`init`するため、既存の`craft.yaml`がある場合もMCP接続先を更新します。
`.env.tunnel`に`MCP_SERVER_URL`が残っていても、Compose側で`http://127.0.0.1:8000/mcp`へ上書きします。
また、`app`の`/health`が成功してから`tunnel-client`を起動するため、アプリ起動直後のMCP接続失敗を避けます。

ヘルスチェック:

```bash
curl http://127.0.0.1:8010/health
```

## MCP接続確認

MCPクライアントからツール一覧を取得します。

```bash
docker compose exec app python scripts/check_mcp_client.py
```

`APP_PORT`を変えてホスト側URLを確認したい場合:

```bash
docker compose exec -e MCP_URL=http://127.0.0.1:8000/mcp app python scripts/check_mcp_client.py
```

期待されるTools:

- `extract_excel_metadata`
- `check_machine_readability`
- `analyze_table`
- `record_agent_judgement`

## Chat UIでの使い方

1. craftをDocker Composeで起動する。
2. Chat UIのMCP設定に、Streamable HTTP MCP Serverとして `http://127.0.0.1:8010/mcp` を登録する。
3. Chat UIで `analyze_table` を呼び、e-StatなどのファイルURLを渡す。
4. AIが返却されたAnalysisResultを確認し、人と会話しながら判断案を作る。
5. AIが `record_agent_judgement` で判断案を保存する。
6. 人がcraft UIでReviewを登録する。

## 協業フロー

```text
Chat UI上のAI
  ↓ MCP analyze_table
craft
  ↓
miner + machine-readable-checker
  ↓
AnalysisResult
  ↓ Chat UI上でAIと人が確認
record_agent_judgement
  ↓
Human Review
```

## Example

解析:

```json
{
  "tool": "analyze_table",
  "arguments": {
    "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040387904&fileKind=0"
  }
}
```

AI判断案の記録:

```json
{
  "tool": "record_agent_judgement",
  "arguments": {
    "analysis_id": "<analysis_id>",
    "model": "Chat UI",
    "judgement": [
      {
        "code": "legacy-xls-conversion-needed",
        "severity": "warning",
        "message": "元ファイルが古い.xls形式のため、.xlsxまたはCSVへの変換を検討します。",
        "evidence": "checker findings: legacy-xls",
        "recommended_action": "変換後ファイルの保存方針と原本URLの保持方針を確認してください。"
      }
    ],
    "needs_human_review": true,
    "reasons": [
      "checkerがlegacy-xlsを警告しているため、人による確認対象とします。"
    ],
    "prompt": "Chat UIでAnalysisResultを確認し、Human Review向け判断案を作成"
  }
}
```

## Troubleshooting

- Toolsが見えない場合は、`docker compose ps`で`app`が起動中か確認する。
- `curl http://127.0.0.1:8010/health` が失敗する場合は、`APP_PORT`の衝突を確認する。
- tunnel-clientログに`connect: connection refused`が出る場合は、`app`のhealthcheck状態と`craft.yaml`内のMCP URLが`http://127.0.0.1:8000/mcp`になっているか確認する。
- Chat UIがローカルURLへ接続できない場合は、同じマシン上で動作しているか、MCP設定がStreamable HTTPになっているか確認する。
- `record_agent_judgement`はAPIが返した事実を書き換えず、`agent`領域だけを更新する。
