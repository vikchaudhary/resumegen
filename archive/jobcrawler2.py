import requests
from bs4 import BeautifulSoup

def search_for_jobs_on_google_careers(query):
  """Searches the Google Careers site for jobs.

  Args:
    query: The query to search for.

  Returns:
    A list of job listings.
  """

  url = "https://careers.google.com/jobs/search/?q=" + query
  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")
  job_elements = soup.find_all("div", class_="job-result")
  job_listings = []
  for job_element in job_elements:
    job_listing = {
        "title": job_element.find("h2").text,
        "location": job_element.find("span", class_="location").text,
        "url": job_element.find("a").get("href"),
    }
    job_listings.append(job_listing)
  return job_listings


if __name__ == "__main__":
  query = "software engineer"
  job_listings = search_for_jobs_on_google_careers(query)
  for job_listing in job_listings:
    print(job_listing)
