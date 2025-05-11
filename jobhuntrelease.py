import requests
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import os
import re
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")

# Set up Chrome options for Selenium
chrome_options = Options()
# chrome_options.add_argument('--headless')  # Run in headless mode
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Common headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

USER_AGENTS = [
    # Add more user agents as needed
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
    # ... more ...
]

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': HEADERS['Accept'],
        'Accept-Language': HEADERS['Accept-Language'],
    }

# Job sites with their specific selectors
JOB_SITES = {
    'LinkedIn': {
        'url': 'https://www.linkedin.com/jobs/search/?keywords=2026%20new%20grad%20software',
        'job_cards': 'div.job-card-container',
        'title': 'h3.base-search-card__title',
        'link': 'a.base-card__full-link',
        'company': 'h4.base-search-card__subtitle'
    },
    'Indeed': {
        'url': 'https://www.indeed.com/jobs?q=2026+new+grad+software&sort=date',
        'job_cards': 'div.job_seen_beacon',
        'title': 'h2.jobTitle',
        'link': 'a.jcs-JobTitle',
        'company': 'span.companyName'
    }
}

# Top 50 tech companies and their career page URLs
COMPANY_CAREERS = {
    "Microsoft": "https://careers.microsoft.com/us/en/search-results?keywords=new%20grad",
    "Apple": "https://jobs.apple.com/en-us/search?search=new%20grad",
    "NVIDIA": "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite?keywords=new%20grad",
    "Amazon": "https://www.amazon.jobs/en/search?base_query=new+grad",
    "Google": "https://careers.google.com/jobs/results/?q=new%20grad",
    "Meta": "https://www.metacareers.com/jobs/?q=new%20grad",
    "Broadcom": "https://careers.broadcom.com/jobs?keywords=new%20grad",
    "Tesla": "https://www.tesla.com/careers/search/?query=new%20grad",
    "TSMC": "https://www.tsmc.com/english/careers/search-job?keyword=new%20grad",
    "Tencent": "https://careers.tencent.com/en-us/career.html?keywords=new%20grad",
    "Netflix": "https://jobs.netflix.com/search?q=new%20grad",
    "Oracle": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobSearch?keyword=new%20grad",
    "SAP": "https://jobs.sap.com/search/?q=new%20grad",
    "Alibaba": "https://talent.alibaba.com/off-campus?lang=en_US",
    "ASML": "https://www.asml.com/en/careers/find-your-job?searchTerm=new%20grad",
    "Palantir": "https://www.palantir.com/careers/?search=new%20grad",
    "Salesforce": "https://www.salesforce.com/company/careers/search-jobs/?keywords=new%20grad",
    "Samsung": "https://www.samsung.com/us/careers/search/?keyword=new%20grad",
    "Cisco": "https://jobs.cisco.com/jobs/SearchJobs/?keywords=new%20grad",
    "IBM": "https://www.ibm.com/employment/entrylevel/",
    "ServiceNow": "https://careers.servicenow.com/careers/jobs?keywords=new%20grad",
    "Intuit": "https://careers.intuit.com/search-jobs?k=new%20grad",
    "Uber": "https://www.uber.com/global/en/careers/list/?q=new%20grad",
    "Xiaomi": "https://hr.xiaomi.com/en/job-posts?search=new%20grad",
    "AMD": "https://jobs.amd.com/search/?q=new%20grad",
    "Booking Holdings": "https://careers.bookingholdings.com/search/?q=new%20grad",
    "Adobe": "https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced?keywords=new%20grad",
    "QUALCOMM": "https://jobs.qualcomm.com/search-jobs/new%20grad/2768/1",
    "Texas Instruments": "https://careers.ti.com/search-jobs/new%20grad/3297/1",
    "PDD Holdings": "https://careers.pinduoduo.com/en/",
    "Sony": "https://www.sonyjobs.com/search-jobs/new%20grad/",
    "Schneider Electric": "https://www.se.com/ww/en/about-us/careers/job-search/?search=new%20grad",
    "Spotify": "https://www.spotifyjobs.com/search-jobs/?q=new%20grad",
    "Applied Materials": "https://careers.appliedmaterials.com/search/?q=new%20grad",
    "ADP": "https://jobs.adp.com/search-jobs/new%20grad/",
    "MercadoLibre": "https://careers.mercadolibre.com/search/?q=new%20grad",
    "Palo Alto Networks": "https://jobs.paloaltonetworks.com/search/?q=new%20grad",
    "Arm Holdings": "https://careers.arm.com/search/?q=new%20grad",
    "Shopify": "https://www.shopify.com/careers/search?query=new%20grad",
    "MicroStrategy": "https://www.microstrategy.com/en/company/careers?search=new%20grad",
    "AppLovin": "https://www.applovin.com/careers/?search=new%20grad",
    "Meituan": "https://zhaopin.meituan.com/en?search=new%20grad",
    "Arista Networks": "https://www.arista.com/en/company/careers?search=new%20grad",
    "Keyence": "https://www.keyence.com/careers/search/?q=new%20grad",
    "Analog Devices": "https://careers.analog.com/search/?q=new%20grad",
    "CrowdStrike": "https://www.crowdstrike.com/careers/?search=new%20grad",
    "Fiserv": "https://www.careers.fiserv.com/search-jobs/new%20grad/",
    "Lam Research": "https://careers.lamresearch.com/search/?q=new%20grad",
    "Micron Technology": "https://micron.eightfold.ai/careers?query=new%20grad",
    "Nintendo": "https://careers.nintendo.com/search/?q=new%20grad",
    "SK Hynix": "https://recruit.skhynix.com/en/careers/job-search?search=new%20grad",
    "Intel": "https://jobs.intel.com/en/search-jobs/new%20grad/",
    # ... add more as needed ...
}

