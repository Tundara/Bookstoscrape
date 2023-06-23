import requests

from bs4 import BeautifulSoup
import csv

def writeInCsv(allData, filename):
    header = ["product_page_url", "universal_ product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"]
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(allData)

    print("FILE: "+filename+" Successfully created")

def getPageFromRequest(url):
    r = requests.get(url=url).content
    soup = BeautifulSoup(r, 'html.parser')
    
    return soup

def getProductInfo(url):
    page = getPageFromRequest(url)
    table = page.find("table", {"class", "table table-striped"}).find_all("td")
    data = []

    title = page.find("div", {"class", "product_main"}).h1.text.strip().encode('ascii', 'ignore').decode("ascii")
    available = page.find("p", {"class", "availability"}).text.strip()
    description = page.findAll("p")[3].text.strip().encode('ascii', 'ignore').decode("ascii")
    upc = table[0].text.strip()
    product_inc_tax = table[3].text.strip().encode('ascii', 'ignore').decode("ascii")
    product_exc_tax = table[2].text.strip().encode('ascii', 'ignore').decode("ascii")
    image_url = page.find("div", {"class": "item active"}).img["src"].strip()
    review = table[6].text.strip()
    
    data.append([url, upc, title, product_inc_tax, product_exc_tax, available, description, "category", review, image_url])
    
    return data
    
    
def getAllCategories(url):
    page = getPageFromRequest(url)
    categories = []
    cat = page.find("ul", {"class":"nav nav-list"}).find("li").find("ul").find_all("li")
    for cate in cat:
        categories.append(cate.find("a")["href"].split("index.html")[0])
    
    return categories

def getCategoryInfo(url):
    page = getPageFromRequest(url)
    categories = []
    
    bookList = page.find("section").find("ol").find_all("li")
  
    for book in bookList:
        categories.append(book.find("a").get("href"))
    
    return categories
  
def getCategoryNumber(url):
    page = getPageFromRequest(url)
    try:
        number = page.find("li", {"class", "current"}).text.strip().split("Page 1 of ")[1]
    except:
        number = 1
    
    return number

def getCategoryData(url, categoryname):
    allData = []
    categoryInfo = getCategoryInfo(url)
    number = getCategoryNumber(url)

    i=1
    path = "" 
    for _ in range(0, int(number)):
        if i <= number:
            print(url+path)
            categoryInfo = getCategoryInfo(url+path)
            for book in categoryInfo:
                newData = getProductInfo("http://books.toscrape.com/catalogue"+book.split("../../..")[1])
                allData.extend(newData)
            i+=1
            path = "page-"+str(i)+".html"

    writeInCsv(allData, "./data/"+categoryname.split("catalogue/category/books/")[1].split("/")[0]+"-data.csv")
 
def main():
    url = "https://books.toscrape.com/"
    categories = getAllCategories(url)
    for category in categories:
        getCategoryData(url+category, category)

if __name__ == "__main__":
    main()