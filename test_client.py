import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from mcp.types import CallToolRequestParams

async def run_test():
    print("正在连接到 MCP SSE 服务...")
    
    # 连接到 SSE 端点
    async with sse_client("http://localhost:8000/sse") as streams:
        read_stream, write_stream = streams
        
        # 创建会话
        async with ClientSession(read_stream, write_stream) as session:
            # 1. 初始化
            await session.initialize()
            print("✅ 连接成功！")
            
            # 2. 获取工具列表
            print("\n--- 获取工具列表 ---")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"发现工具: {tool.name} - {tool.description}")

            # 3. 测试调用搜索工具
            print("\n--- 测试工具: search_academic_papers ---")
            query = "A Structure-aware and Motion-adaptive Framework for 3D Human Pose Estimation with Mamba"
            print(f"正在搜索: {query} ...")
            
            result = await session.call_tool(
                "get_paper_references_analysis",
                arguments={"title": query}
            )
            
            # 打印结果（result.content 是一个列表，通常包含 TextContent）
            for content in result.content:
                if content.type == 'text':
                    print(f"返回结果:\n{content.text[:2000]}...") # 只打印前500字符
            
            # 4. 测试引用分析工具（如果需要）
            # print("\n--- 测试工具: get_paper_references_analysis ---")
            # result_ref = await session.call_tool(
            #     "get_paper_references_analysis",
            #     arguments={"title": "DenseBody: Directly Regressing Dense 3D Human Pose and Shape From a Single Color Image"}
            # )
            # print("引用分析调用完成")

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except Exception as e:
        print(f"测试出错: {e}")
