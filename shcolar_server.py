import requests
import json
import time
import os
from typing import List, Dict, Any
from loguru import logger
from fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("Scholar Search Service")

from utils import bibtex_to_gbt7714


# --- Scholar 类定义 (主要逻辑保持不变，移除了pdb和部分print) ---
class Scholar:
    """学术论文搜索与分析类"""
    
    def __init__(self, api_key: str="", base_url: str = "https://lifuai.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        
        # 简单的逻辑判断 base_url
        if "lifuai" in self.base_url or "api.semanticscholar.org" in self.base_url:
            self.headers = {
                'Content-Type': 'application/json'
            }
            if self.api_key:
                self.headers['Authorization'] = f'Bearer {self.api_key}'
            # 对于官方 semantic scholar，有时使用的是 x-api-key
            if "semanticscholar.org" in self.base_url and self.api_key:
                 self.headers['x-api-key'] = self.api_key
        else:
            self.headers = None
    
    def _make_request(self, endpoint: str, params: Dict = None, method: str = 'GET', data: Dict = None) -> Dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        count = 0
        while count <= 10: # 减少重试次数以提高响应速度
            count += 1
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, headers=self.headers, timeout=30)
                elif method.upper() == 'POST':
                    response = requests.post(url, params=params, json=data, headers=self.headers, timeout=30)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求失败 (尝试 {count}): {e}")
                time.sleep(1)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                time.sleep(1)
        
        logger.error("最终请求失败") 
        return {}

    def search_papers(self, query: str, limit: int = 10, fields: str = None) -> List[Dict]:
        if fields is None:
            fields = 'title,authors,year,abstract,citationCount,venue,openAccessPdf,citationStyles'
        
        params = {
            'query': query,
            'limit': limit,
            'fields': fields
        }
        
        data = self._make_request('graph/v1/paper/search', params=params)
        return data.get('data', [])

    def get_paper_details(self, paper_id: str, fields: str = None) -> Dict:
        if paper_id.startswith('10.'):
            paper_id = f'DOI:{paper_id}'
        endpoint = f'graph/v1/paper/{paper_id}'
        # 默认获取所有字段以便分析
        if not fields:
            fields = 'title,authors,year,abstract,citationCount,venue,citationStyles,references'
        return self._make_request(endpoint, params={'fields': fields})

    def batch_get_papers(self, paper_ids: List[str], fields: str = None) -> List[Dict]:
        if fields is None:
            fields = 'title,authors,year,citationCount,publicationVenue,journal,citationStyles,abstract'
        data = {'ids': paper_ids}
        params = {'fields': fields}
        return self._make_request('graph/v1/paper/batch', params=params, method='POST', data=data)

    def get_paper_references(self, paper_id: str, limit: int = 100, fields: str = None) -> List[Dict]:
        if fields is None:
            fields = 'contexts,title,authors,year,citationCount'
        params = {'limit': limit, 'fields': fields}
        endpoint = f'graph/v1/paper/{paper_id}/references'
        data = self._make_request(endpoint, params=params)
        return data.get('data', [])

    def get_references_info(self, title: str) -> Dict[str, Any]:
        """
        获取论文及其参考文献的详细信息（含格式化引用）
        """
        papers = self.search_papers(query=title, limit=1)
        
        if not papers:
            return {"error": "未查找到相关论文", "main_paper": {}, "references": []}
            
        main_paper = papers[0]
        # 添加主论文的引用格式
        if "citationStyles" in main_paper and main_paper["citationStyles"]:
            main_paper["gbt7714"] = bibtex_to_gbt7714(main_paper["citationStyles"].get('bibtex', ''))
        
        paper_id = main_paper['paperId']
        logger.info(f'''获取论文的papepr_id为{paper_id}''') 
        # 获取参考文献列表
        logger.info("获取参考文献列表")
        references_raw = self.get_paper_references(paper_id=paper_id, limit=50) # 限制数量防止超时
        logger.info("获取参考文献成功")
        # 提取被引用的论文ID
        references_paper_ids = []
        for ref in references_raw:
            if ref.get("citedPaper") and ref["citedPaper"].get('paperId'):
                references_paper_ids.append(ref["citedPaper"]['paperId'])
        
        # 批量获取参考文献详情
        reference_details = []
        if references_paper_ids:
            reference_details = self.batch_get_papers(paper_ids=references_paper_ids)
            for info in reference_details:
                if "citationStyles" in info and info["citationStyles"]:
                    info["gbt7714"] = bibtex_to_gbt7714(info["citationStyles"].get('bibtex', ''))

        return {
            "main_paper": main_paper,
            "references": reference_details
        }

# --- 实例化全局 Scholar 对象 ---
# 建议在运行 MCP 时通过环境变量配置 key
#API_KEY = os.environ.get("SCHOLAR_API_KEY", "") 
#BASE_URL = os.environ.get("SCHOLAR_BASE_URL", "https://api.semanticscholar.org")

#scholar_client = Scholar(api_key=API_KEY, base_url=BASE_URL)

# --- MCP 工具定义 ---

@mcp.tool
def search_academic_papers(query: str, limit: int = 5) -> str:
    """
    Search for academic papers by keyword.
    
    Args:
        query: The search query (e.g., "3D Human Pose Estimation")
        limit: Number of results to return (default 5)
    """
    scholar_client = Scholar(api_key="", base_url="https://api.semanticscholar.org")
    results = scholar_client.search_papers(query, limit=limit)
    return json.dumps(results, ensure_ascii=False, indent=2)

@mcp.tool
def get_paper_references_analysis(title: str) -> str:
    """
    Find a paper by title and get detailed information about its references,
    including GB/T 7714 citation formats. Useful for literature review.
    
    Args:
        title: The exact or partial title of the paper.
    """
    scholar_client = Scholar(api_key="", base_url="https://api.semanticscholar.org")
    result = scholar_client.get_references_info(title)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool
def get_paper_details(paper_id: str) -> str:
    """
    Get detailed metadata for a specific paper using its ID or DOI.
    
    Args:
        paper_id: The Semantic Scholar ID or DOI (e.g., "10.1109/CVPR.2020.00000")
    """
    scholar_client = Scholar(api_key="", base_url="https://api.semanticscholar.org")
    result = scholar_client.get_paper_details(paper_id)
    return json.dumps(result, ensure_ascii=False, indent=2)

# --- 服务器入口 ---
#if __name__ == "__main__":
    # 打印启动提示
#    logger.info("正在启动 Scholar MCP Server (SSE 模式)...")
#    logger.info("SSE 访问地址: http://0.0.0.0:8000/sse")

    # 启动 SSE 服务
    # FastMCP 默认在 transport='sse' 时会使用 uvicorn 启动
#    mcp.run(transport='sse')
