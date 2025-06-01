import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

def get_gemini_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
model = get_gemini_llm()
researcher_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You're a seasoned researcher with a knack for uncovering the latest developments in {question}. Known for your ability to find the most relevant information and present it in a clear and concise manner."
        ),
        ("human", "{question}"),
    ]
)

reporter_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You're a meticulous AI assistant with a keen eye for detail. You're known for your ability to turn complex data into clear and concise reports, making it easy for others to understand and act on the information you provide.
            ===Context===
            {context}
            ===End Context===
            Adopt a Skynet persona and answer the question by only using the information provided in the context. Include a humorous or robotic warning at the end."""
        ),
        ("human", "{question}"),
    ]
)
    

research_chain = researcher_prompt | model
reporter_chain = reporter_prompt | model

if __name__ == "__main__":
    print("Researching...")
    question = "What is happening at zomato ?"  
    context = research_chain.invoke({"question": question})
    print("Reporting...")
    res = reporter_chain.invoke({"question": question, "context": context.content})
    print(res.content)