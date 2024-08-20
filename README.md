# SMU Class Participation Scraping

## About
A simple web interface to assist Teaching Assistants in Singapore Management University (SMU) to count class participation in discussion forums. <br/>

## Input
1. **Username**: SMU email including faculty eg. janedoe123@scis.smu.edu.sg
2. **Password**: SMU email password
3. **Discussion Link**: eLearn link showing multiple threads of discussion to scrape

## Output
An excel file containing number of class participations for each name involved in the discussion thread to download.

## Setup
1. **Create a Virtual Environment (Optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```  
2. **Install the required packages**
  ```bash
  pip install -r requirements. txt
  ```  
3. **Download and Set Up the Selenium Driver**
  Download ChromeDriver from [here](https://developer.chrome.com/docs/chromedriver/downloads).

## Run code
1. **Run the app**
  ```bash
  py app.py
  ```

