from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_core.messages import AIMessage
import json
import cachetools

from lunary import LunaryCallbackHandler

class HeadlineAnalyzer:
    def __init__(self, 
                base_url="http://localhost:1234/v1", 
                api_key="not-needed", 
                temperature=0,
                model="gpt-3.5-turbo"):
        
        handler = LunaryCallbackHandler(app_id="482206eb-58f4-4301-b72b-0810f8f91433")

        self.chat = ChatOpenAI(
            base_url=base_url, 
            api_key=api_key,
            temperature=temperature,
            model=model
            ,callbacks=[handler]
        )
        self.prompts = {
            # "system": """
            #     You are a highly intelligent and advanced language model designed to classify news headlines. 
            #     Your goal is to evaluate and categorize news headlines as "misogynistic/sexist" or "neutral" from a radical feminist perspective, considering both the context and the implications of the language used. 
            #     You understand the nuances and subtleties of language and are well-versed in feminist theory and gender studies. 
            #     Your classifications should reflect a thorough and precise understanding of how language can perpetuate or challenge sexism and misogyny.
            #     Furthermore, you're an expert in crafting social media content with sarcasm and irony, always from a radical feminist perspective and tailored for a female audience.
            #     Avoid using double quotes (\") in your responses to prevent possible errors with the JSON format.
            # """,
            # "prompt_1": """
            #     Classify the following news headline into one of two categories: "misogynistic/sexist" or "neutral." Your evaluation should be based on a radical feminist perspective and a precise and careful interpretation of what constitutes misogyny and sexism. Provide a brief explanation for your classification.
            #     If the headline is in Spanish, first translate to English and then classify.
            #     At the end add a JSON object with keys:
            #     - is_misogynistic: boolean.
            #     - refactored: refactor the headline from a radical feminist perspective with sarcasm and irony focused on the creation of content for social networks making it evident why it is a misogynistic/sexist headline (only if is_misogynistic is true).
            #     - refactored_es: value of the new_headline key translated into Spanish (only if is_misogynistic is true).
            
            #     Headline: {headline}
            # """,
            # "system_content": """
            #     You are an exceptional content creator known for crafting viral content in a sarcastic, funny, and ironic tone, always from a radical feminist perspective and tailored for a female audience. 
            #     Your task is to take headlines and expose why they are misogynistic or sexist. 
            #     Your analysis should be sharp, witty, and clearly highlight the underlying sexism or misogyny in each headline. 
            #     Use your creativity to reformulate these headlines in a way that emphasizes their sexist nature while entertaining and engaging your audience.
            #     Avoid using double quotes (\") in your responses to prevent possible errors with the JSON format.
            # """,
            # "prompt_content": """
            #     Take the following headline and transform it into a sarcastic, hilarious, and deeply ironic statement that exposes the blatant sexism or misogyny behind it. 
            #     Your response should be sharp and witty, providing an insightful analysis that is both engaging and entertaining for a female audience. 
            #     Aim to create a headline that not only points out the sexist nature but does so in a way that is irresistible and thought-provoking. 
            #     Provide a brief reasoning on why the headline is sexist or misogynistic to use in your reformulation.
            #     Avoid using double quotes (\") in your responses to prevent possible errors with the JSON format.
            #     At the end, create a JSON object with the following keys:
            #     - refactored: new headline
            #     - refactored_es: value of the new_headline key translated into Spanish
            #     Headline: {headline}
            #     Brief summary of the news: {context}
            # """

            "system": """
                You are a highly intelligent and advanced language model designed to classify news headlines. 
                Your goal is to evaluate and categorize news headlines as 'misogynistic/sexist' or 'neutral' from a radical feminist perspective, considering both the context and the implications of the language used. 
                You understand the nuances and subtleties of language and are well-versed in feminist theory and gender studies. 
                Your classifications should reflect a thorough and precise understanding of how language can perpetuate or challenge sexism and misogyny.
                Furthermore, you're an expert in crafting social media content with {tone} tone, always from a radical feminist perspective and tailored for a female audience.
            """,
            "prompt_1": """
                You are a highly intelligent and advanced language model designed to classify news headlines.

                Step 1: Translate the headline to English if it is in Spanish.
                Step 2: Analyze the headline based on a radical feminist perspective.
                Step 3: Determine if the headline is 'misogynistic/sexist' or 'neutral'.
                Step 4: Provide a brief explanation for your classification.
                Step 5: If classified as 'misogynistic/sexist', reformulate the headline from a radical feminist perspective with {tone} tone.
                Step 6: Translate the refactored headline back into Spanish.

                At the end, create a JSON object with the following keys:
                - is_misogynistic: boolean.
                - reason: why is sexist or misogynistic? (In Spanish, concise sentence)
                - refactored: refactor the headline using reason from a radical feminist perspective with {tone} tone, focused on the creation of content for social networks making it evident why it is a misogynistic/sexist headline (only if is_misogynistic is true).
                - refactored_es: value of the new_headline key translated into Spanish (only if is_misogynistic is true).

                Headline: "{headline}"
            """,
            "system_content": """
                You are an exceptional content creator known for crafting viral content in a {tone} tone, always from a radical feminist perspective and tailored for a female audience.
                Your task is to take headlines and expose why they are misogynistic or sexist.
                Your analysis should clearly highlight the underlying sexism or misogyny in each headline.
                Use your creativity to reformulate these headlines in a way that emphasizes their sexist nature while engaging your audience.
                Avoid using double quotes (\") in your responses to prevent possible errors with the JSON format.
            """,
            "prompt_content": """
                You are an exceptional content creator known for crafting viral content.

                Step 1: Read the headline and the brief summary of the news.
                Step 2: Analyze the headline to identify any underlying sexism or misogyny.
                Step 3: Provide a brief reasoning on why the headline is sexist or misogynistic.
                Step 4: Transform the headline into a statement that aligns with the {tone} tone, exposing the blatant sexism or misogyny behind it.
                Step 5: Ensure your response is engaging and fitting for a female audience.
                Step 6: Translate the refactored headline into Spanish.

                Avoid using double quotes (\") in your responses to prevent possible errors with the JSON format.
                
                At the end, create a JSON object with the following keys:
                - reason: why is sexist or misogynistic? (In Spanish, concise sentence)
                - refactored: use reason to generate new headline
                - refactored_es: value of the new_headline key translated into Spanish

                Headline: "{headline}"
                Brief summary of the news: "{context}"
            """
        }

        self.default_empty_object = {
            "is_misogynistic": None,
            "refactored": None,
            "refactored_es": None,
        }

        self.cache = cachetools.LRUCache(maxsize=100)

    def get_cache(self, movie, year):
        key = (movie, year)
        return self.cache.get(key)

    def set_cache(self, movie, year, value):
        key = (movie, year)
        self.cache[key] = value

    def clear_cache(self):
        self.cache.clear()

    def run(self, headline: str, tone: str = "Engaging and Conversational"):
        chat_history = ChatMessageHistory()

        prompt_system = PromptTemplate.from_template(self.prompts["system"])
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_system.format(tone=tone)),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt_template | self.chat

        
        # Step 1
        prompt_1 = PromptTemplate.from_template(self.prompts["prompt_1"])
        chat_history.add_user_message(prompt_1.format(headline=headline, tone=tone))
        response_1 = chain.invoke({"messages": chat_history.messages})
        chat_history.add_ai_message(response_1)
        
        try:
            result = self.extract_json(response_1)
            return result if result else self.default_empty_object
        except Exception as e:
            print("Parsing json", e)
            return self.default_empty_object
    
    def extract_json(self, ai_message: AIMessage) -> dict:
        """Extracts the JSON object from the AI message"""
        try:
            start_index = ai_message.content.find("{")
            end_index = ai_message.content.rfind("}")
            json_str = ai_message.content[start_index:end_index+1]
            if not json_str:
                return None
            return json.loads(json_str)
        except Exception as e:
            return None
        
    def regenerate(self, headline: str, context: str = "", tone: str = "Engaging and Conversational"):
        chat_history = ChatMessageHistory()
        
        prompt_system = PromptTemplate.from_template(self.prompts["system_content"])
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_system.format(tone=tone)),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt_template | self.chat

        prompt_content = PromptTemplate.from_template(self.prompts["prompt_content"])
        chat_history.add_user_message(prompt_content.format(headline=headline, context=context, tone=tone))
        response_content = chain.invoke({"messages": chat_history.messages})
        chat_history.add_ai_message(response_content)

        try:
            result = self.extract_json(response_content)
            return result if result else self.default_empty_object
        except Exception as e:
            print("Parsing json", e)
            return self.default_empty_object