# utils/pdf_reader.py
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal
import unicodedata

# Bảng ánh xạ VNI -> Unicode (chuẩn hóa, không dựa vào đoán mò)
VNI_MAP = {
    'A\xC0': 'À', 'A\xC1': 'Á', 'A\xC2': 'Ả', 'A\xC3': 'Ã', 'A\xC4': 'Ạ',
    'E\xC0': 'È', 'E\xC1': 'É', 'E\xC2': 'Ẻ', 'E\xC3': 'Ẽ', 'E\xC4': 'Ẹ',
    'I\xC0': 'Ì', 'I\xC1': 'Í', 'I\xC2': 'Ỉ', 'I\xC3': 'Ĩ', 'I\xC4': 'Ị',
    'O\xC0': 'Ò', 'O\xC1': 'Ó', 'O\xC2': 'Ỏ', 'O\xC3': 'Õ', 'O\xC4': 'Ọ',
    'U\xC0': 'Ù', 'U\xC1': 'Ú', 'U\xC2': 'Ủ', 'U\xC3': 'Ũ', 'U\xC4': 'Ụ',
    'Y\xC0': 'Ỳ', 'Y\xC1': 'Ý', 'Y\xC2': 'Ỷ', 'Y\xC3': 'Ỹ', 'Y\xC4': 'Ỵ',
    'D\xD0': 'Đ', 'd\xD0': 'đ',
    'O\xD5': 'Ô', 'o\xD5': 'ô', 'U\xD6': 'Ư', 'u\xD6': 'ư',
    'A\xD2': 'Â', 'a\xD2': 'â', 'E\xD3': 'Ê', 'e\xD3': 'ê',
}

def convert_vni_to_unicode(text: str) -> str:
    """Chuyển đổi văn bản VNI sang Unicode dựa trên ký tự gốc."""
    result = ""
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in VNI_MAP:
            result += VNI_MAP[text[i:i+2]]
            i += 2
        else:
            result += text[i]
            i += 1
    return result

def read_pdf(file_path: str) -> str:
    """Trích xuất văn bản từ PDF và chuyển đổi VNI sang Unicode."""
    full_text = ""
    try:
        # Trích xuất từng trang
        for page_layout in extract_pages(file_path):
            for element in page_layout:
                if isinstance(element, LTTextBoxHorizontal):
                    raw_text = element.get_text()
                    # Chuyển đổi VNI sang Unicode
                    unicode_text = convert_vni_to_unicode(raw_text)
                    full_text += unicode_text + "\n"
        return full_text.strip()
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return "Error: Could not extract text"

if __name__ == "__main__":
    file_path = "uploaded_files/Cv 114_1.pdf"
    content = read_pdf(file_path)
    print(f"Content preview: {content[:500]}...")