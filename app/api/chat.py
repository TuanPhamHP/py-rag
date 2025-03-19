import openai
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv
from app.services.search import retrieve_context
from utils.normalize import normalize_relevant_docs_scripts

load_dotenv()

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RAG_KEYWORDS = ["tài liệu", "nội bộ", "hồ sơ", "báo cáo", "file", "tệp tin"]
async def should_use_rag(question: str) -> bool:
    """Kiểm tra xem câu hỏi có chứa từ khóa yêu cầu tìm kiếm dữ liệu nội bộ không"""
    return any(keyword in question.lower() for keyword in RAG_KEYWORDS)


async def generate(prompt, other_context):
    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[*other_context,{"role": "user", "content": prompt}],
        stream=True
    )

    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def generate_prompt(question: str, context: str = "") -> str:
    """Tạo prompt dựa trên câu hỏi & dữ liệu tìm được"""
    base_prompt = """
    Bạn là một chatbot AI. Trả lời câu hỏi của người dùng một cách chuyên nghiệp, rõ ràng.
    
    Nếu có dữ liệu nội bộ, hãy sử dụng nó. Nếu không, hãy trả lời dựa trên kiến thức của bạn.
    
    Nội dung câu trả lời sẽ luôn luôn sử dụng ngôn ngữ HTML5 và KHÔNG dùng Markdown.
    Các title sẽ dùng thẻ <h1></h1> -> <h6></h6>. Các danh sách dùng thẻ <ul><li></li></ul>.
    Nếu câu hỏi về so sánh tiêu chí thì nên dùng bảng biểu.
    """
    if context:
        base_prompt += f"\n\n**Dữ liệu nội bộ:** \n{context} \n Sử dụng dữ liệu nội bộ làm nguồn chính để hiển thị."

    return base_prompt + f"\n\n**Câu hỏi:** {question}"

@router.post("/")
async def chat_with_gpt(request: Request):
    data = await request.json()
    list_msg = data.get("listMsg", [])

    if not list_msg:
        return {"error": "listMsg is required"}
    other_context =list_msg[:-1] if len(list_msg) > 1 else []
    user_question = list_msg[-1]["content"]
    use_rag = await should_use_rag(user_question)

    retrieved_docs = await retrieve_context(user_question) if use_rag else []
    retrieved_context = normalize_relevant_docs_scripts(retrieved_docs)

    print(retrieved_context)
    prompt = generate_prompt(user_question, retrieved_context)
    return StreamingResponse(generate(prompt,other_context), media_type="text/event-stream")