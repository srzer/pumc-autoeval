from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
import random
import re
import getpass

# ============================================================
# 【配置区】
# ============================================================

LOGIN_URL = "https://bjxh.drgeek.cn/queryBindLoginMobile.do"
BASE_URL  = "https://bjxh.drgeek.cn/updateEvaluateMobile.do"

SCORE_MIN = 7
SCORE_MAX = 9

# ============================================================
# 工具函数
# ============================================================

def wait(seconds=1):
    time.sleep(seconds)

def my_strategy():
    # 这里可以自定义打分策略，目前是随机分数
    return random_score()

def random_score():
    return random.randint(SCORE_MIN, SCORE_MAX)

# ============================================================
# 从列表页抓取所有未评价项的 URL
# ============================================================

def get_todo_urls(driver, list_url):
    print(">>> 加载待评价列表...")
    driver.get(list_url)
    wait(1.5)

    items = driver.find_elements(By.CSS_SELECTOR, "li.ui-li-static")
    urls = []

    for item in items:
        # 只处理「未评价」的项
        badges = item.find_elements(By.CSS_SELECTOR, ".lift-badge")
        if not any("未评价" in b.text for b in badges):
            continue

        onclick = item.get_attribute("onclick") or ""
        # 提取 updateEvaluate(...) 的参数
        m = re.search(r"updateEvaluate\((.+?)\)", onclick)
        if not m:
            continue

        # 参数是单引号包裹的字符串，去掉引号后按逗号分割
        raw = m.group(1)
        params = [p.strip().strip("'") for p in raw.split(",")]
        if len(params) < 5:
            continue

        evaluate_code, evaluate_year, evaluate_month, evaluate_person_id, evaluate_target_id = params[:5]
        evaluate_target_dept_id     = params[5] if len(params) > 5 else ""
        evl_target_dept_classify_id = params[6] if len(params) > 6 else ""
        resident_dept_data_id       = params[7] if len(params) > 7 else ""
        bill_data_id                = params[8] if len(params) > 8 else ""

        url = (
            f"{BASE_URL}"
            f"?evaluateCode={evaluate_code}"
            f"&evaluateYear={evaluate_year}"
            f"&evaluateMonth={evaluate_month}"
            f"&evaluatePersonId={evaluate_person_id}"
            f"&evaluateTargetId={evaluate_target_id}"
            f"&evaluateTargetDeptId={evaluate_target_dept_id}"
            f"&evlTargetDeptClassifyId={evl_target_dept_classify_id}"
            f"&residentDeptDataId={resident_dept_data_id}"
            f"&billDataId={bill_data_id}"
            f"&addEvaluateDate=undefined"
            f"&date={evaluate_year}-{evaluate_month.zfill(2)}"
            f"&code={evaluate_code}"
            f"&current_tab=todo"
        )

        # 尝试获取评价对象名称用于日志
        try:
            content = item.find_element(By.CSS_SELECTOR, ".list-view-content")
            label = content.text.replace("评价对象", "").strip()
        except Exception:
            label = evaluate_target_id

        urls.append((label, url))

    print(f">>> 共找到 {len(urls)} 个未评价项")
    return urls

# ============================================================
# 打分逻辑
# ============================================================

def fill_scores(driver):
    wait(1.5)  # 等待 AJAX 加载题目

    score_inputs = driver.find_elements(By.CSS_SELECTOR, "input.billInputItem.tol")
    if not score_inputs:
        print("  [!] 未找到评分题，跳过")
        return 0

    filled = 0
    for inp in score_inputs:
        label_text = inp.get_attribute("billdetailname") or inp.get_attribute("name")
        target = my_strategy()

        try:
            pointers = inp.find_elements(By.XPATH,
                "./following-sibling::div[contains(@class,'score-pointer')]")
            if not pointers:
                parent = inp.find_element(By.XPATH, "./parent::*")
                pointers = parent.find_elements(By.CSS_SELECTOR, ".score-pointer")

            best = None
            for p in pointers:
                if p.get_attribute("value") and int(p.get_attribute("value")) == target:
                    best = p
                    break
            if best is None:
                best = min(pointers, key=lambda p: abs(int(p.get_attribute("value") or 0) - target))

            driver.execute_script("arguments[0].click();", best)
            print(f"    [{label_text}] → {best.get_attribute('value')}")
            filled += 1
        except Exception as e:
            print(f"    [!] [{label_text}] 失败: {e}")

    return filled

def submit_form(driver):
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tj"))
        )
        driver.execute_script("arguments[0].click();", btn)
        wait(1.5)
        print("  >>> 提交成功")
        return True
    except Exception as e:
        print(f"  [!] 提交失败: {e}")
        return False

# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 50)
    print("  北京协和医院教学管理平台 - 自动评分脚本")
    print("=" * 50)
    print()

    date     = input("    请输入评价月份（格式 2026-04）：").strip()
    LIST_URL = f"https://bjxh.drgeek.cn/listMyEvaluateMobile.do?date={date}"
    account  = input("    请输入账号：").strip()
    password = getpass.getpass("    请输入密码（不回显）：")

    print(">>> 启动 Firefox...")

    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install())
    )

    try:
        driver.get(LOGIN_URL)
        wait(1.5)
        print(">>> Firefox 已打开登录页面。")
        driver.find_element(By.ID, "account").send_keys(account)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginBtn").click()
        wait(1.5)
        if "login" in driver.current_url.lower() or "queryBind" in driver.current_url:
            input("    检测到未登录成功，请手动完成登录后按回车继续...")
        print()

        # 抓取所有待评价项
        todo_urls = get_todo_urls(driver, LIST_URL)
        if not todo_urls:
            print("[!] 没有待评价项，退出。")
            return

        print()
        total = len(todo_urls)
        success = 0

        for i, (label, url) in enumerate(todo_urls, 1):
            print(f"[{i}/{total}] {label}")
            driver.get(url)

            count = fill_scores(driver)
            if count > 0:
                if submit_form(driver):
                    success += 1
            else:
                print("  [!] 未填写任何题目，跳过提交")

            wait(0.5)

        print()
        print(f">>> 全部完成！成功提交 {success}/{total} 份")

    finally:
        driver.quit()
        print(">>> 浏览器已关闭")


if __name__ == "__main__":
    main()