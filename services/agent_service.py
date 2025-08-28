# AI ve LangChain kütüphanelerini import et
from langchain_openai import ChatOpenAI                    # OpenAI modelleri için
from langchain.agents import create_tool_calling_agent, AgentExecutor  # Agent yapısı
from langchain_experimental.tools import PythonREPLTool   # Python kod çalıştırma
from langchain_experimental.agents.agent_toolkits import create_csv_agent  # CSV analizi
from langchain.tools import tool                          # Custom tool decorator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # Prompt yönetimi
from langchain.memory import ConversationBufferMemory     # Konuşma hafızası
from config.settings import OPENAI_MODEL                  # Model ayarları

# GLOBAL KONUŞMA HAFIZASI
# Tüm conversation'lar boyunca kullanıcı ile agent arasındaki geçmiş konuşmaları saklar
conversation_memory = ConversationBufferMemory(
   memory_key="chat_history",    # Hafızadaki key adı
   return_messages=True          # Mesajları liste olarak döndür
)

# ANA AI MODEL KURULUMU
llm = ChatOpenAI(model=OPENAI_MODEL)

# PYTHON AGENT KURULUMU
# Bu agent Python kodu yazıp çalıştırabilir

# Python agent'ına verilen talimatlar
python_instructions = """You are an agent designed to write and execute python code to answer questions.
                     You have access to a python REPL, which you can use to execute python code.
                     If you get an error, debug your code and try again.
                     Only use the output of your code to answer the question.
                     You might know the answer without running any code, but you should still run the code to get the answer.
                     If it does not seen like you can write code to answer the question, Just return "I don't know" as the answer."""

# Python agent için prompt template
python_prompt = ChatPromptTemplate.from_messages([  
   ("system", python_instructions),              # Sistem talimatları
   ("human", "{input}"),                        # Kullanıcı girişi
   MessagesPlaceholder("agent_scratchpad")      # Agent'ın düşünce süreci
])

# Python REPL aracını oluştur
pythonTool = PythonREPLTool()
tools = [pythonTool]

# Python agent'ını oluştur
python_agent = create_tool_calling_agent(  
   llm=llm,              # Kullanılacak AI model
   tools=tools,          # Kullanılabilir araçlar
   prompt=python_prompt  # Prompt template
)

# Python agent executor'ını oluştur
python_agent_executor = AgentExecutor(
   agent=python_agent,           # Agent objesi
   tools=tools,                  # Araçlar
   verbose=True,                 # Debug çıktısı göster
   handle_parsing_errors=True    # Parsing hatalarını otomatik düzelt
)

# CSV AGENT KURULUMU
# Bu agent CSV dosyalarını pandas ile analiz edebilir

# Global değişken - şu anda yüklü CSV için agent
csv_agent_executor = None

def update_csv_agent(new_csv_path):
   """
   Yeni CSV dosyası için agent oluştur/güncelle
   
   Args:
       new_csv_path (str): Yeni CSV dosyasının yolu
   
   Returns:
       bool: Başarılı ise True
   """
   global csv_agent_executor
   
   # CSV dosyası için özel agent oluştur
   csv_agent_executor = create_csv_agent(
       llm=llm,                      # Aynı AI model
       path=new_csv_path,            # CSV dosya yolu
       verbose=True,                 # Debug çıktısı
       allow_dangerous_code=True     # Pandas kodlarına izin ver
   )
   return True

def clear_csv_agent():
   """
   CSV agent'ını temizle
   Dosya kaldırıldığında hafızayı sıfırlamak için
   """
   global csv_agent_executor
   csv_agent_executor = None

# CUSTOM TOOL'LAR
# Bu tool'lar router agent tarafından kullanılacak

@tool
def python_agent_tool(query: str) -> str:
   """
   Python kodu yazma ve çalıştırma aracı
   
   Kullanım alanları:
   - Matematik hesaplamaları
   - Algoritma yazımı
   - Veri işleme
   - Genel programlama soruları
   
   Args:
       query (str): Doğal dil sorusu (KOD DEĞİL!)
   
   Returns:
       str: Python kodunun çalıştırılma sonucu
   """
   # Python agent'ını çağır ve sonucu al
   result = python_agent_executor.invoke({"input": query})
   return result.get("output", str(result))

@tool
def csv_agent_tool(query: str) -> str:
   """
   CSV dosyası analiz aracı
   
   Kullanım alanları:
   - Veri analizi soruları
   - Pandas işlemleri
   - İstatistiksel hesaplamalar
   - CSV içeriği sorgulamaları
   
   Args:
       query (str): CSV ile ilgili soru
   
   Returns:
       str: Analiz sonucu
   """
   # CSV yüklü değilse uyarı ver
   if csv_agent_executor is None:
       return "No CSV file is currently loaded. Please upload a CSV file first."
   
   # CSV agent'ını çağır ve sonucu al
   result = csv_agent_executor.invoke({"input": query})
   return result.get("output", str(result))

# ROUTER AGENT KURULUMU
# Bu ana agent hangi tool'un kullanılacağına karar verir

# Router agent talimatları
router_instructions = """You are a helpful AI assistant with conversation memory.
You remember previous parts of our conversation and can refer back to them.
You can remember user's name, preferences, and context from earlier in our conversation.

Use python_agent_tool when:
- User asks for Python code generation, execution, or programming tasks
- Mathematical calculations that need Python
- Data processing, algorithms, or programming concepts

Use csv_agent_tool when:
- User asks questions about CSV file data
- Data analysis questions about the CSV data
- Questions that need pandas operations on the CSV

Choose the appropriate tool based on the user's question and maintain conversation context."""

# Router agent prompt'u
router_prompt = ChatPromptTemplate.from_messages([  
   ("system", router_instructions),                    # Sistem talimatları
   MessagesPlaceholder(variable_name="chat_history"),  # Geçmiş konuşmalar
   ("human", "{input}"),                              # Yeni kullanıcı sorusu
   MessagesPlaceholder("agent_scratchpad")            # Agent düşünce süreci
])

# Router'ın kullanabileceği tool'lar
router_tools = [python_agent_tool, csv_agent_tool]

# Router agent'ını oluştur
router_agent = create_tool_calling_agent(  
   llm=llm,              # AI model
   tools=router_tools,   # Kullanılabilir tool'lar
   prompt=router_prompt  # Prompt template
)

# ANA AGENT EXECUTOR - Bu uygulama genelinde kullanılan
router_agent_executor = AgentExecutor(
   agent=router_agent,           # Router agent
   tools=router_tools,           # Tool'lar
   memory=conversation_memory,   # Konuşma hafızası
   verbose=True,                 # Debug çıktısı
   handle_parsing_errors=True    # Hata düzeltme
)