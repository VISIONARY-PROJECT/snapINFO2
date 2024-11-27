import random
import cv2
from paddleocr import PaddleOCR
import torch
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

def preprocess_image_intensity(image_path, output_path):
    # 이미지 읽기
    img = cv2.imread(image_path)

    # 이미지 흑백 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 히스토그램 평활화로 대비 향상
    enhanced = cv2.equalizeHist(gray)

    # 특정 밝기 범위 기반으로 마스크 생성
    lower, upper = 240, 255  # 밝기 범위 설정 (조정 가능)
    mask = cv2.inRange(enhanced, lower, upper)

    # 모폴로지 연산으로 노이즈 제거 및 텍스트 강조
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morphed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 최종 결과 이미지 저장
    cv2.imwrite(output_path, morphed)
    print(f"최종 결과 이미지가 저장되었습니다: {output_path}")

def text_out(path):   
    ocr = PaddleOCR(lang = 'korean') #다국어 사용시 multilingual
    result = ocr.ocr(path, cls = False)
    if result == None:
        return None

    texts = [item[1][0] for line in result for item in line]
    
    combined_text = " ".join(texts)
    
    print("Combined Text (Spell Checked):", combined_text)

    combined_text_file_path = "static/text/combined_text.txt"
    #with open(combined_text_file_path, "w", encoding="utf-8") as file:
        #file.write(combined_text)
    
    return combined_text

# koBART 모델과 토크나이저 불러오기
tokenizer = PreTrainedTokenizerFast.from_pretrained('./kobart_finetuned_model')
model = BartForConditionalGeneration.from_pretrained('./kobart_finetuned_model')
print("model download")

# 텍스트 파일 경로 (바탕화면에 위치한 txt 파일 경로를 설정)
def summary_text(text):
    # 텍스트 요약 처리
    raw_input_ids = tokenizer.encode(text)
    input_ids = [tokenizer.bos_token_id] + raw_input_ids + [tokenizer.eos_token_id]
    print("1단계")

    # 요약 생성 (최소 길이 설정)
    summary_ids = model.generate(
        torch.tensor([input_ids]),
        min_length=10,  # 요약의 최소 길이 (50 토큰)
        max_length=100,  # 요약의 최대 길이 (200 토큰)
        length_penalty=2.0,  # 길이에 대한 페널티 (길이를 조정할 때 유용)
        num_beams=4  # 빔 서치 사용 (더 나은 요약 생성 가능)
    )
    print("2단계")
    summary = tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)
    print("4단계")

    # 요약 결과 출력
    print("요약 결과:")
    print(summary)

    return summary

