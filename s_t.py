import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import time
import glob
from gtts import gTTS
from googletrans import Translator

# --- 1. Configuración de la Página y Estilo Gótico (CSS Injection) ---
st.set_page_config(
    page_title="El Oráculo de la Voz",
    page_icon="🦇",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Paleta Gótica:
# Fondo: #121212 (Negro profundo)
# Texto Principal: #EAE0D0 (Papiro antiguo)
# Acento/Fuego: #A93226 (Rojo sangre)
# Borde/Metal: #5D4037 (Marrón oscuro/Caoba)

gothic_css = """
<style>
/* Fondo general y fuente serif dramática */
body {
    background-color: #121212;
    color: #EAE0D0;
    font-family: 'Times New Roman', Times, serif;
}
.stApp {
    background-color: #121212;
    color: #EAE0D0;
}

/* Título Principal: Dramático y con sombra */
h1 {
    color: #A93226; /* Rojo de acento */
    text-shadow: 3px 3px 5px #000000;
    font-size: 2.5em;
    border-bottom: 2px solid #5D4037;
    padding-bottom: 10px;
    margin-bottom: 30px;
    text-align: center;
}

/* Subtítulos: Menos prominentes, color de texto */
h2, h3 {
    color: #C9C9C9;
    font-family: 'Georgia', serif;
}

/* Sidebar: Fondo de madera oscura */
[data-testid="stSidebar"] {
    background-color: #333333;
    color: #EAE0D0;
    border-right: 3px solid #5D4037;
}

/* Elementos de entrada (Selectboxes, Textareas): Fondo oscuro */
.stTextInput > div > div > input, .stTextArea > div > textarea, .stSelectbox > div > div {
    background-color: #2c2c2c;
    color: #EAE0D0;
    border: 1px solid #5D4037;
    border-radius: 4px;
}

/* Botones Streamlit: Botones tipo Sello/Metal */
.stButton > button {
    background-color: #5D4037;
    color: #EAE0D0;
    border: 2px solid #A93226;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    box-shadow: 4px 4px 6px #000000;
    transition: background-color 0.3s, box-shadow 0.3s, transform 0.1s;
}

.stButton > button:hover {
    background-color: #A93226; /* Hover rojo intenso */
    color: white;
    box-shadow: 6px 6px 10px #000000;
    transform: translateY(-2px);
}

/* Botón de Bokeh (Speech-to-Text): */
.bk-root .bk-btn {
    background-color: #A93226 !important; /* Fuerza el color rojo */
    color: white !important;
    border: 2px solid #5D4037 !important;
    font-weight: bold !important;
    box-shadow: 4px 4px 6px #000000 !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: background-color 0.3s, box-shadow 0.3s;
}
.bk-root .bk-btn:hover {
    background-color: #5D4037 !important; 
}
</style>
"""
st.markdown(gothic_css, unsafe_allow_html=True)

st.title("El Grimorio de las Lenguas")
st.subheader("Dicta tu conjuro. Recibirás el eco en otra lengua.")

# --- 2. Imagen Gótica (Placeholder de un Cuervo) ---
# Imagen: Un cuervo o un manuscrito antiguo sobre un fondo oscuro.
image_url = "https://placehold.co/650x250/2c2c2c/A93226?text=El+Cuervo+de+los+Idiomas"
st.image(image_url, caption="Símbolo de la sabiduría y el misterio.", use_column_width=True)

with st.sidebar:
    st.subheader("El Oráculo de la Voz.")
    st.write(
        "Para invocar la traducción, pulsa el **Sello del Audio** y pronuncia tu mensaje. "
        "Cuando el cuervo te escuche, el texto aparecerá, y podrás sellar tu conversión."
    )
    st.markdown("---")


# --- 3. Funcionalidad Speech-to-Text con Estilo ---
st.write("Pulsa el Sello del Audio para dictar tu mandato:")

# El botón Bokeh para STT
stt_button = Button(label=" Sello del Audio 🦇", width=300, height=50)

# CustomJS para el reconocimiento de voz
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false; // Queremos una frase, no una conversación continua
    recognition.interimResults = false;
    
    // Almacenamiento temporal para que el usuario sepa que está grabando
    document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: "INVOCANDO..."}));

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        } else {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: "No se detectó voz clara."}));
        }
    }
    recognition.start();
    """
))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        text_from_speech = result.get("GET_TEXT")
        if text_from_speech == "INVOCANDO...":
            st.info("🎙️ El Oráculo te escucha. Habla ahora...")
        elif text_from_speech == "No se detectó voz clara.":
            st.error("❌ El Oráculo no ha percibido tu voz. Inténtalo de nuevo.")
        else:
            st.markdown(f"**📜 Mensaje Original:** *{text_from_speech}*")

    try:
        os.makedirs("temp", exist_ok=True)
    except:
        pass
    
    # --- 4. Configuración de Traducción ---
    
    translator = Translator()
    text = str(result.get("GET_TEXT"))
    
    # Mapeo de idiomas
    lang_map = {
        "Inglés (English)": "en", 
        "Español (Spanish)": "es", 
        "Mandarín (Chinese)": "zh-cn", 
        "Japonés (Japanese)": "ja", 
        "Coreano (Korean)": "ko",
        "Bengalí (Bengali)": "bn"
    }

    st.markdown("---")
    st.subheader("Selección del Grimorio")

    col1, col2 = st.columns(2)
    
    with col1:
        in_lang_name = st.selectbox(
            "Lengua de la Fuente (Input)",
            list(lang_map.keys()),
        )
        input_language = lang_map[in_lang_name]

    with col2:
        out_lang_name = st.selectbox(
            "Lengua del Destino (Output)",
            list(lang_map.keys()),
            index=1 # Default a Español
        )
        output_language = lang_map[out_lang_name]
    
    # Selección del Acento (tld)
    english_accent = st.selectbox(
        "Ritual del Acento (Solo afecta al inglés/español)",
        (
            "Predeterminado",
            "España (es)",
            "México (com.mx)",
            "Reino Unido (co.uk)",
            "Estados Unidos (com)",
            "Australia (com.au)",
        ),
    )
    
    tld_map = {
        "Predeterminado": "com",
        "España (es)": "es",
        "México (com.mx)": "com.mx",
        "Reino Unido (co.uk)": "co.uk",
        "Estados Unidos (com)": "com",
        "Australia (com.au)": "com.au",
    }
    tld = tld_map[english_accent]
    
    # Función de conversión y traducción
    def text_to_speech(input_language, output_language, text, tld):
        """Traduce el texto y luego lo convierte a audio."""
        if not text or text == "INVOCANDO..." or text == "No se detectó voz clara.":
            return None, "Error: Texto no válido para traducir."
            
        try:
            translation = translator.translate(text, src=input_language, dest=output_language)
            trans_text = translation.text
            
            # gTTS utiliza el idioma de salida, pero el tld es para el acento
            tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
            
            safe_name = "".join(c for c in text[0:30] if c.isalnum() or c.isspace()).replace(" ", "_")
            if not safe_name: safe_name = "conjuro_traducido"
            file_path = f"temp/{safe_name}.mp3"
            
            tts.save(file_path)
            return file_path, trans_text
            
        except Exception as e:
            st.error(f"Fallo en la traducción o conversión: {e}")
            return None, f"Error en la operación: {e}"
    
    
    display_output_text = st.checkbox("Revelar el texto traducido", value=True)
    
    if st.button("🔥 Sellar la Traducción (Convertir a Audio)"):
        if text == "INVOCANDO..." or text == "No se detectó voz clara." or not text:
            st.error("Aún no tienes un mensaje válido del Oráculo. Pulsa el botón del Sello primero.")
        else:
            with st.spinner('Grabando el eco de la traducción en el éter...'):
                file_path, output_text = text_to_speech(input_language, output_language, text, tld)
            
            if file_path and os.path.exists(file_path):
                audio_file = open(file_path, "rb")
                audio_bytes = audio_file.read()
                
                st.success("✨ ¡El conjuro ha sido traducido y grabado!")
                
                st.markdown(f"## 🎧 Eco del Destino:")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
            
                if display_output_text:
                    st.markdown(f"## 📜 El Manuscrito Revelado:")
                    st.markdown(f"### *{output_text}*")
            
            else:
                st.error("No se pudo completar el ritual de traducción y audio.")

    # --- 5. Limpieza de Archivos Temporales ---
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            try:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
            except Exception:
                pass

    remove_files(7)
           


        
    


