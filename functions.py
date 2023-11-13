function_list = [
    {
        "name": "greeting",
        "description": "This function is callend when user greets to the bot",
        "parameters": {
            "type": "object",
            "properties": {
            },
        "required": [],
        },
    },
    {
        "name": "specialty",
        "description": "This function is called when user says his specialty in construction industry. e.g. My specialty is electrical. or I have specialty in plumbing. or I majored in carpentry.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The specialty of the user in construction industry like eletrical, plumbing or carpentry. If you didn't detect any specialty in construction industry return none. e.g. User: My specialty is electrical, query: 'electrical', User: I didn't specialized in construction industry. query: 'none'"
                }
            },
            "required": [],
        }
    },
    {
        "name": "ask_knowledge",
        "description": "This function is called when user asks knowledge about construction industry. e.g. How are costs estimated in a construction project?, Can you explain the process of procurement in construction?",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The exact object of user's question. This extracts the knowledge user needs exactly from the question"
                }
            },
            "required": []
        }
    },
    {
        "name": "unfamiliar_question",
        "description": "This function is called when user's question is not related to greetings or any field in construction industry. e.g. I have dinner. I love you. I like foods. or what is html? what is javascript?",
        "parameters": {
            "type": "object",
            "properties": {
            },
        "required": [],
        },
    }
]