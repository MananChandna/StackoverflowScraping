from flask import Flask, render_template, request
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape Stack Overflow
def scrape_stackoverflow(tag):
    base_url = 'https://stackoverflow.com/questions/tagged/'
    query_filter = 'Votes'
    url = f"{base_url}{tag}?tab={query_filter}"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        post_summaries = soup.find_all(class_=['s-post-summary'])
        data = []

        for post_summary in post_summaries:
            question_title = post_summary.find(class_='s-post-summary--content-title').text.strip()
            votes = post_summary.find(class_='s-post-summary--stats-item-number').text.strip()
            tags = post_summary.find(class_='tags').text.strip()
            
            post_data = {
                'question_title': question_title,
                'votes': votes,
                'tags': tags
            }

            data.append(post_data)
        
        return data
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_tag = request.form['search_tag']
        if search_tag:
            data = scrape_stackoverflow(search_tag)
            if data:
                df = pd.DataFrame(data)
                df.to_csv("stackoverflow_data.csv", index=False)
                return render_template('index.html', data=data, search_tag=search_tag)
            else:
                error_message = "Failed to fetch data from Stack Overflow. Please try again later."
                return render_template('index.html', error_message=error_message)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
