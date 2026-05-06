"""
AutoClaw - Autonomous AI Agent Platform
Content Creator Skill

Generates reports, articles, social media posts, and other content.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

SKILL_METADATA = {
    "name": "content_creator",
    "version": "1.0.0",
    "description": "Generate reports, articles, social media posts, and documents",
    "author": "AutoClaw Team",
    "capabilities": [
        "write_article",
        "generate_report",
        "create_social_post",
        "format_document",
        "generate_image_prompt"
    ]
}


class ContentCreator:
    """
    Content generation and formatting.
    
    Features:
    - Write articles and blog posts
    - Generate reports from data
    - Create social media content
    - Format documents (Markdown, HTML, etc.)
    - Generate image prompts for DALL-E
    """
    
    def __init__(self):
        self.generated_content = []
    
    async def write_article(self, topic: str, style: str = "professional",
                           word_count: int = 500, outline: Optional[List[str]] = None) -> Dict:
        """
        Write an article on a given topic.
        
        Args:
            topic: Article topic
            style: Writing style (professional, casual, technical, etc.)
            word_count: Target word count
            outline: Optional outline sections
            
        Returns:
            Generated article
        """
        # Build article structure
        if not outline:
            outline = [
                f"Introduction to {topic}",
                f"Key aspects of {topic}",
                f"Practical applications",
                "Conclusion"
            ]
        
        # Generate article content (placeholder - would use LLM in production)
        article = {
            "title": f"A Comprehensive Guide to {topic}",
            "style": style,
            "outline": outline,
            "content": f"# A Comprehensive Guide to {topic}\n\n",
            "word_count": 0,
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate sections
        for section in outline:
            article["content"] += f"## {section}\n\n"
            article["content"] += f"[Content about {section} would be generated here using the LLM. "
            article["content"] += f"This is a placeholder for the actual generated content about {topic}.\n\n"
        
        article["word_count"] = len(article["content"].split())
        
        self.generated_content.append({
            "type": "article",
            "topic": topic,
            "timestamp": article["generated_at"]
        })
        
        return {
            "success": True,
            "article": article,
            "message": f"Generated article on '{topic}' ({article['word_count']} words)"
        }
    
    async def generate_report(self, title: str, data: Dict, 
                             format: str = "markdown") -> Dict:
        """
        Generate a report from data.
        
        Args:
            title: Report title
            data: Data to include in report
            format: Output format (markdown, html, text)
            
        Returns:
            Generated report
        """
        report = {
            "title": title,
            "format": format,
            "generated_at": datetime.now().isoformat(),
            "content": ""
        }
        
        if format == "markdown":
            report["content"] = self._generate_markdown_report(title, data)
        elif format == "html":
            report["content"] = self._generate_html_report(title, data)
        else:
            report["content"] = self._generate_text_report(title, data)
        
        self.generated_content.append({
            "type": "report",
            "title": title,
            "timestamp": report["generated_at"]
        })
        
        return {
            "success": True,
            "report": report,
            "message": f"Generated report: {title}"
        }
    
    def _generate_markdown_report(self, title: str, data: Dict) -> str:
        """Generate a Markdown formatted report."""
        content = f"# {title}\n\n"
        content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        content += "---\n\n"
        
        for key, value in data.items():
            content += f"## {key}\n\n"
            if isinstance(value, dict):
                for k, v in value.items():
                    content += f"- **{k}**: {v}\n"
            elif isinstance(value, list):
                for item in value:
                    content += f"- {item}\n"
            else:
                content += f"{value}\n"
            content += "\n"
        
        return content
    
    def _generate_html_report(self, title: str, data: Dict) -> str:
        """Generate an HTML formatted report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        .meta {{ color: #999; font-style: italic; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="meta">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    <hr>
"""
        
        for key, value in data.items():
            html += f"    <h2>{key}</h2>\n"
            if isinstance(value, dict):
                html += "    <table>\n"
                html += "        <tr><th>Property</th><th>Value</th></tr>\n"
                for k, v in value.items():
                    html += f"        <tr><td>{k}</td><td>{v}</td></tr>\n"
                html += "    </table>\n"
            elif isinstance(value, list):
                html += "    <ul>\n"
                for item in value:
                    html += f"        <li>{item}</li>\n"
                html += "    </ul>\n"
            else:
                html += f"    <p>{value}</p>\n"
        
        html += """
</body>
</html>"""
        return html
    
    def _generate_text_report(self, title: str, data: Dict) -> str:
        """Generate a plain text report."""
        content = f"{title}\n{'=' * len(title)}\n\n"
        content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        content += "-" * 40 + "\n\n"
        
        for key, value in data.items():
            content += f"{key}:\n"
            if isinstance(value, dict):
                for k, v in value.items():
                    content += f"  {k}: {v}\n"
            elif isinstance(value, list):
                for item in value:
                    content += f"  - {item}\n"
            else:
                content += f"  {value}\n"
            content += "\n"
        
        return content
    
    async def create_social_post(self, topic: str, platform: str = "twitter",
                                tone: str = "engaging") -> Dict:
        """
        Create a social media post.
        
        Args:
            topic: Post topic
            platform: Target platform (twitter, linkedin, facebook, instagram)
            tone: Post tone (engaging, professional, casual, humorous)
            
        Returns:
            Generated post content
        """
        # Platform-specific constraints
        platform_limits = {
            "twitter": 280,
            "linkedin": 3000,
            "facebook": 63206,
            "instagram": 2200
        }
        
        max_length = platform_limits.get(platform, 500)
        
        # Generate post (placeholder - would use LLM in production)
        post = {
            "platform": platform,
            "topic": topic,
            "tone": tone,
            "content": f"🚀 Exciting news about {topic}! \n\n"
                      f"This is a placeholder for an engaging post about {topic}. "
                      f"In production, this would be generated by an LLM with the {tone} tone "
                      f"optimized for {platform}.\n\n"
                      f"#{topic.replace(' ', '')} #AI #Automation",
            "hashtags": [f"#{topic.replace(' ', '')}", "#AI", "#Automation"],
            "character_count": 0,
            "generated_at": datetime.now().isoformat()
        }
        
        post["character_count"] = len(post["content"])
        
        # Truncate if needed
        if post["character_count"] > max_length:
            post["content"] = post["content"][:max_length - 3] + "..."
            post["character_count"] = max_length
        
        self.generated_content.append({
            "type": "social_post",
            "platform": platform,
            "timestamp": post["generated_at"]
        })
        
        return {
            "success": True,
            "post": post,
            "message": f"Created {platform} post about '{topic}'"
        }
    
    async def format_document(self, content: str, input_format: str = "markdown",
                             output_format: str = "html") -> Dict:
        """
        Convert document between formats.
        
        Args:
            content: Document content
            input_format: Current format
            output_format: Desired output format
            
        Returns:
            Formatted document
        """
        result = {
            "original_format": input_format,
            "output_format": output_format,
            "content": content,
            "converted_at": datetime.now().isoformat()
        }
        
        # Simple format conversions (placeholder - would use proper libraries in production)
        if input_format == "markdown" and output_format == "html":
            result["content"] = self._markdown_to_html(content)
        elif input_format == "html" and output_format == "markdown":
            result["content"] = self._html_to_markdown(content)
        
        return {
            "success": True,
            "document": result,
            "message": f"Converted from {input_format} to {output_format}"
        }
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Simple Markdown to HTML conversion."""
        html = markdown
        
        # Headers
        html = html.replace("# ", "<h1>").replace("\n", "</h1>\n")
        html = html.replace("## ", "<h2>").replace("\n", "</h2>\n")
        html = html.replace("### ", "<h3>").replace("\n", "</h3>\n")
        
        # Bold and italic
        html = html.replace("**", "<strong>").replace("**", "</strong>")
        html = html.replace("*", "<em>").replace("*", "</em>")
        
        # Line breaks
        html = html.replace("\n\n", "</p><p>")
        
        return f"<div class='markdown-content'>\n{html}\n</div>"
    
    def _html_to_markdown(self, html: str) -> str:
        """Simple HTML to Markdown conversion."""
        markdown = html
        
        # Remove HTML tags (simplified)
        import re
        markdown = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', markdown)
        markdown = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', markdown)
        markdown = re.sub(r'<strong>(.*?)</strong>', r'**\1**', markdown)
        markdown = re.sub(r'<em>(.*?)</em>', r'*\1*', markdown)
        
        return markdown
    
    async def generate_image_prompt(self, subject: str, style: str = "photorealistic",
                                   mood: str = "neutral") -> Dict:
        """
        Generate a detailed image prompt for DALL-E or similar.
        
        Args:
            subject: Main subject of the image
            style: Art style (photorealistic, illustration, painting, etc.)
            mood: Image mood (neutral, dramatic, cheerful, etc.)
            
        Returns:
            Detailed image prompt
        """
        prompt = {
            "subject": subject,
            "style": style,
            "mood": mood,
            "prompt": f"A {style} image of {subject}, {mood} atmosphere, "
                     f"high quality, detailed, professional composition. "
                     f"(This is a placeholder - in production, an LLM would generate "
                     f"a more detailed and creative prompt based on the parameters)",
            "negative_prompt": "blurry, low quality, distorted, watermark",
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "image_prompt": prompt,
            "message": "Generated image prompt ready for DALL-E/Stable Diffusion"
        }
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method for tool manager compatibility."""
        if action == "write_article":
            return await self.write_article(
                kwargs.get("topic", ""),
                kwargs.get("style", "professional"),
                kwargs.get("word_count", 500),
                kwargs.get("outline")
            )
        elif action == "generate_report":
            return await self.generate_report(
                kwargs.get("title", ""),
                kwargs.get("data", {}),
                kwargs.get("format", "markdown")
            )
        elif action == "create_social_post":
            return await self.create_social_post(
                kwargs.get("topic", ""),
                kwargs.get("platform", "twitter"),
                kwargs.get("tone", "engaging")
            )
        elif action == "format_document":
            return await self.format_document(
                kwargs.get("content", ""),
                kwargs.get("input_format", "markdown"),
                kwargs.get("output_format", "html")
            )
        elif action == "generate_image_prompt":
            return await self.generate_image_prompt(
                kwargs.get("subject", ""),
                kwargs.get("style", "photorealistic"),
                kwargs.get("mood", "neutral")
            )
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
