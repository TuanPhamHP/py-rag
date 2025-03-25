# utils/dump_raw.py
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal

def dump_raw_text(file_path: str) -> str:
    full_text = ""
    try:
        for page_layout in extract_pages(file_path):
            for element in page_layout:
                if isinstance(element, LTTextBoxHorizontal):
                    raw_text = element.get_text()
                    hex_text = ' '.join(f'{ord(c):02x}' for c in raw_text[:50])  # Dump 50 ký tự đầu
                    full_text += f"Raw: {raw_text[:50]}\nHex: {hex_text}\n"
                    break  # Chỉ lấy đoạn đầu tiên
        return full_text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Error"

if __name__ == "__main__":
    file_path = "uploaded_files/Cv 114_1.pdf"
    content = dump_raw_text(file_path)
    print(content)