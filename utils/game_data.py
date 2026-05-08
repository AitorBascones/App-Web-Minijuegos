"""
Default game templates. Admin can use these or create custom rounds.
"""

# Duración sugerida (segundos) para cada tipo de juego en fase active
ROUND_DURATIONS = {
    1: 90,   # Ordenar — necesita tiempo para pensar
    2: 45,   # Preferencias — decisión rápida e intuitiva
    3: 60,   # Numérico — estimación
    4: 30,   # Trivia — o lo sabes o no lo sabes
}

GAME_TEMPLATES = [
    # ─────────────────────────────────────────────────────────────────────────
    # JUEGO 1: Ordenar
    # ─────────────────────────────────────────────────────────────────────────
    {
        "title": "🔢 Ordena como puedas",
        "rounds": [
            {
                "topic": "Presentadores de televisión",
                "question": "Ordena estos presentadores de MENOR a MAYOR edad",
                "options": ["Pablo Motos", "Jordi Hurtado", "Karlos Arguiñano", "Jorge Javier Vázquez"],
                "correct_answer": '["Jorge Javier Vázquez", "Pablo Motos", "Jordi Hurtado", "Karlos Arguiñano"]'
            },
            {
                "topic": "Influencers",
                "question": "Ordena estos influencers de MAYOR a MENOR número de seguidores en Instagram",
                "options": ["Clers", "Javi Hoyos", "Peldanyos", "Erra"],
                "correct_answer": '["Peldanyos", "Javi Hoyos", "Clers", "Erra"]'
            },
            {
                "topic": "Inventos",
                "question": "Ordena estos inventos del MÁS ANTIGUO al MÁS RECIENTE",
                "options": ["Café Instantáneo", "Tostadora", "Velcro", "Cubo de Rubik"],
                "correct_answer": '["Tostadora", "Café Instantáneo", "Velcro", "Cubo de Rubik"]'
            },
            {
                "topic": "Canciones",
                "question": "Ordena estas canciones de MÁS a MENOS visitas en Youtube",
                "options": ["She don't give a fo", "La Macarena", "Quédate", "Gasolina"],
                "correct_answer": '["She don\'t give a fo", "La Macarena", "Quédate", "Gasolina"]'
            },
            {
                "topic": "Series Españolas",
                "question": "Ordena estas series de MÁS a MENOS episodios",
                "options": ["AQNHQV", "LQSA", "Aída", "Los Hombres de Paco"],
                "correct_answer": '["Aída", "LQSA", "Los Hombres de Paco", "AQNHQV"]'
            },

        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # JUEGO 2: ¿Qué prefieres?
    # ─────────────────────────────────────────────────────────────────────────
    {
        "title": "🤔 ¿Qué prefieres?",
        "rounds": [
            {
                "topic": "Gastronomía",
                "question": "¿Qué prefieres?",
                "options": [
                    "Beberte un cubata cada vez que te despiertas (siestas incluidas)",
                    "Elegir un desayuno, un almuerzo y una cena de por vida"
                ],
                "correct_answer": None
            },
            {
                "topic": "Moda",
                "question": "¿Qué prefieres?",
                "options": [
                    "Ir siempre con una mancha",
                    "Que toda tu ropa sea de un solo color"
                ],
                "correct_answer": None
            },
            {
                "topic": "Comunicación",
                "question": "¿Qué prefieres?",
                "options": [
                    "Solo utilizar texto para comunicarte (ni audios, ni emojis, ni stickers...)",
                    "Cada vez que quieras hablar con alguien tienes que cambiarle el nombre en tus contactos"
                ],
                "correct_answer": None
            },
            {
                "topic": "Sexo",
                "question": "¿Qué prefieres?",
                "options": [
                    "Solo poder participar en orgías de 10 o más personas",
                    "Cada año no poder repetir con ninguna persona"
                ],
                "correct_answer": None
            },
            {
                "topic": "Familia",
                "question": "¿Qué prefieres?",
                "options": [
                    "Quedarte en casa de tus padres hasta los 60",
                    "No saber nada de nadie de tu familia por 1 año"
                ],
                "correct_answer": None
            },
            {
                "topic": "Incomodidades",
                "question": "¿Qué prefieres?",
                "options": [
                    "Sentir siempre un pelo en la boca",
                    "Sentir siempre una piedra en el zapato"
                ],
                "correct_answer": None
            },
            {
                "topic": "Random",
                "question": "¿Qué prefieres?",
                "options": [
                    "Pelearte con 100 caballos del tamaño de un pato",
                    "Pelearte con un pato del tamaño de un caballo"
                ],
                "correct_answer": None
            },

        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # JUEGO 3: ¿Quién se acerca más?
    # ─────────────────────────────────────────────────────────────────────────
    {
        "title": "🎯 ¿Quién se acerca más?",
        "rounds": [
            {
                "topic": "Qué tío más cansino",
                "question": "¿Cuánto es el mayor tiempo que se ha pasado una persona hablando ininterrumpidamente? (Horas)",
                "options": [],
                "correct_answer": "124"
            },
            {
                "topic": "Duelo de miradas",
                "question": "¿Cuál es el récord de tiempo sin pestañear? (Minutos)",
                "options": [],
                "correct_answer": "57"
            },
            {
                "topic": "Qué barbaridad",
                "question": "¿Cuál es el máximo peso que ha levantado una persona solo con la barba? (Kg)",
                "options": [],
                "correct_answer": "68.3"
            },
            {
                "topic": "Hipo tengo y a mi amor se lo recomiendo",
                "question": "¿Cuánto duró el hipo más largo del mundo? (Días)",
                "options": [],
                "correct_answer": "24820"
            },
            {
                "topic": "Por cojones que entramos",
                "question": "¿Cuál es el nº máximo de personas que se han metido dentro de un Smart?",
                "options": [],
                "correct_answer": "20"
            },
            {
                "topic": "Maestro liendre",
                "question": "¿Cuál es el récord de persona con más carreras universitarias?",
                "options": [],
                "correct_answer": "13"
            },
            {
                "topic": "Sorpresa",
                "question": "¿Cuál es el récord de tener récords mundiales?",
                "options": [],
                "correct_answer": "551"
            },

        ],
    }
]

AVATARS = [
    "🦁", "🐸", "🦊", "🐺", "🦄", "🐲", "🦅", "🐬", "🦋",
    "👨‍🍳", "👮‍♀️", "👼", "🕵️‍♂️", "👨‍🌾", "👩‍🏭", "🧑‍🚒", "👰", "🧙‍♂️", "🧛", "🧜‍♀️", "💁‍♂️",
    "💁‍♀️", "🤹", "🏃‍♂️‍➡️", "🏄‍♀️", "🏋️‍♀️", "🚵‍♀️", "🤸‍♀️", "⛹️‍♀️", "⛹️‍♂️", "🤽‍♀️", "🛀", "👩‍🦽"
]
