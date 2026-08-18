import httpx
import respx

from app.clients.machine_readable_checker import MachineReadableCheckerClient
from app.clients.miner import MinerClient


@respx.mock
async def test_miner_extract_posts_url() -> None:
    route = respx.post("http://miner.test/api/extract").mock(
        return_value=httpx.Response(200, json={"sheets": []})
    )

    response = await MinerClient("http://miner.test").extract("https://example.test/book.xlsx")

    assert route.called
    assert route.calls.last.request.content == b'{"source":"https://example.test/book.xlsx"}'
    assert response.payload == {"sheets": []}


@respx.mock
async def test_checker_check_url_posts_url() -> None:
    route = respx.post("http://checker.test/api/check-url").mock(
        return_value=httpx.Response(200, json={"issues": []})
    )

    response = await MachineReadableCheckerClient("http://checker.test").check_url(
        "https://example.test/table.csv"
    )

    assert route.called
    assert response.payload == {"issues": []}
