import random
import cv2
from paddleocr import PaddleOCR

from hanspell import spell_checker
import re
import requests

def get_passport_key():
    """네이버에서 '네이버 맞춤법 검사기' 페이지에서 passportKey를 획득"""
    url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=네이버+맞춤법+검사기"
    res = requests.get(url)
    print(res.status_code)
    html_text = res.text
    match = re.search(r'passportKey=([^&"}]+)', html_text)
    if match:
        passport_key = match.group(1)
        return passport_key
    else:
        return None



def fix_spell_checker_py_code(file_path, passportKey):
    """획득한 passportKey를 spell_checker.py 파일에 적용"""
    pattern = r"'passportKey': '.*'"

    with open(file_path, 'r', encoding='utf-8') as input_file:
        content = input_file.read()
        modified_content = re.sub(pattern, f"'passportKey': '{passportKey}'", content)

    with open(file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(modified_content)

# 경로를 정확히 설정하세요
spell_checker_file_path = "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/hanspell/spell_checker.py"

passport_key = get_passport_key()
if passport_key:
    print(f"획득한 passportKey: {passport_key}")
    fix_spell_checker_py_code(spell_checker_file_path, passport_key)
    print("passportKey 수정 완료")
else:
    print("passportKey를 찾을 수 없습니다.")



def text_out(path):   
    ocr = PaddleOCR(lang = 'korean') #다국어 사용시 multilingual
    result = ocr.ocr(path, cls = False)
    

    texts = [item[1][0] for line in result for item in line]
    
    combined_text = " ".join(texts)
    
    spell_checked = spell_checker.check(combined_text)
    combined_text = spell_checked.checked
    print("Combined Text (Spell Checked):", combined_text)

    combined_text_file_path = "static/text/combined_text.txt"
    #with open(combined_text_file_path, "w", encoding="utf-8") as file:
        #file.write(combined_text)
    
    return combined_text 
