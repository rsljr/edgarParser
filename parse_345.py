#!/usr/bin/env python
# coding: utf-8

# ## Corporate insider trading data ##
# This notebook contains a few functions to parse forms 3, 4 and 5 (see the [SEC FAQ](https://www.sec.gov/fast-answers/answersform345htm.html) for details about these forms). The function *parse_345()* takes the form and return a dataframe in which each row is a transaction reported in the form. The text from the request serves as input for the *parse_345()*. The input is cleaned and later passes through the function that extracts the data from the form.
# 
# **Caveats:**  
# Current function covers only files with xml. Function *parse_345()* is a parser. You need to feed a SEC txt link into it. There are many python and r packages to get a direct link to the filings.

# required
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import re
import numpy as np

def parse_345(link):
    
    def clean_text_xml(file):
        page = file.split("\\n")
        cleanedPage = ""
        counter = 0
        documentStart = re.compile('\<XML\>')
        documentEnd = re.compile('\<\/XML\>')
        for line in page:
            if counter == 0:
                if documentStart.search(line) is not None:
                    counter = counter + 1  
                else:
                    continue
            else:
                if documentEnd.search(line) is not None:
                    counter = 0
                else:
                    cleanedPage = cleanedPage + line + " "
                    
        cleanedPage = bs(cleanedPage, "xml")
        return(cleanedPage)
    
    def get_identity(text):
        
        counter = 0
        infoList = list()
        
        issuer = text.find("issuer")
        if issuer.find("issuerCik") is not None:
            infoList.append(["firmCIK", issuer.find("issuerCik").text.strip()])
        if issuer.find("issuerName") is not None:
            infoList.append(["firmName", issuer.find("issuerName").text.strip()])
        if issuer.find("issuerTradingSymbol") is not None:
            infoList.append(["firmTicker", issuer.find("issuerTradingSymbol").text.strip()])
        
        owner = text.find("reportingOwnerId")
        if owner.find("rptOwnerCik") is not None:
            infoList.append(["executiveCIK", owner.find("rptOwnerCik").text.strip()])
        if owner.find("rptOwnerName") is not None:
            infoList.append(["executiveName", owner.find("rptOwnerName").text.strip()])
        
        address = text.find("reportingOwnerAddress")
        if address.find("rptOwnerStreet1") is not None:
            infoList.append(["ownerAddress1", address.find("rptOwnerStreet1").text.strip()])
        if address.find("rptOwnerStreet2") is not None:
            infoList.append(["ownerAddress2", address.find("rptOwnerStreet2").text.strip()])
        if address.find("rptOwnerCity") is not None:
            infoList.append(["ownerCity", address.find("rptOwnerCity").text.strip()])
        if address.find("rptOwnerState") is not None:
            infoList.append(["ownerState", address.find("rptOwnerState").text.strip()])
        if address.find("rptOwnerZipCode") is not None:
            infoList.append(["ownerZipCode", address.find("rptOwnerZipCode").text.strip()])

        relationship = text.find("reportingOwnerRelationship")
        if relationship.find("isDirector") is not None:
            infoList.append(["isDirector", relationship.find("isDirector").text.strip()])
        if relationship.find("isOfficer") is not None:
            infoList.append(["isOfficer", relationship.find("isOfficer").text.strip()])
        if relationship.find("isTenPercentOwner") is not None:
            infoList.append(["isTenPercentOwner", relationship.find("isTenPercentOwner").text.strip()])
        if relationship.find("isOther") is not None:
            infoList.append(["isOther", relationship.find("isOther").text.strip()])
        if relationship.find("officerTitle") is not None:
            infoList.append(["officerTitle", relationship.find("officerTitle").text.strip()])
        if relationship.find("otherText") is not None:
            infoList.append(["otherText", relationship.find("otherText").text.strip()])
        
        if text.find("documentType") is not None:
            infoList.append(["documentType", text.find("documentType").text.strip()])   
        if text.find("periodOfReport") is not None:
            infoList.append(["periodOfReport", text.find("periodOfReport").text.strip()])
        if text.find("notSubjectToSection16") is not None:
            infoList.append(["notSubjectToSection16", text.find("notSubjectToSection16").text.strip()])         
        if text.find("dateOfOriginalSubmission") is not None:
            infoList.append(["dateOfOriginalSubmission", text.find("dateOfOriginalSubmission").text.strip()])
            
        
        dataDict = dict()
        for item in infoList:
            dataDict[item[0]] = item[1]
            
        data = pd.DataFrame.from_dict([dataDict])      
        return(data)
    
    def get_transaction_row(transaction):
        infoTransaction = list()
        
        if transaction.find("securityTitle") is not None:
            infoTransaction.append(["securityTitle", transaction.find("securityTitle").text.strip()])
        if transaction.find("transactionDate") is not None:
            infoTransaction.append(["transactionDate", transaction.find("transactionDate").text.strip()])
        if transaction.find("conversionOrExercisePrice") is not None:
            infoTransaction.append(["conversionOrExercisePrice", transaction.find("conversionOrExercisePrice").text.strip()])
        
        if transaction.find("transactionCoding") is not None:    
            trnsctnCoding = transaction.find("transactionCoding")
            if trnsctnCoding.find("transactionFormType") is not None:
                infoTransaction.append(["transactionFormType", trnsctnCoding.find("transactionFormType").text.strip()])
            if trnsctnCoding.find("transactionCode") is not None:
                infoTransaction.append(["transactionCode", trnsctnCoding.find("transactionCode").text.strip()])
            if trnsctnCoding.find("equitySwapInvolved") is not None:
                infoTransaction.append(["equitySwapInvolved", trnsctnCoding.find("equitySwapInvolved").text.strip()])  
        
        if transaction.find("transactionAmounts") is not None:
            trnsctnAmounts = transaction.find("transactionAmounts")
            if trnsctnAmounts.find("transactionShares") is not None:
                infoTransaction.append(["transactionShares", trnsctnAmounts.find("transactionShares").text.strip()])
            if trnsctnAmounts.find("transactionPricePerShare") is not None:
                infoTransaction.append(["transactionPricePerShare", trnsctnAmounts.find("transactionPricePerShare").text.strip()])
            if trnsctnAmounts.find("transactionAcquiredDisposedCode") is not None:
                infoTransaction.append(["transactionAcquiredDisposedCode", trnsctnAmounts.find("transactionAcquiredDisposedCode").text.strip()])
        
        if transaction.find("exerciseDate") is not None:
            infoTransaction.append(["exerciseDate", transaction.find("exerciseDate").text.strip()])
        if transaction.find("expirationDate") is not None:
            infoTransaction.append(["expirationDate", transaction.find("expirationDate").text.strip()])

        if transaction.find("underlyingSecurity") is not None:
            trnsctnUnderlying = transaction.find("underlyingSecurity")
            if trnsctnUnderlying.find("underlyingSecurityTitle") is not None:
                infoTransaction.append(["underlyingSecurityTitle", trnsctnUnderlying.find("underlyingSecurityTitle").text.strip()])
            if trnsctnUnderlying.find("underlyingSecurityShares") is not None:
                infoTransaction.append(["underlyingSecurityShares", trnsctnUnderlying.find("underlyingSecurityShares").text.strip()])

        if transaction.find("sharesOwnedFollowingTransaction") is not None:
            infoTransaction.append(["sharesOwnedFollowingTransaction", transaction.find("sharesOwnedFollowingTransaction").text.strip()])
        if transaction.find("directOrIndirectOwnership") is not None:
            infoTransaction.append(["directOrIndirectOwnership", transaction.find("directOrIndirectOwnership").text.strip()])
        if transaction.find("natureOfOwnership") is not None:
            infoTransaction.append(["natureOfOwnership", transaction.find("natureOfOwnership").text.strip()])
              
        return(infoTransaction)
    
    def get_non_derivative_table(text):
        tableNonDerivative = text.find_all(re.compile(r"nonDerivativeTransaction|nonDerivativeHolding"))
        infoNonTable = list()
        for transaction in tableNonDerivative:
            transactionDict = dict()
            infoTransaction = get_transaction_row(transaction)
               
            for item in infoTransaction:
                transactionDict[item[0]] = item[1]
            
            transactionDict["table"] = "I: Non-Derivative Securities"
            infoNonTable.append(pd.DataFrame.from_dict([transactionDict]))
        if len(infoNonTable) > 0:
            data = pd.concat(infoNonTable, sort = False, ignore_index = True)
        else:
            data = pd.DataFrame()
        return(data)
    
    def get_derivative_table(text):
        tableDerivative = text.find_all(re.compile(r"derivativeTransaction|derivativeHolding"))
        infoTable = list()
        for transaction in tableDerivative:
            infoTransaction = get_transaction_row(transaction)
            transactionDict = dict()
            
            for item in infoTransaction:
                transactionDict[item[0]] = item[1]
            
            transactionDict["table"] = "II: Derivative Securities"
            infoTable.append(pd.DataFrame.from_dict([transactionDict]))
        
        
        if len(infoTable) > 0:
            data = pd.concat(infoTable, sort = False, ignore_index = True)
        else:
            data = pd.DataFrame()
        
        return(data)


    linkRequest = str(requests.get(link, headers={'User-Agent': 'Mozilla'}).content) 
    text = clean_text_xml(linkRequest)
    identityData = get_identity(text)
    dataNonTable = get_non_derivative_table(text)
    dataDerivativeTable = get_derivative_table(text)
    identityData["edgar.link"] = link
    dataNonTable["edgar.link"] = link
    dataDerivativeTable["edgar.link"] = link
    
    data  = pd.concat([dataNonTable,dataDerivativeTable], sort = False, ignore_index = True)
    data = pd.merge(data, identityData, on = "edgar.link")
    
    if text.find("footnotes") is not None:
        data["footnotes"] = text.find("footnotes").text

    return(data)