#!/usr/bin/env python
# coding: utf-8

# # 8-K form #
# The function *parse_8k_filing()* takes a link as argument and returns a 
# dataframe with Company name, CIK, Item, and text. If items are not found,
#  then the function returns an error.
# **Caveats:** 
# The function is a parser. You need to feed a SEC txt link into it. 
# There are many python and r packages to get a direct link to the filings.

# required
import re
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import sys
import unicodedata

def parse_8k_filing(link):
    # retrieve the text file from SEC
    def get_text(link):
        page = requests.get(link)
        html = bs(page.content, "lxml")
        text = html.get_text().replace(u'\xa0', ' ').replace("\t", " ").replace("\x92", "'").split("\n")
        return(text)
    # find items reported in 8-k
    def get_items(text):
        itemPattern = re.compile("^(Item\s[1-9][\.\d]*)")
        value = list()
        for line in text:
            if itemPattern.search(line.strip()) is not None:
                value.append(itemPattern.search(line.strip()).group(0))

        return(value)
    # get the text associated with the items
    def get_data(file, items) :
        text8k = list()
        dataList = list()
        stop = re.compile("SIGNATURE", re.IGNORECASE)
        companyCik = re.compile("(CENTRAL INDEX KEY:)([\s\d]+)", re.IGNORECASE)
        companyName = re.compile("(COMPANY CONFORMED NAME:)(.+)", re.IGNORECASE)
        control = 0
        itemPattern = re.compile("|".join((["^" + i for i in items])))
        for line in file:
            if control == 0:
                if companyCik.search(line) is not None:
                    cik = companyCik.search(line).group(2).strip()
                if companyName.search(line) is not None:
                    conm = companyName.search(line).group(2).strip()
                if itemPattern.search(line) is not None:
                    it = itemPattern.search(line).group(0)
                    text8k.append(re.sub(it, "", line))
                    control = 1
            else:
                if itemPattern.search(line) is not None:
                    dataList.append([it, "\n".join(text8k)])
                    it = itemPattern.search(line).group(0)
                    text8k = list()
                    text8k.append(re.sub(it, "", line))

                elif stop.search(line) is not None:
                    dataList.append([it, "\n".join(text8k)])
                    text8k = list()
                    break
                else:
                    text8k.append(line)
        data = pd.DataFrame.from_dict(dataList)
        data.columns = ["item", "itemText"]
        data["cik"] = cik
        data["conm"] = conm
        data["edgar.link"] = link
        return(data)
    # Alternative version to extract items text from 8-K files 
    # in which lines are not properly divided.
    def get_data_alternative(file):
        dataList = list()
        fullText = " ".join(file)
        fullText = unicodedata.normalize("NFKD", fullText).encode('ascii', 'ignore').decode('utf8')
        itemPattern = re.compile("\.\s*(Item\s[1-9][\.\d]*)")
        items = itemPattern.findall(fullText)
        itemsStart = list()
        stop = re.compile("SIGNATURE", re.IGNORECASE)
        sig = stop.search(fullText).start()
        for i in items:
            itStartPattern = re.compile("\.\s*"+i)
            itemsStart.append(itStartPattern.search(fullText).start())
        itemsStart.append(sig)
        n = 1
        while n < len(itemsStart) :
            dataList.append([items[(n-1)], fullText[itemsStart[(n-1)]:itemsStart[n]]])
            n += 1
            
        companyCik = re.compile("(CENTRAL INDEX KEY:)([\s\d]+)", re.IGNORECASE)
        companyName = re.compile("(COMPANY CONFORMED NAME:)(.+)", re.IGNORECASE)
        cik = companyCik.search(fullText).group(2).strip()
        conm = companyName.search(fullText).group(2).strip()
        conm = re.sub("CENTRAL INDEX KEY.*", "", conm)
        conm = conm.strip()
        data = pd.DataFrame.from_dict(dataList)
        data.columns = ["item", "itemText"]
        data["cik"] = cik
        data["conm"] = conm
        data["edgar.link"] = link      
            
        return(data)
          
    
    file = get_text(link)
    items = get_items(file)
    if len(items) >= 1:      
        df = get_data(file, items)  
    else:
        try:
            df = get_data_alternative(file)
            
        except:
            sys.exit("No Items Found")
    
    return(df) 