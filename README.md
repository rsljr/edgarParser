# edgarParser #

> "EDGAR is the Electronic Data Gathering, Analysis, and Retrieval system used at the U.S. Securities and Exchange Commission (SEC). EDGAR is the primary system for submissions by companies and others who are required by law to file information with the SEC.  
>
> Containing millions of company and individual filings, EDGAR benefits investors, corporations, and the U.S. economy overall by increasing the efficiency, transparency, and fairness of the securities markets. The system processes about 3,000 filings per day, serves up 3,000 terabytes of data to the public annually, and accommodates 40,000 new filers per year on average." [About EDGAR](https://www.sec.gov/edgar/about)

EDGAR is a rich source of data. There are many packages to access and download company filings. However, because working with filings is not straightforward, parsers for SEC filings are few and far between packages.

As part of my research projects, I have written parsers to extract data from filings. I decided to share these parsers to democratize and ease the access to information that often is sold by thousands of dollars.

## 3, 4, and 5 form: Corporate insider data ##

The function [parse_345()](https://github.com/rsljr/python-edgar/blob/master/parse_345.py) parses forms 3, 4 and 5. It takes the form and return a dataframe in which each row is a transaction reported in the form (see caveats in the function description).  

## DEF 14A form: Executive compensation ##

The function [get_executive_compensation()](https://github.com/rsljr/python-edgar/blob/master/annotated%20notebooks/get_exectuvive_compensation.ipynb) parses the form DEF14A to extract the "summary compensation table". The function identifies the table and transforms it into a tidy dataframe. It works better with fillings submitted after 2004 (see caveats in the function description).  

## 8-K form: disclosure ##

The function [parse_8k_filing()](https://github.com/rsljr/python-edgar/blob/master/parse_8K.py) parses 8-K forms to extract disclosed items and their associated text.  You can check the page [Expansion of Form 8-K Items](https://www.sec.gov/rules/final/33-8400.htm) to see item meaning.  

## 13f form: Institutional Investors ##

The function [parse_13f_filing()](https://github.com/rsljr/python-edgar/blob/master/parse_13f.py) parses 13f forms to extract data regarding institutional investors and their portfolios.

## 10-K form: Business, Risk, MD&A ##

The function [parse_10k_filing()](https://github.com/rsljr/python-edgar/blob/master/parse_10K.py) parses 10-K forms to extract the sections: business description, risk, and management discussion and analysis.  

Visit [Accessing EDGAR Data](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm) to know more about EDGAR.  

[![HitCount](https://hits.dwyl.com/rsljr/https://githubcom/rsljr/edgarParser.svg?style=flat-square)](http://hits.dwyl.com/rsljr/https://githubcom/rsljr/edgarParser)
