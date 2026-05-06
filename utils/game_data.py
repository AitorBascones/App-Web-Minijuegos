"""
Default game templates. Admin can use these or create custom rounds.
"""
GAME_TEMPLATES = [
    {
        "title": "🔢 Ordena como puedas",
        "rounds": [
            {
                "topic": "Presentadores de televisión",
                "question": "Ordena estos actores de MENOR a MAYOR edad",
                "options": ["Pablo Motos", "Jordi Hurtado", "Karlos Arguiñano", "Jorge Javier Vázquez"],
                "correct_answer": '["Jorge Javier Vázquez", "Pablo Motos", "Jordi Hurtado", "Karlos Arguiñano"]'
            },
            
            {
                "topic": "Influencers",
                "question": "Ordena estos influencers de MAYOR a MENOR número de seguidores en instagram",  
                "options": ["Clers", "Javi Hoyos", "Peldanyos", "Erra"],
                "correct_answer": '["Peldanyos", "Javi Hoyos", "Clers", "Erra"]'
                
            },
            
            {
                "topic": "Inventos",
                "question": "Ordena estos inventos del MÁS ANTIGUO al MÁS RECIENTE",
                "options": ["Café Instantáneo", "Tostadora", "Velcro", "Cubo de Rubbik"],
                "correct_answer": '["Tostadora", "Café Instantáneo", "Velcro", "Cubo de Rubbik"]',
                
            },
            
            {
                "topic": "Canciones",
                "question": "Ordena estas canciones de MÁS a MENOS voisitas en Youtube",
                "options": ["She dont give a fo", "La Macarena", "Quedate", "Gasolina"],
                "correct_answer": '["She dont give a fo", "La Macarena", "Quedate", "Gasolina]"',
                
            },
            
            {
                "topic": "Series Españolas",
                "question": "Ordena estas series de MÁS a MENOS episodios",
                "options": ["AQNHQV", "LQSA", "Aída", "Los Hombres de Paco"],
                "correct_answer": '["Aída", "LQSA", "Los Hombres de Paco", "AQNHQV"]',
                
            },
        ],
    },
    
    {

        "title": "🤔 ¿Qué prefieres?",
        "rounds": [
            {
                "topic": "Gastronomía",
                "question": "¿Qué prefieres?",
                "options": ["Beberte un cubata cada vez que te despiertas (siestas incluidas) ", "Elegir un desayuno, un almuerzo y una cena de por vida"],
                "correct_answer": None
            },
            {
                "topic": "Moda",
                "question": "¿Qué prefieres?",
                "options": ["Ir siempre con una mancha", "Que toda tu ropa sea de un solo color"],
                "correct_answer": None
            },
            {
                "topic": "Comunicación",
                "question": "¿Qué prefieres?",
                "options": ["Solo utilizar texto para comunicarte (ni auidios,ni emojis,stickers...)", "Cada vez que quieras hablar con alguién tienes que cambiarle el nombre en tus contactos"],
                "correct_answer": None
            },
            
              {
                "topic": "Sexo",
                "question": "¿Qué prefieres?",
                "options": ["Solo poder participar en orgías de 10 o más personas", "Cada año no poder repetir con niguna persona"],
                "correct_answer": None
            },
              {
                "topic": "Familia",
                "question": "¿Qué prefieres?",
                "options": ["Quedarte en casa de tus padres hasta los 60", "No saber nada de nadie de tu familia por 1 año"],
                "correct_answer": None
            },
               {
                "topic": "Incomodidades",
                "question": "¿Qué prefieres?",
                "options": ["Sentir siempre un pelo en la boca", "Sentir siempre una piedra en el zapato"],
                "correct_answer": None
            },
                {
                "topic": "Random",
                "question": "¿Qué prefieres?",
                "options": ["Pelearte con 100 caballos del tamaño de un pato", "Pelearte con un pato del tamaño de un caballo"],
                "correct_answer": None
            },
        ],
    },
    
    {
        "title": "🎯 ¿Quién se acerca más?",
        "rounds": [
            {
                "topic": "Que tio más cansino",
                "question": "¿Cuanto es el mayor tiempo que se ha pasado una persona hablando ininterrumpidamente? (Horas)",
                "options": [],
                "correct_answer": "124"
            },
            {
                "topic": "Duelo de miradas",
                "question": "¿Cuál es el record de tiempo sin pestañear? (Minutos)",
                "options": [],
                "correct_answer": "57"
            },
            {
                "topic": "Que barbaridad",
                "question": "¿Cual es el máximo peso que ha levantado una persona solo con la barba (Kg)?",
                "options": [],
                "correct_answer": "68.3"
            },
            
                        {
                "topic": "Hipo tengo y a mi amor se lo recomiendo",
                "question": "¿Cuanto duró el hipo más largo del mundo (días)?",
                "options": [],
                "correct_answer": "24820"
            },
                                    {
                "topic": "Por cojones que entramos",
                "question": "¿Cual es el nº máximo de personas que se han metido dentro de un smart?",
                "options": [],
                "correct_answer": "20"
            },
                                                {
                "topic": "Maestro liendre",
                "question": "¿Cuál es el record de persona con más carreras universatarias?",
                "options": [],
                "correct_answer": "13"
            },
                                                            {
                "topic": "Sorpresa",
                "question": "¿Cual es el record de tener records mundiales?",
                "options": [],
                "correct_answer": "551"
            },
        ],
    },
]

AVATARS = ["🦁", "🐸", "🦊", "🐺", "🦄", "🐲", "🦅", "🐬", "🦋",
           "👨‍🍳","👮‍♀️","👼","🕵️‍♂️","👨‍🌾","👩‍🏭","🧑‍🚒","👰","🧙‍♂️","🧛","🧜‍♀️","💁‍♂️",
           "💁‍♀️","🤹","🏃‍♂️‍➡️","🏄‍♀️","🏋️‍♀️","🚵‍♀️","🤸‍♀️","⛹️‍♀️","⛹️‍♂️","🤽‍♀️","🛀","👩‍🦽"]