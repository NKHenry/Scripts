#web scraping script to take taste.com recipes and export xml documents
#recipes from the nutritional information subset at taste
#for use in COMP4920 software project, not intented for public use
from urllib import urlretrieve
import urllib2
import sys
from bs4 import BeautifulSoup
import re
from sets import Set
import codecs

source = sys.argv[1]


for i in range (0,3):

    page = urllib2.urlopen(source)

    soup = BeautifulSoup(page)
    soup.prettify()

    #get next page of recipes
    button = soup.find('a', class_="button next-page")
    next = button['href']

    #get all recipes
    block = soup.find('div', class_="content-item tab-content current")
    recipes = block.find_all('a')

    urls = Set()
    for recipe in recipes:
        if 'href' in recipe.attrs and recipe['href'] not in urls:
            urls.add(recipe['href'])

    for link in urls:
        page = urllib2.urlopen(link)

        soup = BeautifulSoup(page)
        soup.prettify()

        if soup.find('h1', itemprop="name"):
            title = soup.find('h1', itemprop="name")
            print title
            recipename = re.sub(" ", "_", title.string)
        else:
            continue

        if soup.find('td', class_="servings"):
            servings = soup.find('td', class_="servings")
        else:
            continue

        if soup.find('ul', class_="ingredient-table"):
            ingredients = soup.find('ul', class_="ingredient-table")
        else:
            continue

        #nutrition is per serve
        if soup.find('table', class_="nutrition-table"):
            nutrition = soup.find('table', class_="nutrition-table")
        else:
            continue

        if soup.find('div', class_="content-item tab-content current method-tab-content"):
            directions = soup.find('div', class_="content-item tab-content current method-tab-content")
        else:
            continue

        #get retrieve image and get extension
        imageTag = soup.find('div', class_="recipe-image-wrapper")
        image = imageTag.img['src']
        outpath = re.search(".*/.*\.([a-z]+)$", image)
        imgExtension = outpath.group(1)
        imgName = recipename + "." +imgExtension
        urlretrieve(image, imgName)

        outfile = recipename + ".xml"
        f = codecs.open(outfile, "w", 'utf_8')
        f.write("<recipe>\n")
        f.write("<head>\n")
        f.write("\t<title>"+title.string+"</title>\n")
        f.write("\t<yield>"+servings.em.string+"</yield>\n</head>\n")
        f.write("<ingredients>\n")
        for ing in ingredients.find_all("li"):
            f.write("\t<ing>\n\t\t<item>")
            f.write(ing.label.string.strip()+"\t\t</item>\n\t</ing>\n")

        f.write("</ingredients>\n")
        f.write("<nutrition>\n")
        line = ""
        for stat in nutrition.stripped_strings:
            if re.search("[0-9]", stat):
                line = re.sub("><", ">"+stat+"<", line)
                f.write(line)
            else:
                line = "\t<"+stat+"></"+stat+">\n"
        f.write("</nutrition>\n")

        f.write("<directions>\n")
        for step in directions.find_all('p', class_="description"):
            f.write("\t<step>"+step.string+"</step>\n")

        f.write("</directions>\n")
        f.write("<img>"+imgName+"</img>\n")
        f.write("</recipe>")
        f.close()

    source = next
