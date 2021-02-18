#!/usr/bin/env python
# # 13f form
# 
# The function *parse_13f_filing() takes a link as argument and returns a dataframe with Institutional Investor (II) Name, II CIK, related institutional investors, and portfolio held by II.
# 
# Caveats: The function is a parser. You need to feed a SEC txt link into it. There are many python and r packages to get a direct link to the filings. Currently, it parses only files with xml code.

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import re
import xml.etree.ElementTree as ET

def parse_13f_filing(link):

    def clean_text_xml(file):
        pages = list()
        page = file.split("\\n")
        cleaned_page = ""
        counter = 0
        document_start = re.compile('\<XML\>')
        document_end = re.compile('\<\/XML\>')
        for line in page:
            if counter == 0:
                if document_start.search(line) is not None:
                    counter = counter + 1  
                else:
                    continue
            else:
                if document_end.search(line) is not None:
                    counter = 0
                    cleaned_page = re.sub("\s{1,20}", " ", cleaned_page)
                    pages.append(cleaned_page)
                    cleaned_page = ""
                else:
                    cleaned_page = cleaned_page + line + " "

        return(pages)
    
    def parse_address(address):
        addressList = list()
        if address.find("com:street1") is not None:
            addressList.append(["street1", address.find("com:street1").text.strip()])
        if address.find("com:street2") is not None:
            addressList.append(["street2", address.find("com:street2").text.strip()])
        if address.find("com:city") is not None:
            addressList.append(["city", address.find("com:city").text.strip()])
        if address.find("com:stateOrCountry") is not None:
            addressList.append(["stateOrCountry", address.find("com:stateOrCountry").text.strip()])
        if address.find("com:zipCode") is not None:
            addressList.append(["zipCode", address.find("com:zipCode").text.strip()])

        return(addressList)

    def parse_otherInvestors(investorList):
        investors = investorList.find_all("otherManager2")
        allInvestorInfo = list()
        for investor in investors:
            rowInvestorInfo = list()
            if investor.find("sequenceNumber") is not None:
                rowInvestorInfo.append(["numberOtherInvestorIncluded", investor.find("sequenceNumber").text.strip()])
            if investor.find("cik") is not None:
                rowInvestorInfo.append(["cikOtherInvestorIncluded", investor.find("cik").text.strip()])
            if investor.find("form13FFileNumber") is not None:
                rowInvestorInfo.append(["fileNumberOtherInvestorIncluded", investor.find("form13FFileNumber").text.strip()])
            if investor.find("name") is not None:
                rowInvestorInfo.append(["nameOtherInvestorIncluded", investor.find("name").text.strip()])
            allInvestorInfo.append(rowInvestorInfo)

        return(allInvestorInfo)

    def parse_otherManagerAppear(other):
        allManager = other.find_all("otherManager")
        managerList = list()    
        for row in allManager:
            managmentRow = list()
            if row.find("sequenceNumber") is not None:
                managmentRow.append(["sequenceNumberInvestorAppear", row.find("sequenceNumber").text.strip()])
            if row.find("cik") is not None:
                managmentRow.append(["cikInvestorAppear", row.find("cik").text.strip()])
            if row.find("form13FFileNumber") is not None:
                managmentRow.append(["fileNumberOtherInvestorAppear", row.find("form13FFileNumber").text.strip()])
            if row.find("name") is not None:
                managmentRow.append(["nameOtherInvestorAppear", row.find("name").text.strip()])
            managerList.append(managmentRow)

        return(managerList)

    def parse_institutionalInvestorInfo(page_list):
        dataDictionary = dict()
        document = bs(page_list[0], "xml")
        # get sections
        filer = document.find("filer")
        coverPage = document.find("coverPage")
        signatureBlock = document.find("signatureBlock")
        summaryPage = document.find("summaryPage")
        other = document.find("otherManagersInfo")
        # get data
        dataDictionary["cikManager"] = filer.find("cik").text
        address = parse_address(coverPage.find("address"))
        for line in address:
            dataDictionary[line[0]] = line[1] 

        dataDictionary["managerName"] = coverPage.find("name").text.strip()
        dataDictionary["reportCalendar"] = coverPage.find("reportCalendarOrQuarter").text.strip()
        dataDictionary["reportType"] = coverPage.find("reportType").text.strip()
        dataDictionary["form13FFileNumber"] = coverPage.find("form13FFileNumber").text.strip()
        dataDictionary["representantName"] = signatureBlock.find("name").text.strip()
        dataDictionary["representantTitle"] = signatureBlock.find("title").text.strip()
        if summaryPage is not None:
            dataDictionary["entryTotal"] = summaryPage.find("tableEntryTotal").text.strip()
            dataDictionary["valueTotal"] = summaryPage.find("tableValueTotal").text.strip()
            dataDictionary["otherIncludedManagersCount"] = summaryPage.find("otherIncludedManagersCount").text.strip()

            if summaryPage.find("isConfidentialOmitted") is not None:
                dataDictionary["isConfidentialOmitted"] = summaryPage.find("isConfidentialOmitted").text.strip()

            if summaryPage.find("otherIncludedManagersCount").text.strip() != "0":
                dataDictionary["otherIncludedManagersList"] = parse_otherInvestors(summaryPage.find("otherManagers2Info")) 

        if coverPage.find("isAmendment") is not None:
            if coverPage.find("isAmendment").text.strip() == "true":
                dataDictionary["isAmendment"] = coverPage.find("isAmendment").text.strip()
                dataDictionary["amendmentType"] = coverPage.find("amendmentType").text.strip()
            else:
                dataDictionary["isAmendment"] = coverPage.find("isAmendment").text.strip()

        if other is not None:
            dataDictionary["otherManagementApppear"] = parse_otherManagerAppear(other)

        # create dataframe   
        dt = pd.DataFrame.from_dict([dataDictionary])  
        return(dt, coverPage.find("reportType").text.strip())

    def parse_institutionalInvestorPortfolio(page_list, reportType):
        check = re.compile("13F HOLDINGS REPORT|13F COMBINATION REPORT")
        if check.search(reportType) is not None:
            document = bs(page_list[1], "xml")
            portfolio = list()
            # find all securities held
            securities = document.find_all('infoTable')
            for row in securities:
                portfolioDict = dict()
                portfolioDict["nameOfIssuer"] = row.find("nameOfIssuer").text.strip()
                portfolioDict["titleOfClass"] = row.find("titleOfClass").text.strip()   
                portfolioDict["cusip"] = row.find("cusip").text.strip()  
                portfolioDict["valueInThousands"] = row.find("value").text.strip()  
                portfolioDict["noVotingAuthoritySharesHeld"] = row.find("None").text.strip() 
                portfolioDict["sharedVotingAuthoritySharesHeld"] = row.find("Shared").text.strip() 
                portfolioDict["soleVotingAuthoritySharesHeld"] = row.find("Sole").text.strip() 
                portfolioDict["sharesHeldAtEndOfQtr"] = row.find("sshPrnamt").text.strip() 
                portfolioDict["securityType"] = row.find("sshPrnamtType").text.strip() 
                portfolioDict["investmentDiscretion"] = row.find("investmentDiscretion").text.strip()
                if row.find("otherManager") is not None:
                    portfolioDict["otherManager"] = row.find("otherManager").text.strip()
                if row.find("putCall") is not None:
                    portfolioDict["putCall"] = row.find("putCall").text.strip()

                portfolio.append(pd.DataFrame.from_dict([portfolioDict]))

            # concatanate secutires
            dtPortfolio = pd.concat(portfolio, sort = False, ignore_index = True)
        else:
            dtPortfolio = pd.DataFrame()

        return(dtPortfolio)



    linkRequest = str(requests.get(link).content)
    contentPages = clean_text_xml(linkRequest)
    if len(contentPages) > 0: 
        investorData = parse_institutionalInvestorInfo(contentPages)
        portfolioData = parse_institutionalInvestorPortfolio(contentPages, investorData[1])
        investorData[0]["edgar.link"] = link
        if len(portfolioData) > 0:
            portfolioData["edgar.link"] = link
            data = pd.merge(investorData[0], portfolioData)
        else:
            data = investorData[0]
    else:
        data = pd.DataFrame()
        data["edgar.link"] = link

    return(data)


