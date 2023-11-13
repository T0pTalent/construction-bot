import openai
import pinecone
from config import *
from utils import *
from functions import function_list

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

class ChatBot():
    def __init__(self) -> None:
        self.index_name = PINECONE_INDEX_NAME
        self.pinecone_index = pinecone.Index(self.index_name)
        self.top_k = 10

        self.function_call_prompt = {"role": "system", "content": "You are a helpful assistant in construction Industry."}

        self.greeting_prompt = {
            "role": "system",
            "content": "You are a helpful assistant in Construction Industry. If the user greets you, then greet the user and ask user's specialties politely."
        }

        self.specialty_prompt = {
            "role": "system",
            "content": "You are a helpful assistant in Construction Industry. User's specialty is <specialty>. Encourage users to ask knowledge related his specialty in the construction sector politely."
        }

        self.main_prompt = {
            "role": "system",
            "content": "You are a helpful assistant in Construction Industry. You need to answer user's question based on the data from your knowledge base and conversation history"
        }

        self.unfamiliar_prompt = {
            "role": "system",
            "content": "You are a helpful assistant in Construction Industry. Refuse to answer user's question politely and encourage user to chat related to knowledge about construction industry."
        }

        self.messages = []
        self.history = []

    def query_db(self, query, top_k=3):
        # Query the Pinecone DB and get references
        query_vector = embedding(query)
        # Get the references from Pinecone DB
        result = self.pinecone_index.query(
            vector=query_vector, top_k=top_k)
        matches = result.to_dict()["matches"]
        ids = []
        for match in matches:
            ids.append(match["id"])
        data = self.pinecone_index.fetch(ids).to_dict()["vectors"]
        descriptions = []
        for id in ids:
            descriptions.append(data[id]["metadata"]['answer'])
        return '\n'.join(descriptions)

    def run(self, query):
        self.history.append({"role": "user", "content": query})
        if len(self.history) < 5:
            self.messages = [self.function_call_prompt] + self.history
        else:
            self.messages = [self.function_call_prompt] + self.history[-5:]
        
        function_response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=self.messages,
            temperature=0,
            functions=function_list,
            function_call="auto"
        )

        if function_response.choices[0].finish_reason == "function_call":
            params = function_response['choices'][0].message.function_call
            print(params.name)
            if params.name == 'greeting':
                messages = [self.greeting_prompt] + self.messages[1:]
                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    temperature=0.7,
                )
                self.history.append({'role': 'assistant', 'content': response.choices[0].message["content"]})
                return response.choices[0].message["content"]
            elif params.name == 'specialty':
                query = json.loads(params.arguments)['query']
                sys_prompt = self.specialty_prompt
                sys_prompt['content'] = self.specialty_prompt['content'].replace('<specialty>', query)
                messages = [sys_prompt] + self.messages[1:]
                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    temperature=0.7
                )
                self.history.append({'role': 'assistant', 'content': response.choices[0].message["content"]})
                return response.choices[0].message["content"]
            elif params.name == 'ask_knowledge':
                query = json.loads(params.arguments)['query']
                knowledge = f'This is knowledge from my knowledge base:\n{self.query_db(query)}'
                messages = [self.main_prompt] + self.messages[1:-1] + [{'role': 'assistant', 'content': knowledge}] + [self.messages[-1]]
                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    temperature=0.3
                )
                self.history.append({'role': 'assistant', 'content': response.choices[0].message["content"]})
                return response.choices[0].message["content"]
            elif params.name == 'unfamiliar_question':
                messages = [self.unfamiliar_prompt] + self.messages[1:]
                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    temperature=0.7
                )
                self.history.append({'role': 'assistant', 'content': response.choices[0].message["content"]})
                return response.choices[0].message["content"]
            else:
                self.history.append({'role': 'assistant', 'content': function_response.choices[0].message["content"]})
                return function_response.choices[0].message['content']
        