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



  
