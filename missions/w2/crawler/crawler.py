import os
import time
import logging
import re
from multiprocessing import Process
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from schema import Review, JsonHandler

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class SteamReviewCrawler:
    def __init__(self, app_id: int, review_type: str, target_reviews: int = 2000):
        self.app_id = app_id
        self.review_type = review_type  # 'positive' or 'negative'
        self.target_reviews = target_reviews
        self.count = 0
        self.seen_review_ids = set()
        self.base_url = os.environ.get(
            "STEAM_API_URL", 
            f"https://steamcommunity.com/app/{self.app_id}/{self.review_type}reviews/"
        )

    def fetch_reviews(self):
        lang = 'english'
        # 추출 url 설정
        url = f"{self.base_url}?browsefilter=toprated&filterLanguage={lang}"
        logging.info(f"[{self.review_type.upper()}] Opening browser to URL: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(url)
                # 해당 상품의 페이지를 가져오기. 리뷰를 가져오기 위해서는 리뷰가 로딩될 때까지 기다려야 함.
                page.wait_for_selector('div.apphub_Card', timeout=15000)
            except Exception as e:
                logging.error(f"[{self.review_type.upper()}] Failed to load page or find reviews: {e}")
                browser.close()
                return
            
            last_card_count = 0
            retries = 0
            
            while self.count < self.target_reviews:
                # 무한 스크롤 작동시키기
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # HTML DOM이 업데이트될 때까지 잠시 대기
                time.sleep(1.5)
                
                html = page.content()
                soup = BeautifulSoup(html, 'lxml')
                cards = soup.find_all('div', class_='apphub_Card')
                
                # 다음 리뷰가 있는지 5회 재시도
                if len(cards) == last_card_count:
                    retries += 1
                    if retries > 5:
                        logging.warning(f"[{self.review_type.upper()}] No new reviews loaded after 5 retries. End of list.")
                        break
                    time.sleep(2) 
                    continue
                else:
                    retries = 0 
                
                last_card_count = len(cards)
                
                # 리뷰 파싱
                for card in cards:
                    modal_url = card.get('data-modal-content-url', '')
                    review_id = modal_url if modal_url else str(hash(card.text))
                        
                    if review_id in self.seen_review_ids:
                        continue
                    
                    self.seen_review_ids.add(review_id)
                    
                    # User Name
                    user_name = None
                    name_div = card.find('div', class_='apphub_CardContentAuthorName')
                    if name_div and name_div.a:
                        user_name = name_div.a.text.strip()
                        
                    # Playtime
                    playtime_hours = 0.0
                    hours_div = card.find('div', class_='hours')
                    if hours_div:
                        hours_text = hours_div.text.strip()
                        hmatch = re.search(r'([\d\.]+)\s*hrs', hours_text)
                        if hmatch:
                            playtime_hours = float(hmatch.group(1))
                            
                    # Sentiment
                    sentiment = "Positive"
                    title_div = card.find('div', class_='title')
                    if title_div:
                        title_text = title_div.text.strip().lower()
                        if 'not recommended' in title_text:
                            sentiment = "Negative"

                    # Date and Text
                    review_text = ""
                    date_posted = ""
                    text_content = card.find('div', class_='apphub_CardTextContent')
                    if text_content:
                        date_div = text_content.find('div', class_='date_posted')
                        if date_div:
                            date_str = date_div.text.replace('Posted:', '').strip()
                            date_posted = date_str
                            date_div.extract() 
                        
                        review_text = text_content.get_text(separator=' ', strip=True)
                        
                    # Helpful Count
                    helpful_count = 0
                    helpful_div = card.find('div', class_='found_helpful')
                    if helpful_div:
                        helpful_text = helpful_div.get_text(separator=' ', strip=True)
                        num_match = re.search(r'([\d,]+)\s*people found this review helpful', helpful_text)
                        if num_match:
                            helpful_count = int(num_match.group(1).replace(',', ''))
                            
                    review_obj = Review(
                        review_id=review_id,
                        user_name=user_name,
                        playtime_hours=playtime_hours,
                        sentiment=sentiment,
                        review_text=review_text,
                        date_posted=date_posted,
                        helpful_count=helpful_count
                    )
                    
                    self.count += 1
                    yield review_obj
                    
                    if self.count >= self.target_reviews:
                        break
                        
            browser.close()

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Stream Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File Handler
    os.makedirs(DATA_DIR, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(DATA_DIR, 'crawler.log'), encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def run_crawler(app_id, review_type, output_file):
    setup_logger()
    crawler = SteamReviewCrawler(app_id=app_id, review_type=review_type, target_reviews=2000)
    handler = JsonHandler(output_file)
    
    try:
        logging.info(f"[{review_type.upper()}] Starting crawler...")
        for review in crawler.fetch_reviews():
            handler.append(review)
            if crawler.count % 100 == 0:
                logging.info(f"[{review_type.upper()}] Successfully crawled and saved {crawler.count} reviews so far.")
    except Exception as e:
        logging.error(f"[{review_type.upper()}] Crawler stopped due to exception: {e}")
    finally:
        handler.close()
        logging.info(f"[{review_type.upper()}] Finished crawling. Total collected: {crawler.count}")


if __name__ == "__main__":
    setup_logger()
    
    app_id = 4704690
    
    # 긍정 리뷰 + 부정 리뷰 멀티 프로세스로 동시에 가져옴
    p_positive = Process(target=run_crawler, args=(app_id, "positive", os.path.join(DATA_DIR, "output_positive.json")))
    p_negative = Process(target=run_crawler, args=(app_id, "negative", os.path.join(DATA_DIR, "output_negative.json")))
    
    logging.info("Starting concurrent crawling for positive and negative reviews...")
    p_positive.start()
    p_negative.start()
    
    p_positive.join()
    p_negative.join()
    logging.info("All crawling processes have finished.")
