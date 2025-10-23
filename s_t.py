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

# Paleta Gótica (Estilo Bloodborne):
# Fondo: #0A0A0A (Negro profundo)
# Texto Principal: #F5F5DC (Hueso/Papiro)
# Acento/Sangre: #8B0000 (Rojo intenso)
# Metal/Piedra: #6B5B3E (Bronce oscuro/Caoba)

gothic_css = """
<style>
/* Fondo general y fuente serif dramática */
body {
    background-color: #0A0A0A;
    color: #F5F5DC;
    font-family: 'Georgia', serif;
}
.stApp {
    background-color: #0A0A0A;
    color: #F5F5DC;
}

/* Título Principal: Cincelado y Dramático */
h1 {
    color: #8B0000; /* Rojo sangre */
    text-shadow: 2px 2px 5px #000000;
    font-size: 2.8em;
    border-bottom: 5px double #6B5B3E; /* Borde doble color bronce */
    padding-bottom: 10px;
    margin-bottom: 30px;
    text-align: center;
    letter-spacing: 2px;
}

/* Subtítulos: Menos prominentes, color de metal */
h2, h3 {
    color: #D4D4D4;
    font-family: 'Georgia', serif;
}

/* Sidebar: Fondo de cámara oscura con bordes intrincados */
[data-testid="stSidebar"] {
    background-color: #1A1A1A;
    color: #F5F5DC;
    border-right: 3px solid #6B5B3E;
    box-shadow: 0 0 15px rgba(107, 91, 62, 0.5), inset 0 0 5px rgba(0, 0, 0, 0.8);
}

/* Elementos de entrada (Runas): Fondo oscuro, borde metálico */
.stTextInput > div > div > input, .stTextArea > div > textarea, .stSelectbox > div > div {
    background-color: #1A1A1A;
    color: #F5F5DC;
    border: 2px solid #6B5B3E;
    border-radius: 4px;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.5);
}

/* Botones Streamlit (Sellar Traducción): Botones tipo Relicario */
.stButton > button {
    background-color: #444444; /* Base metálica */
    color: #F5F5DC;
    border: 3px solid #8B0000; /* Borde rojo sangre */
    border-radius: 8px;
    padding: 12px 25px;
    font-weight: bold;
    box-shadow: 6px 6px 10px #000000, inset 0 0 10px rgba(255, 255, 255, 0.1);
    transition: background-color 0.3s, box-shadow 0.3s, transform 0.1s;
}

.stButton > button:hover {
    background-color: #8B0000; /* Hover a rojo intenso */
    color: white;
    box-shadow: 8px 8px 15px #000000;
    transform: translateY(-2px);
}

/* Botón de Bokeh (Sello del Audio): Rojo, Metal y Sombra pesada */
.bk-root .bk-btn {
    background-color: #8B0000 !important; /* Fuerza el color rojo */
    color: white !important;
    border: 3px solid #6B5B3E !important; /* Borde metálico */
    font-weight: bold !important;
    box-shadow: 6px 6px 10px #000000 !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: background-color 0.3s, box-shadow 0.3s;
}
.bk-root .bk-btn:hover {
    background-color: #6B5B3E !important; /* Color de metal oxidado al pasar el ratón */
}
</style>
"""
st.markdown(gothic_css, unsafe_allow_html=True)

st.title("El Grimorio de las Lenguas")
st.subheader("Dicta tu conjuro. Recibirás el eco en otra lengua.")

# --- 2. Imagen Gótica (Placeholder de un Cuervo) ---
# Imagen: Un cuervo, una lámpara de aceite en una noche oscura o un libro antiguo.
image_url = "https://placehold.co/650x250/1A1A1A/8B0000?text=Antigua+Linterna+y+Manuscritos+Prohibidos"
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

# --- Separador Gótico ---
st.markdown(
    """
    <div style="text-align: center; margin: 30px 0;">
        <span style="font-size: 2.5em; color: #6B5B3E; display: inline-block; transform: rotate(90deg);">
            &#10010;
        </span>
        <span style="font-size: 2.5em; color: #8B0000; margin: 0 10px;">
            &#9888;
        </span>
        <span style="font-size: 2.5em; color: #6B5B3E; display: inline-block; transform: rotate(-90deg);">
            &#10010;
        </span>
    </div>
    """, 
    unsafe_allow_html=True
)
# -------------------------

if result:
    if "GET_TEXT" in result:
        text_from_speech = result.get("GET_TEXT")
        if text_from_speech == "INVOCANDO...":
            st.info("🎙️ El Oráculo te escucha. Habla ahora...")
        elif text_from_speech == "No se detectó voz clara.":
            st.error("❌ El Oráculo no ha percibido tu voz. Inténtalo de nuevo.")
        else:
            st.markdown(f"**📜 Mensaje Original (Revelado):** *{text_from_speech}*")

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
           


        
    


