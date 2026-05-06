"""
AutoClaw - Autonomous AI Agent Platform
Web Search Skill

Searches the web using Google, Bing, or custom APIs.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

SKILL_METADATA = {
    "name": "web_search",
    "version": "1.0.0",
    "description": "Web search using Google, Bing, or custom search APIs",
    "author": "AutoClaw Team",
    "capabilities": [
        "google_search",
        "bing_search",
        "custom_search",
        "extract_results"
    ]
}


class WebSearch:
    """
    Web search operations.
    
    Features:
    - Google search
    - Bing search
    - Custom search API
    - Extract and filter results
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.search_history = []
        
        # API configurations
        self.google_api_key = self.config.get("google_api_key", "")
        self.google_cse_id = self.config.get("google_cse_id", "")
        self.bing_api_key = self.config.get("bing_api_key", "")
    
    async def google_search(self, query: str, num_results: int = 10,
                           date_range: Optional[str] = None) -> Dict:
        """
        Search using Google Custom Search API.
        
        Args:
            query: Search query
            num_results: Number of results to return
            date_range: Date filter (e.g., "y1" for past year)
            
        Returns:
            Search results
        """
        if not self.google_api_key or not self.google_cse_id:
            # Fallback: simulate search
            return self._simulate_search(query, num_results, "google")
        
        try:
            import aiohttp
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": query,
                "num": min(num_results, 10)
            }
            
            if date_range:
                params["dateRestrict"] = date_range
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    results = self._parse_google_results(data)
                    
                    self.search_history.append({
                        "engine": "google",
                        "query": query,
                        "timestamp": datetime.now().isoformat(),
                        "results_count": len(results)
                    })
                    
                    return {
                        "success": True,
                        "engine": "google",
                        "query": query,
                        "results": results,
                        "total_results": data.get("searchInformation", {}).get("formattedTotalResults", "unknown")
                    }
                    
        except ImportError:
            return self._simulate_search(query, num_results, "google")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "engine": "google"
            }
    
    async def bing_search(self, query: str, num_results: int = 10,
                         market: str = "en-US") -> Dict:
        """
        Search using Bing Search API.
        
        Args:
            query: Search query
            num_results: Number of results
            market: Market code (e.g., en-US, zh-CN)
            
        Returns:
            Search results
        """
        if not self.bing_api_key:
            # Fallback: simulate search
            return self._simulate_search(query, num_results, "bing")
        
        try:
            import aiohttp
            
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
            params = {
                "q": query,
                "count": min(num_results, 50),
                "mkt": market
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    
                    results = self._parse_bing_results(data)
                    
                    self.search_history.append({
                        "engine": "bing",
                        "query": query,
                        "timestamp": datetime.now().isoformat(),
                        "results_count": len(results)
                    })
                    
                    return {
                        "success": True,
                        "engine": "bing",
                        "query": query,
                        "results": results,
                        "total_results": data.get("webPages", {}).get("totalEstimatedMatches", "unknown")
                    }
                    
        except ImportError:
            return self._simulate_search(query, num_results, "bing")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "engine": "bing"
            }
    
    async def custom_search(self, api_url: str, query: str,
                           params: Optional[Dict] = None) -> Dict:
        """
        Search using a custom search API.
        
        Args:
            api_url: Custom API endpoint
            query: Search query
            params: Additional parameters
            
        Returns:
            Search results
        """
        try:
            import aiohttp
            
            request_params = params or {}
            request_params["q"] = query
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=request_params) as response:
                    data = await response.json()
                    
                    self.search_history.append({
                        "engine": "custom",
                        "url": api_url,
                        "query": query,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return {
                        "success": True,
                        "engine": "custom",
                        "query": query,
                        "results": data,
                        "source": api_url
                    }
                    
        except ImportError:
            return self._simulate_search(query, 10, "custom")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "engine": "custom"
            }
    
    def _parse_google_results(self, data: Dict) -> List[Dict]:
        """Parse Google Custom Search results."""
        results = []
        items = data.get("items", [])
        
        for item in items:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "display_link": item.get("displayLink", "")
            })
        
        return results
    
    def _parse_bing_results(self, data: Dict) -> List[Dict]:
        """Parse Bing Search results."""
        results = []
        web_pages = data.get("webPages", {})
        items = web_pages.get("value", [])
        
        for item in items:
            results.append({
                "title": item.get("name", ""),
                "link": item.get("url", ""),
                "snippet": item.get("snippet", ""),
                "display_link": item.get("hostPageDisplayUrl", "")
            })
        
        return results
    
    def _simulate_search(self, query: str, num_results: int, engine: str) -> Dict:
        """Simulate search results when API is not configured."""
        results = []
        
        for i in range(num_results):
            results.append({
                "title": f"Result {i+1} for '{query}' (simulated)",
                "link": f"https://example.com/result{i+1}",
                "snippet": f"This is a simulated search result for '{query}'. Configure your API key for real results.",
                "display_link": "example.com"
            })
        
        self.search_history.append({
            "engine": engine,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results_count": num_results,
            "simulated": True
        })
        
        return {
            "success": True,
            "engine": engine,
            "query": query,
            "results": results,
            "note": "These are simulated results. Configure API keys for real searches."
        }
    
    async def extract_results(self, urls: List[str]) -> Dict:
        """
        Extract content from URLs.
        
        Args:
            urls: List of URLs to extract content from
            
        Returns:
            Extracted content
        """
        extracted = []
        
        for url in urls[:5]:  # Limit to 5 URLs
            try:
                import aiohttp
                from bs4 import BeautifulSoup
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract title and main content
                        title = soup.title.string if soup.title else ""
                        
                        # Remove script and style elements
                        for tag in soup(['script', 'style']):
                            tag.decompose()
                        
                        text = soup.get_text(separator=' ', strip=True)[:2000]
                        
                        extracted.append({
                            "url": url,
                            "title": title,
                            "content": text,
                            "success": True
                        })
                        
            except ImportError:
                extracted.append({
                    "url": url,
                    "error": "beautifulsoup4 not installed",
                    "success": False
                })
            except Exception as e:
                extracted.append({
                    "url": url,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "success": True,
            "extracted": extracted,
            "count": len(extracted)
        }
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method for tool manager compatibility."""
        if action == "google_search":
            return await self.google_search(
                kwargs.get("query", ""),
                kwargs.get("num_results", 10),
                kwargs.get("date_range")
            )
        elif action == "bing_search":
            return await self.bing_search(
                kwargs.get("query", ""),
                kwargs.get("num_results", 10),
                kwargs.get("market", "en-US")
            )
        elif action == "custom_search":
            return await self.custom_search(
                kwargs.get("api_url", ""),
                kwargs.get("query", ""),
                kwargs.get("params")
            )
        elif action == "extract_results":
            return await self.extract_results(kwargs.get("urls", []))
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
