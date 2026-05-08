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
            {
                "topic": "Redes Sociales",
                "question": "Ordena estas redes sociales del AÑO DE CREACIÓN más antiguo al más reciente",
                "options": ["YouTube", "Twitter/X", "Facebook", "TikTok"],
                "correct_answer": '["Facebook", "YouTube", "Twitter/X", "TikTok"]'
            },
            {
                "topic": "Taquilla mundial",
                "question": "Ordena estas películas de MAYOR a MENOR recaudación en taquilla mundial",
                "options": ["Avatar", "Titanic", "El Rey León (2019)", "Frozen II"],
                "correct_answer": '["Avatar", "Titanic", "El Rey León (2019)", "Frozen II"]'
            },
            {
                "topic": "Velocidad animal",
                "question": "Ordena estos animales de MÁS RÁPIDO a MÁS LENTO",
                "options": ["Avestruz", "Guepardo", "Caballo", "Elefante"],
                "correct_answer": '["Guepardo", "Avestruz", "Caballo", "Elefante"]'
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
            {
                "topic": "Superpoderes",
                "question": "¿Qué prefieres?",
                "options": [
                    "Poder volar a voluntad",
                    "Ser invisible a voluntad"
                ],
                "correct_answer": None
            },
            {
                "topic": "Vacaciones",
                "question": "¿Qué prefieres?",
                "options": [
                    "Una semana en playa de lujo todo incluido",
                    "Un mes de mochilero por Asia con presupuesto justo"
                ],
                "correct_answer": None
            },
            {
                "topic": "Tecnología",
                "question": "¿Qué prefieres?",
                "options": [
                    "Vivir sin internet para siempre",
                    "Vivir sin música para siempre"
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
            {
                "topic": "Cartografía mundial",
                "question": "¿Cuántos países hay reconocidos en el mundo?",
                "options": [],
                "correct_answer": "195"
            },
            {
                "topic": "Medicina básica",
                "question": "¿Cuántos litros de sangre tiene de media el cuerpo humano?",
                "options": [],
                "correct_answer": "5"
            },
            {
                "topic": "La gran muralla",
                "question": "¿Cuántos kilómetros mide la Muralla China?",
                "options": [],
                "correct_answer": "21196"
            },
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # JUEGO 4: Trivia Relámpago (nuevo)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "title": "🧠 Trivia Relámpago",
        "rounds": [
            {
                "topic": "Tecnología",
                "question": "¿En qué año se fundó Google?",
                "options": ["1994", "1996", "1998", "2000"],
                "correct_answer": "1998"
            },
            {
                "topic": "Ciencia",
                "question": "¿Cuántos huesos tiene el cuerpo humano adulto?",
                "options": ["156", "206", "256", "306"],
                "correct_answer": "206"
            },
            {
                "topic": "Geografía",
                "question": "¿Cuál es el país más grande del mundo por superficie?",
                "options": ["China", "Canadá", "EEUU", "Rusia"],
                "correct_answer": "Rusia"
            },
            {
                "topic": "Historia",
                "question": "¿En qué año cayó el Muro de Berlín?",
                "options": ["1985", "1987", "1989", "1991"],
                "correct_answer": "1989"
            },
            {
                "topic": "Fútbol",
                "question": "¿Cuántos Balones de Oro tiene Cristiano Ronaldo?",
                "options": ["4", "5", "6", "7"],
                "correct_answer": "5"
            },
            {
                "topic": "Naturaleza",
                "question": "¿Cuántos corazones tiene un pulpo?",
                "options": ["1", "2", "3", "4"],
                "correct_answer": "3"
            },
            {
                "topic": "Tecnología",
                "question": "¿En qué año se lanzó el primer iPhone?",
                "options": ["2005", "2007", "2009", "2011"],
                "correct_answer": "2007"
            },
            {
                "topic": "Cine",
                "question": "¿Cuántos Oscars ganó la película Titanic (1997)?",
                "options": ["9", "11", "13", "7"],
                "correct_answer": "11"
            },
            {
                "topic": "Astronomía",
                "question": "¿Cuántos planetas tiene el Sistema Solar?",
                "options": ["7", "8", "9", "10"],
                "correct_answer": "8"
            },
            {
                "topic": "Arte",
                "question": "¿Quién pintó La Última Cena?",
                "options": ["Miguel Ángel", "Rafael", "Leonardo da Vinci", "Botticelli"],
                "correct_answer": "Leonardo da Vinci"
            },
        ],
    },
]

AVATARS = [
    "🦁", "🐸", "🦊", "🐺", "🦄", "🐲", "🦅", "🐬", "🦋",
    "👨‍🍳", "👮‍♀️", "👼", "🕵️‍♂️", "👨‍🌾", "👩‍🏭", "🧑‍🚒", "👰", "🧙‍♂️", "🧛", "🧜‍♀️", "💁‍♂️",
    "💁‍♀️", "🤹", "🏃‍♂️‍➡️", "🏄‍♀️", "🏋️‍♀️", "🚵‍♀️", "🤸‍♀️", "⛹️‍♀️", "⛹️‍♂️", "🤽‍♀️", "🛀", "👩‍🦽"
]
