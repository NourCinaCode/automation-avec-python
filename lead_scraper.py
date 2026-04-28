"""
Lead Scraper Bot
Scrapes business emails and contacts from any website
Usage: python lead_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import time
from urllib.parse import urljoin, urlparse

def get_emails_from_page(url):
    """Extract all emails from a webpage"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find emails using regex
        text = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        
        # Also find phone numbers
        phones = re.findall(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text)
        
        # Find page title (business name)
        title = soup.find('title')
        name = title.text.strip() if title else urlparse(url).netloc
        
        return {
            'url': url,
            'name': name,
            'emails': list(set(emails)),
            'phones': list(set(phones[:3]))  # first 3 phones
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_google_results(query, num_pages=3):
    """Scrape websites from Google search results"""
    urls = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for page in range(num_pages):
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&start={page*10}"
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/url?q=' in href:
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    if actual_url.startswith('http') and 'google' not in actual_url:
                        urls.append(actual_url)
            
            time.sleep(2)  # Be respectful, avoid blocks
        except Exception as e:
            print(f"Error on page {page}: {e}")
    
    return list(set(urls))

def save_leads_to_csv(leads, filename='leads.csv'):
    """Save all leads to a CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Business Name', 'Website', 'Email', 'Phone'])
        
        for lead in leads:
            if lead and lead['emails']:
                for email in lead['emails']:
                    writer.writerow([
                        lead['name'],
                        lead['url'],
                        email,
                        lead['phones'][0] if lead['phones'] else ''
                    ])
    
    print(f"\n✅ Saved {len(leads)} leads to {filename}")

def main():
    print("=" * 50)
    print("🔍 LEAD SCRAPER BOT")
    print("=" * 50)
    
    # Get search query from user
    query = input("\nEnter search query (e.g. 'restaurants in Casablanca'): ")
    num_pages = int(input("How many pages to scrape? (1-5): ") or "2")
    
    print(f"\n🌐 Searching Google for: {query}")
    urls = scrape_google_results(query, num_pages)
    print(f"Found {len(urls)} websites to scrape...")
    
    leads = []
    for i, url in enumerate(urls[:20]):  # Max 20 sites
        print(f"Scraping [{i+1}/{min(len(urls), 20)}]: {url}")
        lead = get_emails_from_page(url)
        if lead:
            leads.append(lead)
        time.sleep(1)
    
    # Show results
    print("\n📊 RESULTS:")
    print("-" * 40)
    for lead in leads:
        if lead['emails']:
            print(f"✅ {lead['name']}")
            print(f"   Emails: {', '.join(lead['emails'])}")
            if lead['phones']:
                print(f"   Phone: {lead['phones'][0]}")
            print()
    
    # Save to CSV
    save_leads_to_csv(leads)
    print(f"\n💰 You can sell these {len(leads)} leads for $50-$200!")

if __name__ == "__main__":
    main()
