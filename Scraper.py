# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 23:33:36 2023

@author: apsin
"""

import zipfile
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

# Define the URL where the zip files are located
base_url= 'https://www.sec.gov'

url = 'https://www.sec.gov/dera/data/crowdfunding-offerings-data-sets' #dataset url

# Send an HTTP GET request to the URL
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to zip files on the webpage
zip_links = [base_url + a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.zip')]

# Initialize an empty list to store dataframes

def zipFileToDf(zip_links, fileName):
    dataframes = []
    
    for zip_link in zip_links:
        # Send an HTTP GET request to download the zip file
        response = requests.get(zip_link)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the zip file content
            zip_data = BytesIO(response.content)
            zip_file = zipfile.ZipFile(zip_data, 'r')
            
            # Define the folder inside the zip file where the date file, with fileName is located
            
            folder_name = zip_link[-13:-4].replace('q','Q') #the folder name is part of link string i.e. same as zip file name but with uppercase Q

            # Specify the file path within the zip file
            file_path_in_zip = f'{folder_name}/{fileName}'
            
            # Check if 'FORM_C_DISCLOSURE.tsv' exists in the specified folder inside the zip file
            if file_path_in_zip in zip_file.namelist():
                # Extract 'FORM_C_DISCLOSURE.tsv' from the specified folder inside the zip file
                tsv_data = zip_file.open(file_path_in_zip)
                
                # Read the TSV data into a Pandas dataframe
                df = pd.read_csv(tsv_data, sep='\t')
                
                # Append the dataframe to the list
                dataframes.append(df)
                
                # Close the TSV file
                tsv_data.close()
            else:
                print(f"'{fileName} not found in {zip_link}/{folder_name}")
            
            # Close the zip file
            zip_file.close()
        else:
            print(f"Failed to download {zip_link}")
    
    # Combine all dataframes into one and return it
    return pd.concat(dataframes, ignore_index=True)

df_disclosure= zipFileToDf(zip_links, 'FORM_C_DISCLOSURE.tsv')
#df_CoIssuer= zipFileToDf(zip_links, 'FORM_C_COISSUER_INFORMATION.tsv')
df_Issuer= zipFileToDf(zip_links, 'FORM_C_ISSUER_INFORMATION.tsv')
df_Submission= zipFileToDf(zip_links, 'FORM_C_SUBMISSION.tsv')

df_merged= pd.merge(df_disclosure,df_Issuer, on= 'ACCESSION_NUMBER', how='left')
df_merged= pd.merge(df_merged,df_Submission, on= 'ACCESSION_NUMBER', how='left')

columns_to_drop= ['STREET1', 'STREET2', 'COMMISSIONCIK', 'COMMISSIONFILENUMBER', 'CRDNUMBER', 'PERIOD']
df_merged.drop(columns= columns_to_drop, axis=1, inplace=True)

#For renaming columns
column_mapping = {
    'ACCESSION_NUMBER': 'accessionNumber',
    'COMPENSATIONAMOUNT': 'compensationAmount',
    'FINANCIALINTEREST': 'financialInterest',
    'SECURITYOFFEREDTYPE': 'securityOfferedType',
    'SECURITYOFFEREDOTHERDESC': 'securityOfferedOtherDesc',
    'NOOFSECURITYOFFERED': 'noOfSecurityOffered',
    'PRICE': 'price',
    'PRICEDETERMINATIONMETHOD': 'priceDeterminationMethod',
    'OFFERINGAMOUNT': 'offeringAmount',
    'OVERSUBSCRIPTIONACCEPTED': 'oversubscriptionAccepted',
    'OVERSUBSCRIPTIONALLOCATIONTYPE': 'oversubscriptionAllocationType',
    'DESCOVERSUBSCRIPTION': 'oversubscriptionDesc',
    'MAXIMUMOFFERINGAMOUNT': 'maximumOfferingAmount',
    'DEADLINEDATE': 'campaignDeadlineDate',
    'CURRENTEMPLOYEES': 'currentEmployees',
    'TOTALASSETMOSTRECENTFISCALYEAR': 'totalAssetMostRecentFiscalYear',
    'TOTALASSETPRIORFISCALYEAR': 'totalAssetPriorFiscalYear',
    'CASHEQUIMOSTRECENTFISCALYEAR': 'cashEqMostRecentFiscalYear',
    'CASHEQUIPRIORFISCALYEAR': 'cashEqPriorFiscalYear',
    'ACTRECEIVEDRECENTFISCALYEAR': 'accountsReceivedRecentFiscalYear',
    'ACTRECEIVEDPRIORFISCALYEAR': 'accountsReceivedPriorFiscalYear',
    'SHORTTERMDEBTMRECENTFISCALYEAR': 'shortTermDebtMRecentFiscalYear',
    'SHORTTERMDEBTPRIORFISCALYEAR': 'shortTermDebtPriorFiscalYear',
    'LONGTERMDEBTRECENTFISCALYEAR': 'longTermDebtRecentFiscalYear',
    'LONGTERMDEBTPRIORFISCALYEAR': 'longTermDebtPriorFiscalYear',
    'REVENUEMOSTRECENTFISCALYEAR': 'revenueMostRecentFiscalYear',
    'REVENUEPRIORFISCALYEAR': 'revenuePriorFiscalYear',
    'COSTGOODSSOLDRECENTFISCALYEAR': 'costGoodsSoldRecentFiscalYear',
    'COSTGOODSSOLDPRIORFISCALYEAR': 'costGoodsSoldPriorFiscalYear',
    'TAXPAIDMOSTRECENTFISCALYEAR': 'taxPaidMostRecentFiscalYear',
    'TAXPAIDPRIORFISCALYEAR': 'taxPaidPriorFiscalYear',
    'NETINCOMEMOSTRECENTFISCALYEAR': 'netIncomeMostRecentFiscalYear',
    'NETINCOMEPRIORFISCALYEAR': 'netIncomePriorFiscalYear',
    'ISAMENDMENT': 'isAmendment',
    'PROGRESSUPDATE': 'progressUpdate',
    'NATUREOFAMENDMENT': 'natureOfAmendment',
    'NAMEOFISSUER': 'issuerName',
    'LEGALSTATUSFORM': 'legalStatusForm',
    'LEGALSTATUSOTHERDESC': 'legalStatusOtherDesc',
    'JURISDICTIONORGANIZATION': 'jurisdictionOrganization',
    'DATEINCORPORATION': 'dateIncorporation',
    'CITY': 'city',
    'STATEORCOUNTRY': 'stateOrCountry',
    'ZIPCODE': 'zipCode',
    'ISSUERWEBSITE': 'issuerWebsite',
    'COMPANYNAME': 'IntermediaryName',
    'ISCOISSUER': 'isCoIssuer',
    'SUBMISSION_TYPE': 'submissionType',
    'FILING_DATE': 'filingDate',
    'CIK': 'issuerCIK',
    'FILE_NUMBER': 'fileNumber'
}

df_merged.rename(columns=column_mapping, inplace=True)

df_merged.to_excel('scrapedCrowdOfferingsData.xlsx')  


  
