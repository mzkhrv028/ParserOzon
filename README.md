# ParserOzon
### Overview
This project allows you to extract data from the [Ozon](https://www.ozon.ru/) website in json format using the **Scrapy**, **Selenium** libraries.
### Install
Download the program to your computer:
```bash
git clone https://github.com/murreds/ParserOzon.git
```
And install the required libraries.
```bash
python3 -m pip install -r requirements.txt
```
> **Note:** Firefox browser installed is required.
### Features
- Extracting data from the first pages and by category of card products.
- Obtaining data on the characteristics of the each products by category.
### Usage
First, go to the project directory and enter the command:
```bash
cd ./ozonscraper
```
To get data about each product card from the first pages, enter:
```bash
scrapy crawl cardproduct -a category={category} [-a page=page] [-a mode=full]
```
To get product characteristics data, enter:
```bash
scrapy crawl chproduct -a category={category}
```
The category must be one of 'smartphone, tv, tablets, laptop'. \
Data is stored in a directory: */path/to/project/directory/ozonscraper/data*
> **Important:** first you need to use the first command then the second.
### Example
```bash
scrapy crawl cardproduct -a category=laptop -a page=2 && scrapy crawl chproduct -a category=laptop
```
