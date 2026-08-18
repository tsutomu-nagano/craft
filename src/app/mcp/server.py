from mcp.server.fastmcp import FastMCP

from app.mcp.tools.analyze_table import analyze_table
from app.mcp.tools.check_readability import check_machine_readability
from app.mcp.tools.extract_metadata import extract_excel_metadata
from app.mcp.tools.record_agent_judgement import record_agent_judgement

mcp = FastMCP("craft")

mcp.tool(
    name="extract_excel_metadata",
    description="ExcelファイルURLを受け取り、miner APIで構造・メタデータを抽出します。",
)(extract_excel_metadata)
mcp.tool(
    name="check_machine_readability",
    description="CSV/TSV/ExcelのURLを受け取り、machine-readable-checker APIで機械判読性を確認します。",
)(check_machine_readability)
mcp.tool(
    name="analyze_table",
    description="表形式データURLを統合解析し、API由来の事実とAI判断を分離したAnalysisResultを保存して返します。",
)(analyze_table)
mcp.tool(
    name="record_agent_judgement",
    description=(
        "Chat UI上のAIがAnalysisResultを読んで作成した判断案をcraftに保存します。"
        "APIが返した事実とは分けてagent領域に記録します。"
    ),
)(record_agent_judgement)

mcp_app = mcp.streamable_http_app()
