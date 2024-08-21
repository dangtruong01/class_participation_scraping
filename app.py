from flask import Flask, render_template, request, redirect, url_for, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import tempfile
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the input values from the form
        username = request.form['username']
        password = request.form['password']
        base_url = request.form['discussion_link']
        
        # Call the scraping function with these inputs
        excel_file_path = scrape_data(username, password, base_url)
        
        return redirect(url_for('success', filename=excel_file_path))
    
    return render_template('index.html')

@app.route('/success')
def success():
    filename = request.args.get('filename')
    return render_template('success.html', filename=filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

def scrape_data(username_input, password_input, base_url):
    # Setup the webdriver (Chrome in this example)
    driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH

    # Navigate to the login page
    driver.get("https://login2.smu.edu.sg/adfs/ls/?client-request-id=bf479c5d-1630-48b4-ad00-f7e67bcb01f4&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=LoginOptions%3D3%26estsredirect%3d2%26estsrequest%3drQQIARAA42Kw8ssoKSkottLXT0kxtLQws7DQNTFPStM1MUgx0k20TEnUNTE1TDFNNjOwMEi11CtJzUvMKynWSyrKTM8oKS5ITE7VS87P1S9OzM3xyU_PzCsS4hKIneO-30Bsi8dahu_Pqk8zflnFaAmzJDUnNbEoT684t1QvNaVUrzhdP8UoRz-nQD-xtCRDPwdkAsIsPaDcIUYdEL8otbA0tbgk3tAsNS3JwMzE2Mzc1CTZwiTROMXM0jDV1DA1Nc3MONXsAiPjC0bGW0yswUBNRrOYOcHmZ-Tnpm5iVkm2tEg0t0xO1DVNtAT6y9zSUDfRyMRYN83ALDEtxczcxMwk5RGzbEZKSVFpfl66npGBkZFDcXJmMZJ7L7DwvGLhMWC24uDgEmCQYFBg-MHCuIgV6Gsj9aUpTJq1_jNWtNlOm3KD4RSrfoVXSHpksGGAp4W2RZJfVpS5l2l-imGReVRgkkmVt5t7iUlVUlBGpKNxkomtpZXhBDbeU2wMH9gYO9gZZrEz7OIkP9gO8DL84Pv6dM6bl-0b3nm84tfJzTcs88kLTEzMzcoOMA1NSqyMSPew9I3KMEhxCfKLLPc1MKvwLPVOK7TMtt0gwPBAgAEA0&cbcxt=")

    # Wait for the username field to be visible and enter the username
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "userNameInput"))
    )
    username.send_keys(username_input)

    # Enter the password
    password = driver.find_element(By.ID, "passwordInput")
    password.send_keys(password_input)

    # Submit the form
    password.send_keys(Keys.RETURN)

    # Wait for login to complete and navigate to the desired page
    time.sleep(5)  # Adjust this as needed
    driver.get(base_url)

    # Set up necessary variables
    index = 0 #to loop through the links
    classpart_dict = {} #Dictionary to store classpart, key is name, value is number of classpart

    def extract_classpart(element):
        html = element.get_attribute('innerHTML')
        name = html.split("_")[0].strip()
        if name in classpart_dict.keys():
            classpart_dict[name] += 1
        else:
            classpart_dict[name] = 1

    while True:
        # Wait for the links to be present
        links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.d2l-linkheading-link.d2l-clickable.d2l-link"))
        )

        if not links or index >= len(links):
            break

        # Extract and access to the thread
        link = links[index]
        href = link.get_attribute('href')
        print(href)
        driver.get(href)

        # Extract the name posting the thread
        poster_div = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.d2l-thread-statuses-container"))
        )

        child_elements = poster_div.find_elements(By.CSS_SELECTOR, "div.d2l-textblock.d2l-textblock-secondary.vui-emphasis")
        if child_elements:
            first_element = child_elements[0]
            extract_classpart(first_element)
        
        # Extract the names commenting on the thread
        comment_div = WebDriverWait(driver,10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div.d2l-inline.d2l-discussions-post-header"))
        )

        for comment in comment_div:
            headline = comment.find_element(By.CSS_SELECTOR,":first-child")
            extract_classpart(headline)

        # Navigate back
        driver.get(base_url)
        index += 1 # Move to nextthread


    # Prepare output
    print(classpart_dict)
    df = pd.DataFrame.from_dict(classpart_dict, orient='index', columns=['Participation Count'])
    # Create a temporary file to store the Excel file
    temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    
    # Save the DataFrame to the Excel file
    df.to_excel(temp_file.name, index=True)

    return temp_file.name

if __name__ == '__main__':
    app.run(debug=True)
