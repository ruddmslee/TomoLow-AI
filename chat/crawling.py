import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from readability import Document
from bs4 import BeautifulSoup


CANDIDATE_SELECTORS = [   # 본문이 있을 법한 CSS 선택자
    "article",
    ".article-body", 
    ".post-content",
    ".content",
    ".entry-content",
    "#main-content",
    ".story-body",
]


"""
    불필요한 요소 제거 후 본문 추출
"""
def extract_by_readability(html):
    try:
        doc = Document(html)
        summary_html = doc.summary()
        soup = BeautifulSoup(summary_html, "html.parser")
        text = soup.get_text("\n", strip=True)
        return text
    except Exception:
        return None
    

"""
    Chrome 드라이버 생성 
"""
def get_driver(headless=True, proxy=None, block_images=True):
    options = Options()
    
    # 페이지 로딩 전략 - DOM만 로드
    options.page_load_strategy = "eager"
    
    # Docker 필수 옵션
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    
    # 봇 탐지 회피 (navigator.webdriver = true 숨김)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # 화면
    options.add_argument("--window-size=1920,1080")
    
    # User-Agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    
    # 이미지 차단 (속도 향상)
    if block_images:
        prefs = {
            "profile.managed_default_content_settings.images": 2,
        }
        options.add_experimental_option("prefs", prefs)
    
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    
    if headless:
        options.add_argument("--headless=new")
    
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # Stealth 패치
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}, app: {}};
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """
    })
    
    return driver


"""
    Cloudflare 차단 페이지 있는지 확인
"""
def has_cloudflare_challenge(page_source):
    page_lower = page_source.lower()
    return any(keyword in page_lower for keyword in [
        "just a moment",
        "checking your browser",
        "cf_chl_opt"
    ])

"""
    특정 url 크롤링
"""
def crawl_with_driver(driver, url, max_wait=5):
    try:
        driver.set_page_load_timeout(max_wait)
        driver.get(url)
        
        # 1. <body> 대기
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 2. Cloudflare 체크
        if has_cloudflare_challenge(driver.page_source):
            # Cloudflare가 있으면 대기 -> 챌린지 통과 시 탈출
            for i in range(max_wait * 2): 
                time.sleep(0.5)
                if not has_cloudflare_challenge(driver.page_source):
                    break
            
            # 여전히 챌린지가 있으면 실패로 간주
            if has_cloudflare_challenge(driver.page_source):
                return extract_by_readability(driver.page_source)
        
        # 3. 본문 찾기
        found_elem = None
        
        for sel in CANDIDATE_SELECTORS:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    found_elem = elems[0]
                    break
            except:
                continue
        
        # 4. 셀렉터 못 찾으면 스크롤 후 재시도
        if not found_elem:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.3)
            
            for sel in CANDIDATE_SELECTORS:
                try:
                    elems = driver.find_elements(By.CSS_SELECTOR, sel)
                    if elems:
                        found_elem = elems[0]
                        break
                except:
                    continue
        
        # 5. 본문 추출
        if found_elem:
            html = found_elem.get_attribute("outerHTML")
            text = extract_by_readability(html)
            if text and len(text) >= 100:
                return text
            return found_elem.text
        
        # 6. 폴백: 전체 페이지 readability
        return extract_by_readability(driver.page_source)
    
    except TimeoutException:
        print(f"[TIMEOUT] {url} (>{max_wait}s) → skip", flush=True)
        return None
    
    except Exception as e:
        print(f"Crawl error: {e}", flush=True)
        if driver:
            try:
                return extract_by_readability(driver.page_source)
            except:
                pass
        return None


"""
    메인 함수
"""
# ===== 단일 URL 크롤링 =====
def crawl(url, headless=True, proxy=None):
    driver = get_driver(headless=headless, proxy=proxy)
    try:
        return crawl_with_driver(driver, url)
    finally:
        driver.quit()

# ===== 여러 URL 크롤링 =====
class BatchCrawler:
    
    # 드라이버 재사용
    def __init__(self, headless=True, proxy=None):
        self.driver = get_driver(headless=headless, proxy=proxy)
    
    def crawl(self, url):
        return crawl_with_driver(self.driver, url)
    
    def close(self):
        try:
            self.driver.quit()
        except:
            pass

