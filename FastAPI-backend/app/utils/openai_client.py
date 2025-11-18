# import os
# import openai
# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# async def generate_response(message: str) -> str:
#     """
#     Generate a chatbot response using OpenAI API.
#     """
#     try:
#         response = await openai.ChatCompletion.acreate(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": message}],
#         )
#         return response.choices[0].message["content"].strip()
#     except Exception as e:
#         return f"Error generating response: {str(e)}"
