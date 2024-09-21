from flask import Flask, render_template , request
import pymongo
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen 

app = Flask(__name__)

@app.route('/',methods = ['GET'])
def main_method():
    return render_template('index.html')

@app.route('/findingContent', methods=['POST'])
def findCone():
    content = request.form['content']
    search_str = "https://www.amazon.in/s?k=" + content
    search_content = urlopen(search_str)
    amazon_page = search_content.read()
    amazon_html = bs(amazon_page, 'html.parser')
    
    a1 = amazon_html.find('div', {'class': 's-main-slot s-result-list s-search-results sg-row'}).findAll('div', {"data-component-type": "s-search-result"})
    
    reviews = []

    client = pymongo.MongoClient("mongodb+srv://sahil:Sahil2020@cluster0.9rhuxt2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

    db = client['webScrapping']
    amazon_data = db["amazon"]
    
    for ind, item in enumerate(a1):
        if ind == 3:  # Limit to 2 products
            break
        
        product_url = "https://www.amazon.in" + item.find('a', {"class": "a-link-normal s-no-outline"})['href']
        search_content = urlopen(product_url)
        amazon_page = search_content.read()
        amazon_html = bs(amazon_page, 'html.parser')
        
        name = amazon_html.find('span', {"class": "a-size-large product-title-word-break"})
        price = amazon_html.find('span', {"class": "a-price-whole"})
        rating_element = amazon_html.find('span', {"class": "a-size-medium a-color-base"})
        comment_element = amazon_html.find('p', {"class": "a-spacing-small"})
        
        reviews.append({
            "Product": content,
            "Name": name.text.strip() if name else "Not Available",
            "Rating": rating_element.text.split(" ")[0] if rating_element else "Not Available",
            "price": price.text.strip() if price else "Not Available",
            "Comment": comment_element.span.text if comment_element and comment_element.span else "Not Available"
        })
        amazon_data.insert_one(reviews[ind]) 

    # Debug output
    print(reviews)
    
    return render_template('result.html', reviews=reviews)


if __name__== "__main__":
    app.run(host="0.0.0.0")