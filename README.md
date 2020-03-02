# python-edgar #

> "EDGAR is the Electronic Data Gathering, Analysis, and Retrieval system used at the U.S. Securities and Exchange Commission (SEC). EDGAR is the primary system for submissions by companies and others who are required by law to file information with the SEC.  
>
> Containing millions of company and individual filings, EDGAR benefits investors, corporations, and the U.S. economy overall by increasing the efficiency, transparency, and fairness of the securities markets. The system processes about 3,000 filings per day, serves up 3,000 terabytes of data to the public annually, and accommodates 40,000 new filers per year on average." [About EDGAR](https://www.sec.gov/edgar/about)

EDGAR is a rich source of data, but working with it is not straightforward. Although there are many packages to access and download company fillings, parsing these fillings is a different story.  
  
As part of my research projects, I coded some scripts to parse fillings and extract the information I needed. I am making some of my scripts available to facilitate or inspire my fellow researchers facing similar problems.

**Corporate insider data**  

The function [extract_insider_data()](https://github.com/rsljr/python-edgar/blob/master/insider_trading.ipynb) parses forms 3, 4 and 5. It takes the form and return a dataframe in which each row is a transaction reported in the form (see caveats in the function description).  
