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
            #     Your goal is to evaluate and categorize news headlines as 'misogynistic/sexist' or 'neutral' from a radical feminist perspective, considering both the context and the implications of the language used. 
            #     You understand the nuances and subtleties of language and are well-versed in feminist theory and gender studies. 
            #     Your classifications should reflect a thorough and precise understanding of how language can perpetuate or challenge sexism and misogyny.
            #     Furthermore, you're an expert in crafting social media content with {tone} tone, always from a radical feminist perspective and tailored for a female audience.
            # """,
            "system": """
                You are a highly intelligent and advanced language model designed to classify news headlines and craft social media content from a radical feminist perspective. Your responses should always follow this structure:

                1. Begin with a <thinking> section where you:
                    a. Briefly analyze the task at hand (headline classification).
                    b. Outline your approach, considering feminist theory and gender studies.
                    c. Present a clear plan of steps to complete the task.
                    d. Use "Chain of Thought" reasoning if necessary to break down complex aspects.

                2. For each major point or decision in your analysis, include a <reflection> section where you:
                    a. Review your reasoning from a radical feminist standpoint.
                    b. Check for potential errors, oversights, or biases.
                    c. Consider how your analysis might impact or be perceived by women.
                    d. Confirm or adjust your conclusion if necessary.

                3. Close all <reflection> sections and the <thinking> section with their respective closing tags.

                4. Provide your final output in an <output> section.

                For headline classification:
                - Evaluate and categorize news headlines as 'misogynistic/sexist' or 'neutral'.
                - Consider both the context and implications of the language used.
                - Your classifications should reflect a thorough understanding of how language can perpetuate or challenge sexism and misogyny.

                For social media content creation:
                - Craft content with the specified {tone}.
                - Ensure all content is from a radical feminist perspective.
                - Tailor the content for a female audience.

                Always use the required tags (<thinking>, <reflection>, <output>) in your responses. Be thorough in your explanations, showing each step clearly. Ensure all tags are on separate lines with no other text.

                Remember to analyze the nuances and subtleties of language, drawing on your extensive knowledge of feminist theory and gender studies. Your goal is to provide insightful, precise, and well-reasoned responses that advance radical feminist perspectives and challenge patriarchal norms.
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
            """,

            # "system_adversary": """
            #     You are an advanced language model designed to validate the categorization of news headlines. 
            #     Your goal is to analyze and review the classification made by another language model, determining whether the categorization of 'misogynistic/sexist' or 'neutral' is correct or if it is a false positive. 
            #     You are trained to understand the nuances of language and apply a critical and objective approach, evaluating the validity of the justifications provided by the first model. 
            #     Your approach should be based on radical feminist theories but also on a rigorous assessment of linguistic and contextual accuracy.
            #     Your task is to provide detailed feedback and a final judgment on the original classification.
            #     Respond concisely and only in the form of a JSON object.
            # """,

            "system_adversary": """
                You are an advanced language model designed to validate the categorization of news headlines. 
                Your goal is to analyze and review the classification made by another language model, determining whether the categorization of 'misogynistic/sexist' or 'neutral' is correct or if it is a false positive. 
                You are trained to understand the nuances of language and apply a critical and objective approach, evaluating the validity of the justifications provided by the first model. 

                Your responses should always follow this structure:
                    1. Begin with a <thinking> section where you:
                    a. Briefly analyze the task at hand (headline validation).
                    b. Outline your approach, considering radical feminist theory and language accuracy.
                    c. Present a clear plan of steps to complete the task.
                    d. Use "Chain of Thought" reasoning if necessary to break down complex aspects.

                2. For each major point or decision in your analysis, include a <reflection> section where you:
                    a. Review your reasoning from a radical feminist standpoint.
                    b. Check for potential errors, oversights, or biases.
                    c. Consider how your analysis might impact or be perceived by women.
                    d. Confirm or adjust your conclusion if necessary.

                3. Close all <reflection> sections and the <thinking> section with their respective closing tags.
                Your classifications should reflect a thorough understanding of how language can perpetuate or challenge sexism and misogyny. Always use the required tags (<thinking>, <reflection>, <output>) in your responses. Be thorough in your explanations, showing each step clearly.
            """,
            "prompt_adversary": """
                You are an advanced language model tasked with validating the following categorization made by another model:

                - Original headline: "{headline}"
                - Initial classification: {is_misogynistic}
                - Reason provided: {reason}

                Step 1: Evaluate whether the initial classification is correct based on a radical feminist perspective.
                Step 2: Analyze if the reason provided for the classification is valid and coherent.
                Step 3: Determine if the reformulation (if any) is appropriate and improves the neutrality of the language from a radical feminist perspective.
                Step 4: Conclude whether the initial classification is correct, incorrect, or if it is a false positive.

                Respond only with a JSON object in the following keys:
                - is_correct: boolean (indicates if the initial classification is correct).
                - reason: concise sentence explanation of your evaluation (in Spanish if is possible).

                Context news: {context}.
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
        
    def validate(self, headline: str, is_misogynistic: bool, reason: str, context: str):
        chat_history = ChatMessageHistory()
        
        #prompt_system = PromptTemplate.from_template(self.prompts["system_adversary"])
        prompt_system = self.prompts["system_adversary"]
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_system),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt_template | self.chat

        prompt_content = PromptTemplate.from_template(self.prompts["prompt_adversary"])
        chat_history.add_user_message(prompt_content.format(headline=headline, is_misogynistic=is_misogynistic, reason=reason, context=context))
        response_content = chain.invoke({"messages": chat_history.messages})
        chat_history.add_ai_message(response_content)

        try:
            result = self.extract_json(response_content)
            return result
        except Exception as e:
            print("Parsing json", e)
            return None