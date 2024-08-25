from gemini import Gemini
import os
import csv
import requests

# 環境変数を設定
os.environ["GEMINI_ULTRA"] = "1"

# Cookie情報のURL
cookie_url = 'https://*****/prompt/txt/cookies.txt'
questions_file_path = './questions.csv'  # CSVファイルへのパスに変更
required_cookies_keys = ["__Secure-1PSIDCC", "__Secure-1PSID", "__Secure-1PSIDTS"]

# 外部サーバーからCookie情報を取得する関数
def fetch_cookies(url, keys):
    response = requests.get(url)
    cookies = {key: None for key in keys}
    for line in response.text.split('\n'):
        line = line.strip()
        for key in keys:
            if line.startswith(key):
                _, value = line.split('=', 1)
                cookies[key] = value.strip()
                keys.remove(key)
                break
        if not keys:
            break
    return cookies

# CSV形式の質問ファイルから質問を読み込む
def load_questions(filepath):
    questions = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            questions.append(row[0])  # CSVの各行の第一カラムが質問として読み込まれる
    return questions

# 外部サーバーからCookieの値を取得
cookies = fetch_cookies(cookie_url, required_cookies_keys)

# Geminiクライアントの初期化
GeminiClient = Gemini(cookies=cookies)

questions = load_questions(questions_file_path)
responses = {}

# すべての質問に対する処理
for i, question_template in enumerate(questions, start=1):
    question = question_template.format(**{f'response{j}': responses.get(j, '') for j in range(1, i+1)})
    
    response = GeminiClient.generate_content(question)
    if hasattr(response, 'candidates') and response.candidates:
        rcid = response.candidates[0].rcid
        selected_response_text = response.candidates[0].text
        responses[i] = selected_response_text
    
        GeminiClient.rcid = rcid
    
        print(f"質問 {i}: {question}")
        print(f"回答 {i}: {selected_response_text}\n\n")
    else:
        print(f"質問 {i} に対する回答を取得できませんでした。")

# すべての質問に対する回答を取得した後、必要に応じて結果を保存または処理
with open('./responses.txt', 'w', encoding='utf-8') as file:
    for i, response in responses.items():
        file.write(f"質問 {i}: {questions[i-1]}\n")
        file.write(f"回答 {i}: {response}\n\n")
