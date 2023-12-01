import streamlit as st
import pandas as pd
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import shutil

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('log-level=3')

# CHROMEDRIVER_PATH = 'chromedriver.exe'

def get_chromedriver_path():
    return shutil.which('chromedriver')


service = Service(executable_path=get_chromedriver_path())

driver = webdriver.Chrome(service=service, options=chrome_options)
def get_address(search_term):
    lat, lon = [], []
    try:
        print('HIT.......')
        driver.get("https://www.google.com/maps")
        time.sleep(3)

        driver.find_element(By.ID, "searchboxinput").send_keys(search_term)
        driver.find_element(By.ID, "searchbox-searchbutton").click()

        time.sleep(4)
        url = driver.current_url

        if '!3d' in url:
            print('--------------------------coor-----------------------------------')
            url = url.split('!3d')[1]
            url = url.split('!4d')
            lat.append(url[0])
            lon.append(url[1].split('!')[0])
     
            return lat[0], lon[0]
        else:
            time.sleep(0.25)
            f2 = driver.find_elements(By.XPATH, '//a')[1:]
            if f2:
                for k in f2:
                    if k.get_attribute('aria-label') is None:
                        continue

                    if search_term in k.get_attribute('aria-label'):
                        print('-------------------jump------------------------------')
                        k.click()
                        time.sleep(2.5)
                        url = driver.current_url
                        if '!3d' in url:
                            url = url.split('!3d')[1]
                            url = url.split('!4d')
                            lat.append(url[0])
                            lon.append(url[1].split('!')[0])
                     
                            break
                        else:
                            print('------------------------none--------------------------')
                            lat.append('0')
                            lon.append('0')
                 
                            break
                return lat[0], lon[0]
            else:
                print('------------------------fatal none--------------------------')
                lat.append('0')
                lon.append('0')

                time.sleep(0.6)
                return lat[0], lon[0]
    except Exception as e:
        # print("5 error")
        return e


def main():
    st.title("Address Finder")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Process Started wait till progress Bar Start !  Note: 0 is Mutliple Location Error" )

        latitudes, longitudes = [], []
        add = df['address'].to_list()

        # Create progress bar
        progress_bar = st.progress(0)
        progress_text = st.empty()
        processed_data = []

        for row in range(len(add)):
            try:
                
                result = get_address(add[row])
                print('HIT Over....')
                if type(result) == str:
                    st.error(f'{result}')
                    break

                latitudes.append(float(result[0]))
                longitudes.append(float(result[1]))

                # Update progress bar
                progress_value = (row + 1) / len(df['address'])
                progress_bar.progress(progress_value)
                progress_text.text(f"Progress: {int(progress_value * 100)}%")

                # Add to processed_data
                processed_data.append({'Address': add[row], 'latitudes': result[0], 'Longitudes': result[1]})

                # Display df2 on the side
                st.sidebar.title("Processed Data (df2)")
                st.sidebar.write(pd.DataFrame(processed_data))

            except Exception as e:
                st.error(f'Error processing row {row + 1}: {str(e)}')
                break

        # Create df2 DataFrame
        df2 = pd.DataFrame(processed_data)
        
        st.success("Processing completed!")
        st.write("Final Processed Data:")
        st.write(df2)


if __name__ == '__main__':
    main()
