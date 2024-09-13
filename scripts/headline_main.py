import time
from typing import List, Dict
from scripts.headline_manager import HeadlineManager
from scripts.helpers.config import Config
from scripts.webscraper import WebScraper
from headline_analyzer import HeadlineAnalyzer

class HeadlineMain:
    def __init__(self, config: Config, manager: HeadlineManager, analyzer: HeadlineAnalyzer):
        self.config = config
        self.manager = manager
        self.analyzer = analyzer

    def analyze_headlines(self, medias: List[str], progress_callback=None):
        headlines_result = []
        for url in medias:
            
            if progress_callback:
                progress_callback(None, None, url)

            scraper = WebScraper(url)
            links = scraper.get_links(n_words=6)
            for index, link in enumerate(links):

                if progress_callback:
                    progress_callback(index + 1, len(links), url)
                
                link['href'] = scraper.clear_url(link['href'])
                if not self.manager.exists(link['href']):
                    link['text'] = link['text'].replace('\n', '').strip()
                    start_time = time.time()
                    result = self.analyzer.run(link['text'])
                    end_time = time.time()
                    
                    if result is not None and 'is_misogynistic' in result:
                        new = {
                            "source": scraper.extract_domain(link['href']),
                            "url": link['href'],
                            "is_misogynistic": result.get('is_misogynistic', None),
                            "headline": link['text'],
                            "refactored": result.get('refactored', None),
                            "refactored_es": result.get('refactored_es', None),
                            "reason": result.get('reason', None),
                            "execution_time": end_time - start_time,
                            "validated": None
                        }

                        if result.get('is_misogynistic'):
                            
                            #print("Is misogynistic. go to auto validation...")
                            context = scraper.get_context(new['url'])

                            auto_validation_result = self.analyzer.validate(headline=new['headline'], is_misogynistic=True, reason=new['reason'], context=context)
                            if auto_validation_result is not None:
                                new['validated_auto'] = auto_validation_result.get('is_correct', None)
                                new['validated_auto_reason'] = auto_validation_result.get('reason', None)

                                #print(f'Auto validation: {new["is_misogynistic"]} -> {auto_validation_result}')

                        headlines_result.append(new)
                        self.manager.save(new)
        
        return headlines_result