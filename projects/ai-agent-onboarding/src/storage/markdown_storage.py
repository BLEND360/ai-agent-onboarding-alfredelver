"""Save articles to markdown files"""
from pathlib import Path
from typing import List
from datetime import datetime
from src.models.articles import Article
from src.storage.base_storage import ArticleStorage

class MarkdownStorage(ArticleStorage):
    """
    Saves articles to markdown files.
    
    Creates files in data/articles/ directory.
    """

    def __init__(self,base_path='data/articles'):
        
         
         """
        Initialize storage.
        
        Args:
            base_path: Directory to save articles
        """
        
         self.base_path = Path(base_path)
         self.base_path.mkdir(parents=True,exist_ok=True)

    def save(self,articles:List[Article],filename:str=None)-> Path:
          
          """
            Save articles to markdown file.
        
            Args:
            articles: List of articles to save
            filename: Optional filename, auto-generated if not provided
            
            Returns:
             Path to saved file
         """
          if filename is None:
               #autogenerate file name
               timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
               filename  = f"article_{timestamp}.md"

          filepath = self.base_path/filename

          with open(filepath, 'w', encoding='utf-8') as f:
               f.write(f"# Articles - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
               
               for article in articles:
                    f.write(self._format_article(article))
                    f.write("\n---\n\n")
          
          return filepath
    
    def _format_article(self, article: Article) -> str:
        """Format single article as markdown."""
        return f"""## {article.title}

**Source:** {article.source}
**URL:** {article.url}
**Published:** {article.published_at}
**Score:** {article.score if hasattr(article, 'score') else 'N/A'}

{article.summary}
"""

if __name__ =="__main__":
    #  import sys
    #  from pathlib import Path
    #  sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
     from src.models.articles import Article

     # creating test articale
     test_article = Article(
          title = "test article",
          url = 'https://example.com',
          published_at=datetime.now(),
          source='test',
          score='',
          summary='Test Test'

     )
     
     storage = MarkdownStorage()
     path = storage.save([test_article], "test.md")

     # verifying
     assert path.exists()
     print(f'saved to {path}')
     print(f'File Contents')
     print(path.read_text()[:250])


               