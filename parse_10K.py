#!/usr/bin/env python
# coding: utf-8

# # 10-K form
# ## Business, Risk, and MD&A
# The function *parse_10k_filing()* parses 10-K forms to extract the following sections: business description, business risk, and management discussioin and analysis. The function takes two arguments, a link and a string indicating the section. Current options are **"All", "Business", "Risk", "MDA."**
# 
# Caveats:
# The function *parse_10k_filing()* is a parser. You need to feed a SEC text link into it. There are many python and r packages to get a direct link to the fillings.
# 

import pandas as pd
import re
import unicodedata
from bs4 import BeautifulSoup as bs
import requests
import numpy as np
import sys

def parse_10k_filing(link, section):
    
    if section not in ["All", "Business", "Risk", "MDA"]:
        sys.exit()
    
    def get_text(link):
        page = requests.get(link)
        html = bs(page.content, "lxml")
        text = html.get_text()
        text = unicodedata.normalize("NFKD", text).encode('ascii', 'ignore').decode('utf8')
        text = text.split("\n")
        return(text)
    
    def extract_text(text, item, criteria):
            control = 0
            n = 0
            businessList = list()
            tableContent = 0
            for line in text:
                n += 1
                line = line.strip()
                if item.search(line) is not None:
                    if control == 0:
                        n = 0
                        control = 1
                        businessList.append(line)
                    elif control == 1:
                        businessList = list()
                        businessList.append(line)
                        control = 2         
                elif control == 1:
                    if (criteria.search(line) is not None):
                        # identifying if the first match occured in table of content
                        if n > 100:
                            if tableContent == 1:
                                pass
                            else:
                                break
                        if n < 30:
                            tableContent = 1

                    else:
                        businessList.append(line)

                elif control == 2:
                    if criteria.search(line) is not None:
                        break
                    else:
                        businessList.append(line)
            return(businessList)
        
    def extract_nameCIK(text):
        companyCik = re.compile("(CENTRAL INDEX KEY:)([\s\d]+)", re.IGNORECASE)
        companyName = re.compile("(COMPANY CONFORMED NAME:)(.+)", re.IGNORECASE)
        control = 0
        for line in text:
            if companyName.search(line) is not None:
                conm = companyName.search(line).group(2).strip()
            if companyCik.search(line) is not None:
                cik = companyCik.search(line).group(2).strip()
                control == 1
            if control == 1:
                break
        return(conm, cik)

    def get_business(text):
        item1 = re.compile("^item\s*1\.*\s*\\b", re.IGNORECASE)
        item1a = re.compile("^item\s*1a|^item\s*2", re.IGNORECASE)
        businessList = extract_text(text, item1, item1a)
        
        return(businessList)
    
    def get_businessRisk(text):
        item1a = re.compile("^item\s*1a\.*\s*\\b", re.IGNORECASE)
        item2 = re.compile("^item\s*2", re.IGNORECASE)
        riskList = extract_text(text, item1a, item2)
        
        return(riskList)
    
    def get_mda(text):
        item7 = re.compile("^item\s*7[\.\:]\s*", re.IGNORECASE)
        item7a = re.compile("^item\s*7a", re.IGNORECASE)
        item8 = re.compile("^item\s*8", re.IGNORECASE)
        is7a = any([item7a.search(line) for line in text])
        if is7a == True:
            mdaList = extract_text(text, item7, item7a)
        else:
            mdaList = extract_text(text, item7, item8)
                            
        return(mdaList)
    
    text = get_text(link)
    if section == "Business":
        businessDes = get_business(text)
        data = pd.DataFrame.from_dict([{"businessDescription": "\n".join(businessDes)}])
        
    if section == "Risk":
        riskDes = get_businessRisk(text)
        data = pd.DataFrame.from_dict([{"riskDescription": "\n".join(riskDes)}])
        
    if section == "MDA":
        mdaDes = get_mda(text)
        data = pd.DataFrame.from_dict([{"MDA": "\n".join(mdaDes)}])
        
    if  section == "All":
        businessDes = get_business(text)
        riskDes = get_businessRisk(text)
        mdaDes = get_mda(text)
        data = pd.DataFrame.from_dict([{"MDA": "\n".join(mdaDes),
                                        "riskDescription": "\n".join(riskDes),
                                       "businessDescription": "\n".join(businessDes)}])
    ids = extract_nameCIK(text)
    data["conm"] = ids[0]
    data["CIK"] = ids[1]
    data["edgar.link"] = link
        
        
    return(data)