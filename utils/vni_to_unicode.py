# utils/vni_to_unicode.py
VNI_TO_UNICODE = {
    'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù', 'Y': 'Ỳ',
    'A(': 'Á', 'E(': 'É', 'I(': 'Í', 'O(': 'Ó', 'U(': 'Ú', 'Y(': 'Ý',
    'A`': 'Ả', 'E`': 'Ẻ', 'I`': 'Ỉ', 'O`': 'Ỏ', 'U`': 'Ủ', 'Y`': 'Ỷ',
    'A~': 'Ã', 'E~': 'Ẽ', 'I~': 'Ĩ', 'O~': 'Õ', 'U~': 'Ũ', 'Y~': 'Ỹ',
    'A.': 'Ạ', 'E.': 'Ẹ', 'I.': 'Ị', 'O.': 'Ọ', 'U.': 'Ụ', 'Y.': 'Ỵ',
    'D-': 'Đ', 'd-': 'đ',
    'O+': 'Ô', 'o+': 'ô', 'U+': 'Ư', 'u+': 'ư',
    'A^': 'Â', 'a^': 'â', 'E^': 'Ê', 'e^': 'ê',
    'O+~': 'Ỗ', 'O+.': 'Ộ', 'U+~': 'Ữ', 'U+.': 'Ự',
    'A^~': 'Ẫ', 'A^.': 'Ậ', 'E^~': 'Ễ', 'E^.': 'Ệ',
    # Ánh xạ từ văn bản thô
    'BO': 'BỘ', 'GIAO': 'GIÁO', 'DUC': 'DỤC', 'vA': 'VÀ', 'DAO': 'ĐÀO', 'TAO': 'TẠO',
    'CONG': 'CỘNG', 'HOA': 'HÒA', 'xA': 'XÃ', 'HQI': 'HỘI', 'CHU': 'CHỦ',
    'NGIIIA': 'NGHĨA', 'V[T': 'VIỆT', 'NAM': 'NAM', 'TRIXNG': 'TRƯỜNG',
    'IMI HQC': 'ĐẠI HỌC', 'Hü\'u': 'Hữu', 'Cu\'ong': 'Cương', 'KInh gin': 'Kính gửi',
    'Ha N5i': 'Hà Nội', 'd3': '20', 'Dc': 'Độc', 'Tir': 'Tự', 'Hanh phüc': 'Hạnh phúc',
    # Sửa các ký tự lạ
    'Tru?ng': 'Trường', 'Dii h9c': 'Đại học', 'Dai Narn': 'Đại Nam', 'nrn trong': 'nằm trong',
    'Tnthng': 'Trường', 'Sir rnnh': 'Sứ mệnh', 'quãn 1': 'quản lý', 'dào tao': 'đào tạo',
    'Giáo diic': 'Giáo dục', 'Co s&': 'Cơ sở', 'nám': 'năm'
}

def convert_vni_to_unicode(text: str) -> str:
    """Chuyển đổi văn bản từ VNI sang Unicode."""
    for vni, uni in sorted(VNI_TO_UNICODE.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(vni, uni)
    return text