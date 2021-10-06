#!/usr/bin/env python
# coding: utf-8

# # 10-K form
# ## Business, Risk, and MD&A
# The function *parse_10k_filing()* parses 10-K forms to extract the following sections: business description, business risk, and management discussioin and analysis. The function takes two arguments, a link and a number indicating the section, and returns a list with the requested sections. Current options are **0(All), 1(Business), 2(Risk), 4(MDA).**
# 
# Caveats:
# The function *parse_10k_filing()* is a parser. You need to feed a SEC text link into it. There are many python and r packages to get a direct link to the fillings.
# 

import re
import unicodedata
from bs4 import BeautifulSoup as bs
import requests

def parse_10k_filing(link, section):
    
    if section not in [0, 1, 2, 3]:
        print("Not a valid section")
        sys.exit()
    
    def get_text(link):
        page = requests.get(link, headers={'User-Agent': 'Mozilla'})
        html = bs(page.content, "lxml")
        text = html.get_text()
        text = unicodedata.normalize("NFKD", text).encode('ascii', 'ignore').decode('utf8')
        text = text.split("\n")
        text = " ".join(text)
        return(text)
    
    def extract_text(text, item_start, item_end):
        item_start = item_start
        item_end = item_end
        starts = [i.start() for i in item_start.finditer(text)]
        ends = [i.start() for i in item_end.finditer(text)]
        positions = list()
        for s in starts:
            control = 0
            for e in ends:
                if control == 0:
                    if s < e:
                        control = 1
                        positions.append([s,e])
        item_length = 0
        item_position = list()
        for p in positions:
            if (p[1]-p[0]) > item_length:
                item_length = p[1]-p[0]
                item_position = p

        item_text = text[item_position[0]:item_position[1]]

        return(item_text)

    text = get_text(link)
        
    if section == 1 or section == 0:
        try:
            item1_start = re.compile("item\s*[1][\.\;\:\-\_]*\s*\\b", re.IGNORECASE)
            item1_end = re.compile("item\s*1a[\.\;\:\-\_]\s*Risk|item\s*2[\.\,\;\:\-\_]\s*Prop", re.IGNORECASE)
            businessText = extract_text(text, item1_start, item1_end)
        except:
            businessText = "Something went wrong!"
        
    if section == 2 or section == 0:
        try:
            item1a_start = re.compile("(?<!,\s)item\s*1a[\.\;\:\-\_]\s*Risk", re.IGNORECASE)
            item1a_end = re.compile("item\s*2[\.\;\:\-\_]\s*Prop|item\s*[1][\.\;\:\-\_]*\s*\\b", re.IGNORECASE)
            riskText = extract_text(text, item1a_start, item1a_end)
        except:
            riskText = "Something went wrong!"
            
    if section == 3 or section == 0:
        try:
            item7_start = re.compile("item\s*[7][\.\;\:\-\_]*\s*\\bM", re.IGNORECASE)
            item7_end = re.compile("item\s*7a[\.\;\:\-\_]\sQuanti|item\s*8[\.\,\;\:\-\_]\s*", re.IGNORECASE)
            mdaText = extract_text(text, item7_start, item7_end)
        except:
            mdaText = "Something went wrong!"
    
    if section == 0:
        data = [businessText, riskText, mdaText]
    elif section == 1:
        data = [businessText]
    elif section == 2:
        data = [riskText]
    elif section == 3:
        data = [mdaText]
    return(data)