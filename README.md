# Análisis de Grafo Social - Instagram

**Integrantes:**
- Andres Castro Gonzalez
- Juan Felipe Hurtado Herrera
- Franco Sebastian Comas Rey

---


### Datos Recolectados

Para cada persona se analizaron tres categorías de información:

1. **Followers (Seguidores):** Usuarios que siguen la cuenta
2. **Following (Siguiendo):** Usuarios que la persona sigue
3. **Topics (Tópicos/Gustos):** Intereses identificados por Instagram


### Herramientas Utilizadas

- **Python 3.x**
- **NetworkX:** Construcción y análisis de grafos
- **Pandas:** Procesamiento de datos
- **Matplotlib & Plotly:** Visualizaciones estáticas e interactivas

### Proceso de Análisis

1. Exportación de datos desde Instagram en formato JSON
2. Procesamiento y normalización de datos
3. Construcción de grafos individuales 
4. Generación de grafo unificado
5. Cálculo de métricas de centralidad
6. Análisis de similitudes y entidades compartidas

---

## Estadísticas Generales

### Resumen por Persona

| Persona | Seguidores | Siguiendo | Conexiones Mutuas | Tópicos de Interés |
|---------|------------|-----------|-------------------|-------------------|
| Andrés | 77 | 214 | 53 | 32 |
| Franco | 44 | 88 | 28 | 51 |
| Juan | 239 | 328 | 111 | 41 |

### Grafo Andres
<img width="2340" height="1620" alt="image" src="https://github.com/user-attachments/assets/4fe39a62-0b5e-4015-99de-6e6fbf92d11a" />

### Grafo Franco
<img width="2340" height="1620" alt="image" src="https://github.com/user-attachments/assets/efef3a9d-359f-4639-8595-f48d54aa587d" />

### Grafo Juan
<img width="2340" height="1620" alt="image" src="https://github.com/user-attachments/assets/edde4147-b0a1-4ebf-8eb5-82fb9aa4a392" />
 
### Observaciones Iniciales

- Juan tiene la red social más amplia, con 239 seguidores y 328 cuentas seguidas
- Juan también tiene el mayor número de conexiones mutuas (111), indicando relaciones bidireccionales más fuertes
- Franco tiene la red más selectiva, con solo 88 cuentas seguidas
- Franco muestra mayor diversidad de intereses con 51 tópicos identificados
- Andrés sigue a más personas de las que lo siguen (214 vs 77), sugiriendo un comportamiento más activo en seguir contenido

---

## Análisis de Comportamiento y Gustos

### Grafo Unificado
<img width="2340" height="1620" alt="image" src="https://github.com/user-attachments/assets/848ba50b-63a6-46d8-80ff-3fcdc1bb3d1b" />

### Grafo Con Numero de Conexiones 
<img width="840" height="700" alt="image" src="https://github.com/user-attachments/assets/6c7a02b9-1f3d-4929-a98c-51efde344f22" />

