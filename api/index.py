from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Cấu hình Gemini - Nhớ cài đặt GEMINI_API_KEY trong Environment Variables của Vercel
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def load_data():
    # Đường dẫn file data.csv nằm ở thư mục gốc
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', 'data.csv')
    try:
        return pd.read_csv(file_path)
    except Exception:
        return pd.DataFrame(columns=['Cum', 'De', 'Cau', 'De_Bai', 'Loi_Giai', 'Link_Anh'])

@app.route('/api/get_solution', methods=['GET'])
def get_solution():
    try:
        cum = request.args.get('cum')
        de = request.args.get('de')
        cau = request.args.get('cau')
        
        df = load_data()
        # Lọc dữ liệu theo Cụm, Đề, Câu
        result = df[(df['Cum'].astype(str) == str(cum)) & 
                    (df['De'].astype(str) == str(de)) & 
                    (df['Cau'] == cau)]
        
        if not result.empty:
            row = result.iloc[0]
            return jsonify({
                "de_bai": str(row['De_Bai']),
                "loi_giai": str(row['Loi_Giai']),
                "link_anh": str(row['Link_Anh']) if pd.notnull(row['Link_Anh']) else ""
            })
        return jsonify({"error": "Thầy chưa cập nhật dữ liệu câu này, đợi thầy tí nhé!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    data = request.json
    user_msg = data.get("message")
    de_bai = data.get("de_bai")
    loi_giai = data.get("loi_giai")
    
    # Định hình "nhân cách" AI thầy Duy Anh
    prompt = f"""
    Bạn là thầy Duy Anh, giáo viên Toán cực kỳ tâm lý và trẻ trung. 
    Học sinh đang xem bài toán sau:
    - Đề: {de_bai}
    - Lời giải của thầy: {loi_giai}
    
    Học sinh hỏi: "{user_msg}"
    
    Nhiệm vụ:
    1. Trả lời bằng giọng điệu gần gũi, dùng "thầy" và "em" hoặc "mấy đứa" (như đang nói chuyện với Tiến Đạt, Cát Anh, Tường Vy...).
    2. Dựa sát vào lời giải chuẩn của thầy để giải thích bước làm mà học sinh chưa rõ.
    3. Luôn sử dụng LaTeX (kẹp trong $ $) cho công thức toán.
    4. Nếu học sinh hỏi linh tinh, hãy khéo léo nhắc các em tập trung ôn thi Tuyển sinh 10.
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception:
        return jsonify({"reply": "AI của thầy đang 'giải lao' tí, em hỏi lại sau vài giây nhé!"})

if __name__ == '__main__':
    app.run(debug=True)