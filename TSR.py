from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from apscheduler.schedulers.blocking import BlockingScheduler

from bs4 import BeautifulSoup
from os import path
from PIL import Image
import urllib.request
import urllib.parse
import os


def start_driver(user_number, user_id, user_pw, article_num):
    print("출석체크를 시작합니다...")

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    print("EBS에 로그인하고 있습니다....")
    driver.get("https://hoc22.ebssw.kr/sso/loginView.do?loginType=onlineClass&hmpgId=sunrin206")

    input_login_id = driver.find_element(By.ID, "j_username")
    input_login_pw = driver.find_element(By.ID, "j_password")
    btn_login_submit = driver.find_element(By.CLASS_NAME, "img_type")

    input_login_id.send_keys(user_id)
    input_login_pw.send_keys(user_pw)
    btn_login_submit.click()

    WebDriverWait(driver, 10).until(EC.title_is("EBS 온라인 클래스"))

    print("학급 게시판에 접속하고 있습니다...")
    driver.refresh()
    driver.get("https://hoc22.ebssw.kr/sunrin206/hmpg/hmpgBbsDetailView.do?menuSn=407600&bbsId=BBSID_000395982"
               "&bbscttSn="+article_num)

    print("댓글을 작성하고 있습니다...")
    input_board_comment = driver.find_element(By.NAME, "cmmntsCn")
    btn_board_submit = driver.find_element(By.CLASS_NAME, "submit")

    input_board_comment.send_keys(user_number + "번 학습시작")
    btn_board_submit.click()

    alert_board_comment = driver.switch_to.alert
    alert_board_comment.accept()

    if path.exists("screenshot.png"):
        os.remove("screenshot.png")

    driver.save_screenshot("screenshot.png")
    Image.open("screenshot.png").show()

    driver.quit()

    print("\n출석이 완료되었습니다!")
    os._exit(0)


print("프로그램 실행 준비중...")
board_url = "https://hoc22.ebssw.kr/sunrin206/hmpg/hmpgBbsListView.do?menuSn=407600&bbsId=BBSID_000395982"
with urllib.request.urlopen(board_url) as response:
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all("a", {"class": "class_nm_ellipsis"})

print("🚀 206 EBS Automation Tool 0.1 by 정찬효 🚀\n")

if path.exists("user_info.txt"):
    with open('user_info.txt', 'r') as f:
        user_info = f.read()
        student_number = user_info.split(",")[0]
        student_id = user_info.split(",")[1]
        student_pw = user_info.split(",")[2]
        f.close()
    print("유저 정보를 불러왔습니다. ("+student_id+")")
else:
    print("학번을 입력해주세요. (예시: 20625)")
    student_number = input()[-2:]
    print("EBS ID를 입력해주세요.")
    student_id = input()
    print("EBS 패스워드를 입력해주세요.")
    student_pw = input()
    with open('user_info.txt', 'w') as f:
        f.write(student_number + "," + student_id + "," + student_pw)
    print("유저 정보가 저장되었으며, user_info.txt 에서 수정할 수 있습니다.")

print("출석할 게시물의 번호를 입력해 주세요.")
for i, article in enumerate(articles, start=1):
    print(str(i)+". "+article.text.strip())
article_number = articles[int(input())-1].get("href").split("\'")[1]

print("지금 바로 출석할까요? N을 입력하면 출석 시간을 예약할 수 있습니다. (Y,N)")
now_or_later = input()
if now_or_later == 'y' or now_or_later == 'Y':
    start_driver(student_number, student_id, student_pw, article_number)
else:
    print("예약 시간을 입력해 주세요. (예시: 2020-04-16 06:00:00)")
    date_input = input()
    print(date_input + "에 출석이 진행됩니다.")
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: start_driver(student_number, student_id, student_pw), "date", run_date=date_input)
    scheduler.start()
