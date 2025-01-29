import requests
from bs4 import BeautifulSoup

def search_jobs_by_company(company_name):
    base_url = "https://careers.google.com/"  # Replace this with the actual company's career page URL
    search_url = f"{base_url}/search?q={company_name}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        job_listings = []

        # Modify the selectors below to match the structure of the company's career page
        for job in soup.select('.job-listing'):
            job_title = job.select_one('.job-title').text.strip()
            company = job.select_one('.company-name').text.strip()
            job_url = base_url + job.select_one('.job-link')['href']
            
            job_data = {
                'title': job_title,
                'company': company,
                'url': job_url,
            }
            job_listings.append(job_data)

        return job_listings

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return []

if __name__ == "__main__":
    company_name = "google"  # Replace this with the company name you want to search for
    jobs = search_jobs_by_company(company_name)

    if jobs:
        print(f"Job postings at {company_name}:")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['title']} at {job['company']}")
            print(f"   URL: {job['url']}\n")
    else:
        print(f"No job postings found for {company_name}.")
