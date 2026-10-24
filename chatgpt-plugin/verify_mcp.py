"""Actual SDK protocol smoke. Start server first, then run this script."""
import asyncio,json,subprocess,sys
from pathlib import Path
import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def verify():
    async with httpx2.AsyncClient(trust_env=False) as http, streamable_http_client('http://127.0.0.1:8787/mcp',http_client=http) as streams:
        async with ClientSession(streams[0],streams[1]) as session:
            await session.initialize()
            tools=(await session.list_tools()).tools
            names={t.name for t in tools}
            assert names=={'demo_reconciliation','reconcile_csv'},names
            for tool in tools:
                descriptor=tool.model_dump(by_alias=True)
                assert descriptor['_meta']['ui']['resourceUri']=='ui://reconcile-desk/report-v1.html'
                assert descriptor['annotations']['readOnlyHint'] is True
            result=await session.call_tool('demo_reconciliation',{})
            obj=result.model_dump(by_alias=True)
            assert not obj['isError']
            assert obj['structuredContent']['summary']['matched']==1
            resource=await session.read_resource('ui://reconcile-desk/report-v1.html')
            assert resource.contents[0].mime_type=='text/html;profile=mcp-app'
            assert 'Reconcile Desk' in resource.contents[0].text
            denied=await session.call_tool('reconcile_csv',{'invoices_csv':'private','payments_csv':'private'})
            assert denied.model_dump(by_alias=True)['isError']
            print(json.dumps({'protocol':'Streamable HTTP MCP','tools':sorted(names),'demo':obj['structuredContent']['summary'],'ui_resource':'verified','private_upload_block':'verified'},indent=2))

async def main():
    process=subprocess.Popen([sys.executable,'server.py'],cwd=Path(__file__).parent,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        async with httpx2.AsyncClient(trust_env=False) as http:
            for attempt in range(100):
                try:
                    if (await http.get('http://127.0.0.1:8787/health')).status_code==200:break
                except httpx2.ConnectError:
                    await asyncio.sleep(.05)
            else:raise RuntimeError('Server did not become ready')
        await verify()
    finally:
        process.terminate();process.wait(timeout=5)

if __name__=='__main__':asyncio.run(main())