# Load previous notifications
if os.path.exists("notified_jobs.json"):
    with open("notified_jobs.json", "r") as f:
        notified_jobs = set(json.load(f))
else:
    notified_jobs = set()

JOB_SEARCH_QUERIES = [
    "2026 new grad",
    "2026 university graduate",
    "2026 entry level",
    "2025 fall internship",
    "2025 fall co-op",
    "2025-2026 university",
    "fall 2025 internship",
    "fall 2025 co-op",
    "new graduate software engineer",
    "university grad 2026",
    "software engineer intern 2025",
    "2025 internship",
    "2025 co-op",
    "2026 grad",
    "2026 graduate",
    "2026 full time",
    "2025-2026 new grad"
]

JOB_BOARDS = {
    "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords={query}",
    "Indeed": "https://www.indeed.com/jobs?q={query}&sort=date",
    # Add more boards as needed
}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(f"Sent Telegram message: {message}")
    else:
        print(f"Failed to send Telegram message: {response.text}")

def setup_driver():
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return uc.Chrome(options=options)

def matches_keywords(title):
    title_lower = title.lower()
    for keyword in JOB_SEARCH_QUERIES:
        # Use regex to allow for flexible matching (e.g., ignore punctuation, allow partial matches)
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        if pattern.search(title_lower):
            return True
    return False

def check_job_site(site_name, site_config):
    driver = None
    try:
        driver = setup_driver()
        driver.get(site_config['url'])
        
        # Wait for job cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, site_config['job_cards']))
        )
        
        # Get all job cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, site_config['job_cards'])
        
        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, site_config['title']).text
                link = card.find_element(By.CSS_SELECTOR, site_config['link']).get_attribute('href')
                company = card.find_element(By.CSS_SELECTOR, site_config['company']).text
                
                if matches_keywords(title):
                    if link not in notified_jobs:
                        message = f"New 2026 New Grad Job at {company}:\n{title}\n{link}"
                        send_telegram_message(message)
                        notified_jobs.add(link)
            except Exception as e:
                print(f"Error processing job card: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error checking {site_name}: {str(e)}")
    finally:
        if driver:
            driver.quit()

def check_company_careers(company, url):
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        
        # Wait for content to load
        time.sleep(5)  # Basic wait, can be improved with specific selectors
        
        # Get all links
        links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            try:
                title = link.text
                href = link.get_attribute('href')
                
                if href and matches_keywords(title):
                    if href not in notified_jobs:
                        message = f"{company}: {title}\n{href}"
                        send_telegram_message(message)
                        notified_jobs.add(href)
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error checking {company}: {str(e)}")
    finally:
        if driver:
            driver.quit()

def check_job_boards():
    for query in JOB_SEARCH_QUERIES:
        for board, url_template in JOB_BOARDS.items():
            url = url_template.format(query=query.replace(' ', '+'))
            # Use your existing scraping logic here, e.g. with Selenium or requests+BeautifulSoup
            # Notify if a new job is found

def check_tech_internships_github():
    url = "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/listings.json"
    try:
        response = requests.get(url, headers=get_random_headers())
        random_delay()
        data = response.json()
        for job in data:
            title = job.get('position', '')
            company = job.get('company', '')
            link = job.get('url', '')
            if matches_keywords(title):
                if link and link not in notified_jobs:
                    message = f"[GitHub] {company}: {title}\n{link}"
                    send_telegram_message(message)
                    notified_jobs.add(link)
    except Exception as e:
        print(f"Error checking Tech Internships GitHub JSON: {str(e)}")

def check_simplify_jobs():
    base_url = "https://simplify.jobs/api/listings?query={query}"
    for query in JOB_SEARCH_QUERIES:
        url = base_url.format(query=query.replace(' ', '%20'))
        try:
            response = requests.get(url, headers=get_random_headers())
            random_delay()
            data = response.json().get('listings', [])
            for job in data:
                title = job.get('title', '')
                company = job.get('company', '')
                link = f"https://simplify.jobs{job.get('url', '')}"
                if matches_keywords(title):
                    if link and link not in notified_jobs:
                        message = f"[Simplify] {company}: {title}\n{link}"
                        send_telegram_message(message)
                        notified_jobs.add(link)
        except Exception as e:
            print(f"Error checking Simplify.jobs for query '{query}': {str(e)}")

