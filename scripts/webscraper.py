
import requests
from bs4 import BeautifulSoup
import tldextract
from urllib.parse import urlparse, urlunparse

class WebScraper:
    """ Class for scraping a website."""

    def __init__(self, url):
        self.url = url

    def get_links(self, n_words=5):
        """ Get all the links from a website with more than n words. """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            base_url = self.extract_domain(self.url)
            
            # Ensure base_url starts with https://
            if not base_url.startswith('https://'):
                base_url = 'https://' + base_url
            
            links = []
            for a in soup.find_all('a', href=True):
                if len(a.text.split()) > n_words:
                    href = a['href']
                    if not href.startswith(('http://', 'https://')):
                        if not href.startswith('/'):
                            href = '/' + href
                        #print(f"Relative URL found: {base_url.rstrip('/')} - {href}")
                        href = base_url.rstrip('/') + href
                    links.append({
                        'text': a.text,
                        'href': href
                    })
            
            return links
        except requests.exceptions.RequestException as e:
            print(f"Error making the HTTP request: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def extract_domain(self, url):
        """ Extract the main domain from a URL, ignoring subdomains."""
        parsed_url = urlparse(url)
        ext = tldextract.extract(parsed_url.netloc)
        main_domain = f"{ext.domain}.{ext.suffix}"
        return main_domain
    
    def clear_url(self, url):
        """ Clear the URL from any query parameters or fragments."""
        parsed_url = urlparse(url)
        return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

    def get_main_image(self, url = None):
        """ Get the main image from a webpage."""
        url = url or self.url

        try:
            response = requests.get(url)
            response.raise_for_status()  # Check that the request was successful
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to get the main image from the <meta property="og:image"> tag
            main_image = soup.find('meta', property='og:image')
            if main_image and main_image['content']:
                return main_image['content']

            # If no main image found in <meta>, look for the first <img> tag
            first_image = soup.find('img')
            if first_image and first_image['src']:
                return first_image['src']

            # If no image found, return None
            return None
        except requests.RequestException as e:
            print(f"Error making HTTP request: {e}")
            return None
        except Exception as e:
            print(f"Error processing the page: {e}")
            return None

    def get_context(self, url=None, length=500):
        """ Get the main text content from a url."""
        url = url or self.url
    
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                article = soup.find('article')
                if article:
                    texts = []
                    for tag in article.find_all(['h2', 'p']):
                        texts.append(tag.get_text())
                    text = ' '.join(texts)
                else:
                    text = ""
                text = text.strip()
                return text[:length]
            else:
                return f"Failed to retrieve content, status code: {response.status_code}"
        except Exception as e:
            return f"An error occurred: {e}"