import os
import requests
from bs4 import BeautifulSoup
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS untuk semua endpoint

BASE_URL = "https://disnakerja.com"
DATA_DIR = 'data/'

# Fungsi untuk melakukan scraping pekerjaan
def scrape_job_listings(start_page=1, end_page=20):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    job_listings = []
    
    for page in range(start_page, end_page + 1):
        url = f"{BASE_URL}/page/{page}/"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}, status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        job_articles = soup.find_all('article', class_='gmr-box-content')

        for article in job_articles:
            title = article.find('h2', class_='post-title').get_text(strip=True)
            company_url = article.find('a', itemprop='url')['href']
            
            # Mencoba mencari nama perusahaan di tempat lain
            company_name = article.find('h3', class_='post-sub-title')  # Cari berdasarkan elemen lain
            if company_name:
                company_name = company_name.get_text(strip=True)
            else:
                company_name = title  # Fallback ke job-title jika tidak ditemukan

            job_description = article.find('div', class_='entry-content').get_text(strip=True) if article.find('div', class_='entry-content') else None

            job_listings.append({
                'Company Name': title,
                # 'Job Title': title,
                'Job URL': company_url,
                'Description': job_description
            })
    
    return job_listings

# Fungsi untuk menyimpan data pekerjaan ke file JSON
def save_to_json(job_listings, filename='job_listings.json'):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, filename), 'w', encoding='utf-8') as f:
        json.dump(job_listings, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {os.path.join(DATA_DIR, filename)}")

# Fungsi untuk mendapatkan data pekerjaan
def get_job_listings():
    try:
        with open(os.path.join(DATA_DIR, 'job_listings.json'), 'r', encoding='utf-8') as f:
            job_listings = json.load(f)
        return job_listings
    except FileNotFoundError:
        print(f"{os.path.join(DATA_DIR, 'job_listings.json')} not found. Scraping and saving data...")
        job_listings = scrape_job_listings(start_page=1, end_page=10)
        save_to_json(job_listings)
        return job_listings

# Route untuk menampilkan pesan di halaman utama
@app.route('/')
def index():
    return "API success please use /api/jobs"

# Endpoint API untuk mendapatkan data pekerjaan
@app.route('/api/jobs', methods=['GET'])
def api_get_jobs():
    job_listings = get_job_listings()  # Memuat data pekerjaan
    return jsonify(job_listings)

if __name__ == '__main__':
    app.run(debug=True)