def check_levels_fyi():
    url = "https://www.levels.fyi/companies/"
    try:
        response = requests.get(url, headers=get_random_headers())
        random_delay()
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a['href']
            if matches_keywords(title):
                if link and link not in notified_jobs:
                    message = f"[Levels.fyi]: {title}\n{link}"
                    send_telegram_message(message)
                    notified_jobs.add(link)
    except Exception as e:
        print(f"Error checking Levels.fyi: {str(e)}")

def check_yc_work_at_startup():
    url = "https://www.workatastartup.com/jobs"
    try:
        response = requests.get(url, headers=get_random_headers())
        random_delay()
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a['href']
            if matches_keywords(title):
                if link and link not in notified_jobs:
                    message = f"[YC Work at a Startup]: {title}\n{link}"
                    send_telegram_message(message)
                    notified_jobs.add(link)
    except Exception as e:
        print(f"Error checking YC Work at a Startup: {str(e)}")

def check_greenhouse_lever_workday():
    # Example: Greenhouse job board search for "new grad" and "intern"
    greenhouse_url = "https://boards.greenhouse.io/embed/job_board?for=&search={query}"
    lever_url = "https://jobs.lever.co/jobs?commit=Search&query={query}"
    workday_url = "https://www.myworkdayjobs.com/search/jobs?search={query}"
    for query in JOB_SEARCH_QUERIES:
        # Greenhouse
        try:
            url = greenhouse_url.format(query=query.replace(' ', '+'))
            response = requests.get(url, headers=get_random_headers())
            random_delay()
            soup = BeautifulSoup(response.text, "html.parser")
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                link = a['href']
                if matches_keywords(title):
                    if link and link not in notified_jobs:
                        message = f"[Greenhouse]: {title}\n{link}"
                        send_telegram_message(message)
                        notified_jobs.add(link)
        except Exception as e:
            print(f"Error checking Greenhouse for query '{query}': {str(e)}")
        # Lever
        try:
            url = lever_url.format(query=query.replace(' ', '+'))
            response = requests.get(url, headers=get_random_headers())
            random_delay()
            soup = BeautifulSoup(response.text, "html.parser")
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                link = a['href']
                if matches_keywords(title):
                    if link and link not in notified_jobs:
                        message = f"[Lever]: {title}\n{link}"
                        send_telegram_message(message)
                        notified_jobs.add(link)
        except Exception as e:
            print(f"Error checking Lever for query '{query}': {str(e)}")
        # Workday
        try:
            url = workday_url.format(query=query.replace(' ', '+'))
            response = requests.get(url, headers=get_random_headers())
            random_delay()
            soup = BeautifulSoup(response.text, "html.parser")
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                link = a['href']
                if matches_keywords(title):
                    if link and link not in notified_jobs:
                        message = f"[Workday]: {title}\n{link}"
                        send_telegram_message(message)
                        notified_jobs.add(link)
        except Exception as e:
            print(f"Error checking Workday for query '{query}': {str(e)}")

def check_jobs():
    try:
        # Get top 50 tech companies
        companies = get_tech_companies_from_marketcap()
        
        # Check company career pages
        for company in companies:
            # Construct career page URL based on company name
            career_url = f"https://careers.{company.lower().replace(' ', '')}.com"
            check_company_careers(company, career_url)
            
    except Exception as e:
        print(f"Error in check_jobs: {str(e)}")
        send_telegram_message("Error in job checker: " + str(e))

    # Save at end of check_jobs()
    with open("notified_jobs.json", "w") as f:
        json.dump(list(notified_jobs), f)

def get_tech_companies_from_marketcap(pages=2):
    base_url = "https://companiesmarketcap.com/tech/largest-tech-companies-by-market-cap/?page={}"
    companies = []
    for page in range(1, pages+1):
        url = base_url.format(page)
        response = requests.get(url, headers=get_random_headers())
        random_delay()
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.select("table tr"):
            cols = row.find_all("td")
            if len(cols) > 1:
                name = cols[1].get_text(strip=True)
                if name and name not in companies:
                    companies.append(name)
                    if len(companies) >= 50:  # Stop after getting 50 companies
                        return companies
    return companies

def random_delay(min_sec=2, max_sec=6):
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

if __name__ == "__main__":
    try:
        send_telegram_message("Test: This is a notification from your job script!")
        send_telegram_message("Job checker started! Will notify you of new 2026 grad jobs or fall co-op/internships from top 50 tech companies.")
        while True:
            check_jobs()
            time.sleep(300)  # Check every 5 minutes
    except KeyboardInterrupt:
        print("Job checker stopped by user")
        send_telegram_message("Job checker stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        send_telegram_message("Fatal error in job checker: " + str(e))