### Visualizar Grafo Interactivo
- [Ver Grafo Interactivo](https://andrescgon.github.io/Grafo-Red-Social/out/grafo_interactivo.html)
- O abrir localmente: `out/grafo_interactivo.html` en navegador web

### Tópicos Compartidos por TODAS las Personas (21 tópicos)

El análisis reveló **21 tópicos en común** entre las tres personas, lo que representa:
- 65.6% de los intereses de Andrés
- 41.2% de los intereses de Franco
- 51.2% de los intereses de Juan

#### Lista de Intereses Compartidos:

**Deportes y Actividad Física:**
- Soccer (fútbol)
- Combat sports (deportes de combate)
- Football family of sports
- Gym workouts (gimnasio)
- Types of sports

**Tecnología y Entretenimiento:**
- Video games
- Battle royale video games (Fortnite, PUBG, etc.)
- Video games by game play genre
- TV & Movies by genre
- Animation TV & Movies

**Moda y Estilo Personal:**
- Fashion
- Fashion products
- Hair care
- Beauty

**Naturaleza y Mascotas:**
- Animals
- Cats
- Dogs
- Mammals
- Pets

**Otros:**
- Ground transportation
- Visual arts
- Travel destinations 

### Análisis de Similitud por Pares

#### Andrés ↔ Franco: 24 tópicos comunes (75% de Andrés, 47% de Franco)
Destacan intereses compartidos en:
- Board games y tabletop games
- Cars & trucks

#### Andrés ↔ Juan: 24 tópicos comunes (75% de Andrés, 58.5% de Juan)
Destacan intereses compartidos en:
- Boxing 
- Clothing & accessories

#### Franco ↔ Juan: 31 tópicos comunes (60.8% de Franco, 75.6% de Juan)
Mayor similitud entre todos los pares, destacando:
- Basketball
- Motorsports y car racing
- Alcoholic beverages
- Body art y body modification
- Survival video games

### Interpretación de Gustos

El análisis muestra que:

1. Perfil deportivo común: Los tres comparten gran interés por deportes, especialmente fútbol y actividades de gimnasio, típico de estudiantes universitarios activos.

2. Cultura gamer: El interés compartido en videojuegos, especialmente battle royale, sugiere que juegan juntos o comparten conversaciones sobre gaming.

3. Preocupación por imagen personal: Los tópicos de moda, belleza y cuidado del cabello son universales, reflejando la edad y etapa de vida.

4. Amor por mascotas: La presencia de múltiples categorías de mascotas (perros, gatos, pets) sugiere un grupo que comparte contenido de animales.

---

## Análisis de Conexiones Sociales

### Cuentas Seguidas por TODAS las Personas (5 cuentas)

Las únicas 5 cuentas que las tres personas siguen son:

1. @auronplay - YouTuber/streamer español (entretenimiento)
2. @gutierreztovar_jefferson - COMPAÑERO DE UNIVERSIDAD
3. @nigg_.1 - COMPAÑERO DE UNIVERSIDAD
4. @santigl_0016 - COMPAÑERO DE UNIVERSIDAD
5. @usergioarboleda - CUENTA OFICIAL DE LA UNIVERSIDAD SERGIO ARBOLEDA

### Análisis Crítico

Este resultado es altamente significativo y confirma la hipótesis inicial: la gran mayoría de conexiones compartidas provienen del entorno universitario.

### Cuentas Compartidas por Pares

#### Andrés ↔ Franco: 10 cuentas en común

Análisis por categoría:

Compañeros/Universidad (70%):
- @gutierreztovar_jefferson
- @nigg_.1
- @santigl_0016
- @usergioarboleda
- @confesiones.usergioarboleda (página de confesiones de la universidad)
- @andresmr32
- @juaaan_f

YouTubers/Streamers (30%):
- @auronplay
- @elrubiuswtf
- @vegetta777


Conclusión: 70/30 entre contenido universitario y entretenimiento gaming hispanohablante.

#### Andrés ↔ Juan: 17 cuentas en común

Análisis por categoría:

La mayoría de las cuentas que Andrés y Juan comparten corresponden a:
- Compañeros de universidad
- Familiares
- Compañeros del colegio

Aproximadamente 16 de 17 cuentas (94%) pertenecen a estas categorías, con solo 1 cuenta de entretenimiento (@auronplay).

Las cuentas incluyen:
- @gutierreztovar_jefferson (universidad)
- @nigg_.1 (universidad)
- @santigl_0016 (universidad)
- @usergioarboleda (universidad)
- @centrodeidiomas_usa (universidad)
- @dani.masmella (compañero)
- @danireyes_6 (compañero)
- @jalopezfa (compañero)
- @jp.joya (compañero)
- @juanca_gallardo (compañero)
- @julian_rincon_18 (compañero)
- @maril0.0 (compañero)
- @miguel.flechas (compañero)
- @santiago_username (compañero)
- @afortizd (compañero)
- @imposible_is._nothing (compañero)
- @auronplay (YouTuber)

#### Franco ↔ Juan: 13 cuentas en común

Similar distribución con mayoría de compañeros universitarios:
- @gutierreztovar_jefferson
- @auronplay
- @nigg_.1
- @santigl_0016
- @usergioarboleda
- (Y otros compañeros de clase)

---

## Hallazgos Principales

### 1. Fuerte Cohesión Universitaria

Hallazgo más importante: El análisis demuestra que el entorno universitario es el principal nexo social entre las tres personas analizadas.

- 80% de las cuentas compartidas por todos son de la Universidad Sergio Arboleda
- ~94% de cuentas compartidas entre Andrés y Juan son compañeros de clase, familiares o del colegio
- La cuenta @usergioarboleda (oficial de la universidad) es seguida por los tres
- La página @confesiones.usergioarboleda es compartida, mostrando interés en la comunidad universitaria

### 2. Influencia del Entretenimiento Gaming Hispanohablante

Los únicos influencers compartidos son YouTubers/streamers de videojuegos en español:
- Auronplay: Streamer español de gaming y comedia
- ElRubiusOMG: YouTuber español de gaming
- Vegetta777: YouTuber español de Minecraft y gaming

### 3. Patrones de Comportamiento Social

Juan: El "conector social diverso"
- Mayor número de conexiones mutuas (111)
- Mayor número de seguidores (239)
- Sigue a más personas (328)
- Comportamiento más diverso: sigue cuentas más allá del círculo universitario, familiar y del colegio
- Rol: Hub social, probablemente líder de opinión en el grupo con intereses variados

Franco: El "selectivo"
- Menos conexiones totales (88 siguiendo, 44 seguidores)
- Mayor diversidad de intereses (51 tópicos)
- Rol: Usuario selectivo que sigue contenido específico de calidad

Andrés: El "conector cercano"
- Sigue muchas más personas de las que lo siguen (214 vs 77)
- Intereses más focalizados (32 tópicos)
- Las cuentas que sigue son principalmente compañeros de universidad, familiares y del colegio
- Rol: Mantiene conexiones con su círculo social cercano (universidad, familia, colegio)

### 4. Similitud Cultural y Generacional

Los 21 tópicos compartidos por todos revelan un perfil generacional claro:

- Gamers casuales (battle royale, survival)
- Interesados en fitness y gimnasio
- Amantes de mascotas
- Consumidores de contenido visual (memes, series, animación)
- Conscientes de moda y apariencia personal

### 5. Red Social Universitaria Dominante

El análisis de las conexiones compartidas muestra que:

La Universidad Sergio Arboleda funciona como el principal grafo social de conexión:
- Compañeros de clase son la mayoría de contactos compartidos
- El contenido universitario (confesiones, cuenta oficial) es relevante
- Las conexiones mutuas sugieren grupos de estudio o amistad universitaria

### 6. Diferencias en Patrones de Seguimiento

Andrés vs Juan vs Franco - Comportamientos contrastantes:

Andrés:
- Enfoque en círculo cercano: universidad, familia y colegio
- Red más homogénea centrada en relaciones personales directas
- Menor diversidad en tipos de cuentas seguidas

Juan:
- Mayor diversidad en cuentas seguidas 
- Va más allá del círculo universitario/familiar/escolar
- Sigue cuentas de diversos ámbitos e intereses
- Comportamiento más exploratorio en redes sociales

Franco:
- Enfoque mayormente en familia y colegio
- Menor numero de conexiones
- Menor diversidad en tipos de cuentas seguidas
---

## Conclusiones

### Conclusión Principal

El entorno universitario de la Universidad Sergio Arboleda es el factor determinante en las conexiones sociales compartidas entre Andrés, Franco y Juan.

### Conclusiones Específicas

1. Conexiones Universitarias Dominantes (80-94%)
   - La gran mayoría de cuentas compartidas corresponden a compañeros de clase y cuentas oficiales de la universidad
   - Solo 1 de cada 5 conexiones compartidas es de entretenimiento externo
   - Andrés muestra un patrón particularmente enfocado en universidad, familia y colegio

2. Perfil Cultural Cohesivo
   - Los tres comparten 21 tópicos de interés (deportes, gaming, moda, mascotas)
   - Consumen contenido de creadores hispanohablantes

3. Roles Sociales Diferenciados
   - Juan: Conector social con mayor influencia y diversidad en cuentas seguidas
   - Franco: Curador selectivo con intereses diversos
   - Andrés: Enfocado en círculo cercano 

4. Influencia Gaming Moderada
   - Aunque comparten interés en videojuegos, solo 3 creadores de contenido gaming son seguidos por múltiples personas
   - El gaming es un tema de conversación común pero no el nexo principal

5. Importancia de la Comunidad Universitaria
   - El grafo social se construye primariamente en el campus universitario
   - Las redes digitales reflejan las redes físicas del entorno académico

6. Comportamientos Diferenciados de Seguimiento
   - Andrés mantiene una red centrada en relaciones personales cercanas
   - Juan explora contenido más allá de su círculo inmediato
   - Franco mantiene una red centrada en relaciones personales cercanas
   - Esta diferencia muestra distintos usos de las redes sociales dentro del mismo grupo social

### Reflexión Final

Este análisis demuestra que, a pesar de vivir en la era digital con acceso global a contenido, las conexiones físicas y geográficas (universidad, familia, colegio) siguen siendo el factor más importante en la construcción de redes sociales.

Los datos confirman que compartimos más con quienes compartimos espacio físico que con quienes compartimos gustos digitales. Sin embargo, también revelan que existen diferencias individuales en cómo cada persona utiliza las redes sociales: algunos las usan principalmente para mantener conexiones cercanas (Andres, Franco), mientras que otros las utilizan también para explorar contenido diverso (Juan).

---

## Cómo Agregar Datos de Otra Persona

### Formato de nombres de archivos

Los archivos deben estar en la carpeta `data/` y seguir este patrón de nombres:

data/nombre_followers.json data/nombre_following.json data/nombre_topics.json

**Ejemplo:** Para agregar a una persona llamada "pepe":

data/pepe_followers.json data/pepe_following.json data/pepe_topics.json

Pasos para agregar una nueva persona
- Exporta los datos desde Instagram 
- Copia los 3 archivos JSON a la carpeta data/
- Renómbralos siguiendo el patrón: nombre_followers.json, nombre_following.json, nombre_topics.json
- Ejecuta: python generar_grafos_instagram.py
- El script detectará automáticamente la nueva persona y la incluirá en el análisis
- Importante: El nombre del archivo (el prefijo antes de _followers, _following o _topics) debe ser idéntico para los 3 archivos de cada persona.

## Archivos del Proyecto

### Código Fuente
- `generar_grafos_instagram.py` - Script principal para generar grafos
- `analizar_datos_sociales.py` - Script de análisis detallado

### Datos de Entrada
- `data/andres_followers.json`
- `data/andres_following.json`
- `data/andres_topics.json`
- `data/franco_followers.json`
- `data/franco_following.json`
- `data/franco_topics.json`
- `data/juan_followers.json`
- `data/juan_following.json`
- `data/juan_topics.json`

### Resultados
- `out/grafo_individual_andres.png`
- `out/grafo_individual_franco.png`
- `out/grafo_individual_juan.png`
- `out/grafo_unificado.png`
- `out/grafo_unificado.gexf`
- `out/grafo_interactivo.html`
- `out/conexiones_entre_personas.png`
- `out/centralidad_andres.csv`
- `out/centralidad_franco.csv`
- `out/centralidad_juan.csv`
- `out/matriz_similitud.csv`
- `out/entidades_compartidas.csv`
- `out/reporte_completo.txt`

---

## Cómo Ejecutar el Proyecto

### Requisitos
```bash
pip install networkx pandas matplotlib plotly
```

### Generar Grafos
```bash
python generar_grafos_instagram.py
```

### Generar Análisis Detallado
```bash
python analizar_datos_sociales.py
```

---
