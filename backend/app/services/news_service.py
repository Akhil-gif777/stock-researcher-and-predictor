"""News service for fetching recent stock-related news."""
import yfinance as yf
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from app.config import settings


class NewsService:
    """Service for fetching stock-related news."""
    
    def get_recent_news(self, symbol: str, max_articles: int = 10, days_back: int = 7) -> List[Dict]:
        """
        Fetch recent news articles for a stock symbol (7-day lookback by default).

        Primary source: NewsAPI (full article descriptions)
        Fallback: yfinance (if NewsAPI unavailable or fails)

        Args:
            symbol: Stock ticker symbol
            max_articles: Maximum number of articles to return
            days_back: Number of days to look back (default: 7 for trend analysis)

        Returns:
            List of news articles with title, snippet, url, timestamp, credibility tier
        """
        # Try NewsAPI first if key is configured
        if settings.news_api_key:
            try:
                return self._get_newsapi_articles(symbol, max_articles, days_back)
            except Exception as e:
                print(f"⚠️ NewsAPI failed: {str(e)}, falling back to yfinance")

        # Fallback to yfinance
        return self._get_yfinance_news(symbol, max_articles)
    
    def get_market_news(self, max_articles: int = 5, days_back: int = 7) -> List[Dict]:
        """
        Fetch broader market news that could affect stock prices (7-day lookback).

        Args:
            max_articles: Maximum number of articles to return
            days_back: Number of days to look back (default: 7)

        Returns:
            List of market news articles with credibility tier
        """
        if settings.news_api_key:
            try:
                return self._get_market_newsapi_articles(max_articles, days_back)
            except Exception as e:
                print(f"⚠️ Market news NewsAPI failed: {str(e)}")

        return []
    
    def _get_newsapi_articles(self, symbol: str, max_articles: int, days_back: int = 7) -> List[Dict]:
        """Fetch news from NewsAPI with 7-day lookback, improved search and credibility weighting."""
        from newsapi import NewsApiClient

        newsapi = NewsApiClient(api_key=settings.news_api_key)

        # Get company name and industry for better search results
        try:
            ticker = yf.Ticker(symbol)
            company_name = ticker.info.get('longName', symbol)
            industry = ticker.info.get('industry', '')
            sector = ticker.info.get('sector', '')
        except:
            company_name = symbol
            industry = ''
            sector = ''

        # Build comprehensive search queries - start broad, then narrow
        queries = [
            f'"{symbol}"',  # Just the symbol - broadest search
            f'"{company_name}"',  # Just the company name
        ]

        # Add more specific queries if we have company info
        if company_name != symbol:
            queries.extend([
                f'"{symbol}" AND (earnings OR financial OR revenue OR profit OR growth OR stock OR shares)',
                f'"{company_name}" AND (earnings OR financial OR revenue OR profit OR growth OR stock OR shares)',
            ])

        # Add industry/sector specific queries if available
        if industry:
            queries.append(f'"{symbol}" AND "{industry}"')
            queries.append(f'"{company_name}" AND "{industry}"')
        if sector:
            queries.append(f'"{symbol}" AND "{sector}"')
            queries.append(f'"{company_name}" AND "{sector}"')

        all_articles = []

        # Calculate date range (7 days back by default for trend analysis)
        from_date = (datetime.now() - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)
        print(f"📅 NewsAPI: Fetching articles from past {days_back} days (since {from_date.strftime('%Y-%m-%d')})")

        # Try multiple queries to get diverse, relevant articles
        for i, query in enumerate(queries):
            try:
                print(f"🔍 NewsAPI: Trying query {i+1}/{len(queries)}: {query}")
                response = newsapi.get_everything(
                    q=query,
                    language='en',
                    sort_by='publishedAt',
                    page_size=min(max_articles, 20),  # Get more to filter
                    from_param=from_date.isoformat(),
                )
                
                raw_articles = response.get('articles', [])
                print(f"📰 NewsAPI: Query returned {len(raw_articles)} raw articles")
                
                relevant_count = 0
                for article in raw_articles:
                    if self._is_relevant_article(article, symbol, company_name):
                        all_articles.append(article)
                        relevant_count += 1
                
                print(f"✅ NewsAPI: Query {i+1} found {relevant_count} relevant articles")
                        
            except Exception as e:
                print(f"⚠️ Query failed: {query} - {str(e)}")
                continue
        
        # Remove duplicates and sort by relevance
        unique_articles = self._deduplicate_articles(all_articles)
        filtered_articles = self._filter_and_rank_articles(unique_articles, symbol, company_name)
        
        # Format articles with credibility tier
        articles = []
        for article in filtered_articles[:max_articles]:
            publisher = article.get('source', {}).get('name', 'Unknown')
            credibility_tier, credibility_weight = self._get_publisher_credibility(publisher)

            articles.append({
                'type': 'news',
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'snippet': article.get('description', '') or article.get('title', ''),
                'publisher': publisher,
                'timestamp': article.get('publishedAt', datetime.now().isoformat()),
                'credibility_tier': credibility_tier,
                'credibility_weight': credibility_weight,
            })
        
        # If we don't have enough articles, try a more permissive approach
        if len(articles) < max_articles // 2:  # If we have less than half the requested articles
            print(f"⚠️ NewsAPI: Only found {len(articles)} articles, trying broader search...")
            try:
                # Try a very broad search without financial keywords
                broad_response = newsapi.get_everything(
                    q=f'"{symbol}" OR "{company_name}"',
                    language='en',
                    sort_by='publishedAt',
                    page_size=max_articles * 2,
                    from_param=from_date.isoformat(),
                )
                
                broad_articles = []
                for article in broad_response.get('articles', []):
                    if self._is_relevant_article(article, symbol, company_name):
                        broad_articles.append(article)
                
                if broad_articles:
                    broad_unique = self._deduplicate_articles(broad_articles)
                    broad_filtered = self._filter_and_rank_articles(broad_unique, symbol, company_name)
                    
                    # Add to existing articles with credibility
                    for article in broad_filtered:
                        if len(articles) >= max_articles:
                            break
                        publisher = article.get('source', {}).get('name', 'Unknown')
                        credibility_tier, credibility_weight = self._get_publisher_credibility(publisher)

                        articles.append({
                            'type': 'news',
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'snippet': article.get('description', '') or article.get('title', ''),
                            'publisher': publisher,
                            'timestamp': article.get('publishedAt', datetime.now().isoformat()),
                            'credibility_tier': credibility_tier,
                            'credibility_weight': credibility_weight,
                        })
                    
                    print(f"✓ NewsAPI: Broad search added {len(articles)} total articles for {symbol}")
                
            except Exception as e:
                print(f"⚠️ Broad search failed: {str(e)}")
        
        print(f"✓ NewsAPI: Fetched {len(articles)} relevant articles for {symbol}")
        return articles
    
    def _get_yfinance_news(self, symbol: str, max_articles: int) -> List[Dict]:
        """Fallback: Fetch news from yfinance."""
        ticker = yf.Ticker(symbol)
        news = ticker.news
        
        articles = []
        for article in news[:max_articles]:
            articles.append({
                'type': 'news',
                'title': article.get('title', ''),
                'url': article.get('link', ''),
                'snippet': article.get('title', ''),  # yfinance doesn't provide snippets
                'publisher': article.get('publisher', 'Unknown'),
                'timestamp': datetime.fromtimestamp(
                    article.get('providerPublishTime', datetime.now().timestamp())
                ).isoformat()
            })
        
        print(f"✓ yfinance: Fetched {len(articles)} articles for {symbol}")
        return articles
    
    def _get_market_newsapi_articles(self, max_articles: int, days_back: int = 7) -> List[Dict]:
        """Fetch broader market news that could affect stock prices (7-day lookback)."""
        from newsapi import NewsApiClient

        newsapi = NewsApiClient(api_key=settings.news_api_key)

        # Market-wide news queries
        market_queries = [
            'Federal Reserve OR Fed OR interest rates OR monetary policy',
            'inflation OR CPI OR economic data OR GDP',
            'stock market OR S&P 500 OR NASDAQ OR Dow Jones',
            'earnings season OR quarterly results OR corporate earnings',
            'market volatility OR VIX OR market sentiment',
        ]

        all_articles = []

        # Calculate date range
        from_date = (datetime.now() - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)
        print(f"📅 NewsAPI Market: Fetching market articles from past {days_back} days")

        for query in market_queries:
            try:
                response = newsapi.get_everything(
                    q=query,
                    language='en',
                    sort_by='publishedAt',
                    page_size=5,  # Fewer per query
                    from_param=from_date.isoformat(),
                )
                
                for article in response.get('articles', []):
                    if self._is_market_relevant_article(article):
                        all_articles.append(article)
                        
            except Exception as e:
                print(f"⚠️ Market query failed: {query} - {str(e)}")
                continue
        
        # Remove duplicates and format with credibility
        unique_articles = self._deduplicate_articles(all_articles)

        articles = []
        for article in unique_articles[:max_articles]:
            publisher = article.get('source', {}).get('name', 'Unknown')
            credibility_tier, credibility_weight = self._get_publisher_credibility(publisher)

            articles.append({
                'type': 'market_news',
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'snippet': article.get('description', '') or article.get('title', ''),
                'publisher': publisher,
                'timestamp': article.get('publishedAt', datetime.now().isoformat()),
                'credibility_tier': credibility_tier,
                'credibility_weight': credibility_weight,
            })
        
        print(f"✓ NewsAPI: Fetched {len(articles)} market news articles")
        return articles
    
    def _is_relevant_article(self, article: Dict, symbol: str, company_name: str) -> bool:
        """Check if article is relevant to the specific stock."""
        title = article.get('title') or ''
        description = article.get('description') or ''
        content = f"{title} {description}".lower()
        
        # Must contain the symbol or company name
        if symbol.lower() not in content and company_name.lower() not in content:
            return False
        
        # Exclude clearly irrelevant content
        irrelevant_keywords = [
            'job posting', 'career', 'hiring', 'recruitment', 'employment',
            'real estate', 'property', 'housing', 'mortgage',
            'sports', 'entertainment', 'celebrity', 'gossip',
            'weather', 'climate', 'environmental',
            'cryptocurrency', 'bitcoin', 'crypto',
        ]
        
        for keyword in irrelevant_keywords:
            if keyword in content:
                return False
        
        # Accept articles that mention the company, even without specific financial terms
        # This includes business news, product launches, partnerships, etc.
        return True
    
    def _is_market_relevant_article(self, article: Dict) -> bool:
        """Check if article is relevant to market sentiment."""
        title = article.get('title') or ''
        description = article.get('description') or ''
        content = f"{title} {description}".lower()
        
        # Exclude irrelevant content
        irrelevant_keywords = [
            'job posting', 'career', 'hiring', 'recruitment',
            'real estate', 'property', 'housing',
            'sports', 'entertainment', 'celebrity',
            'weather', 'climate',
            'cryptocurrency', 'bitcoin', 'crypto',
        ]
        
        for keyword in irrelevant_keywords:
            if keyword in content:
                return False
        
        return True
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity."""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles
    
    def _filter_and_rank_articles(self, articles: List[Dict], symbol: str, company_name: str) -> List[Dict]:
        """Filter and rank articles by relevance and quality."""
        def relevance_score(article):
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            score = 0
            
            # Higher score for direct mentions in title
            if symbol.lower() in title:
                score += 15
            if company_name.lower() in title:
                score += 12
            
            # Mentions in description
            if symbol.lower() in description:
                score += 8
            if company_name.lower() in description:
                score += 6
            
            # Financial keywords boost score significantly
            financial_keywords = [
                'earnings', 'revenue', 'profit', 'financial', 'quarterly',
                'guidance', 'forecast', 'outlook', 'analyst', 'upgrade',
                'downgrade', 'target price', 'price target', 'stock',
                'shares', 'trading', 'market', 'investment'
            ]
            
            for keyword in financial_keywords:
                if keyword in content:
                    score += 3
            
            # Business keywords also boost score
            business_keywords = [
                'acquisition', 'merger', 'partnership', 'deal', 'agreement',
                'launch', 'product', 'service', 'expansion', 'growth',
                'ceo', 'executive', 'leadership', 'strategy', 'plan'
            ]
            
            for keyword in business_keywords:
                if keyword in content:
                    score += 2
            
            # Quality publishers get higher scores
            publisher = article.get('source', {}).get('name', '').lower()
            quality_publishers = [
                'reuters', 'bloomberg', 'wall street journal', 'cnbc',
                'marketwatch', 'yahoo finance', 'seeking alpha',
                'financial times', 'barrons', 'forbes', 'wsj'
            ]
            
            for pub in quality_publishers:
                if pub in publisher:
                    score += 5
                    break
            
            # Recency bonus (articles from today get higher score)
            try:
                from datetime import datetime, timedelta
                published = article.get('publishedAt', '')
                if published:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    hours_ago = (datetime.now(pub_date.tzinfo) - pub_date).total_seconds() / 3600
                    if hours_ago < 24:  # Within 24 hours
                        score += 5
                    elif hours_ago < 168:  # Within a week
                        score += 2
            except:
                pass
            
            return score
        
        # Sort by relevance score
        return sorted(articles, key=relevance_score, reverse=True)

    def _get_publisher_credibility(self, publisher: str) -> Tuple[int, float]:
        """
        Get credibility tier and weight for a news publisher.

        Returns:
            Tuple of (tier, weight):
            - Tier 1 (Premium): Weight 1.0 - Bloomberg, Reuters, WSJ, FT
            - Tier 2 (Quality): Weight 0.75 - CNBC, MarketWatch, Barron's
            - Tier 3 (Standard): Weight 0.5 - Other sources
        """
        publisher_lower = publisher.lower()

        # Tier 1: Premium financial news sources
        tier1_publishers = [
            'bloomberg', 'reuters', 'wall street journal', 'wsj',
            'financial times', 'ft.com'
        ]
        for pub in tier1_publishers:
            if pub in publisher_lower:
                return (1, 1.0)

        # Tier 2: Quality business/financial sources
        tier2_publishers = [
            'cnbc', 'marketwatch', 'barrons', "barron's",
            'seeking alpha', 'investor', 'forbes', 'fortune'
        ]
        for pub in tier2_publishers:
            if pub in publisher_lower:
                return (2, 0.75)

        # Tier 3: All other sources
        return (3, 0.5)


# Global instance
news_service = NewsService()

