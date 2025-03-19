from typing import List, Dict, Optional
import os

# Định nghĩa cấu trúc của một tài liệu liên quan
class RelevantDoc:
    def __init__(self, filename: str, file_path: Optional[str], content: Optional[str]):
        self.filename = filename
        self.file_path = file_path
        self.content = content

# Prefix đường dẫn tải file
PREFIX_DOWNLOAD_FILE = "documents/download"

def get_download_url( path: Optional[str]) -> str:
    """Hàm tạo đường dẫn tải file dựa trên host hiện tại"""
    base_url = os.getenv("RAG_APP_URL", "http://localhost:8000")
    return f"{base_url}/{PREFIX_DOWNLOAD_FILE}?file_path={path}" if path else "Unknown"

def normalize_relevant_docs_scripts(docs: List[RelevantDoc]) -> Dict[str, str]:
    """Hàm chuẩn hóa thông tin tài liệu nội bộ thành prompt"""
    if docs:
        content = "### 📂 Tài liệu nội bộ liên quan:\n\n" + "\n\n".join(
            f"""<div>- **Tên file:** [{doc.filename}]</div>
<div>- **Tải xuống:** <a class="internal-document" href="{get_download_url(doc.file_path)}" target="_blank">Tải xuống</a></div>
<div>- **Nội dung file:** {doc.content or "Bỏ qua"}</div>"""
            for doc in docs
        )
        content += "\n\nTrả ra kết quả đầy đủ danh sách file nội bộ gồm: tên, đường link tải liên quan, và nội dung chính ngắn gọn của file."
    else:
        content = "Không có tài liệu nội bộ liên quan, hãy trả lời dựa trên kiến thức chung."

    return {"role": "system", "content": content}

# 🧪 **Test thử**
if __name__ == "__main__":
    test_docs = [
        RelevantDoc("document1.pdf", "path/to/document1.pdf", "Nội dung tóm tắt của tài liệu 1."),
        RelevantDoc("document2.pdf", None, "Nội dung tóm tắt của tài liệu 2."),
    ]
    print(normalize_relevant_docs_scripts(test_docs))
