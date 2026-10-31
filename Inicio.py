import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image, ImageColor
from streamlit_drawable_canvas import st_canvas
import os

st.set_page_config(
    page_title="Aprendo los Números",
    page_icon="✏️",
    layout="wide"
)

# Mostrar versión en sidebar
with st.sidebar:
    st.write(f"**TensorFlow:** {tf.__version__}")
    st.write(f"**Keras:** {keras.__version__}")

    st.subheader("🎨 Mi pizarra")

    # Canvas dimensions (moved to the top)
    st.subheader("📏 Tamaño de la pizarra")
    canvas_width = st.slider("Ancho de la pizarra", 300, 700, 500, 50)
    canvas_height = st.slider("Alto de la pizarra", 200, 600, 300, 50)

    # Drawing mode selector
    drawing_mode = st.selectbox(
        "✏️ ¿Con qué quieres escribir?",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    # Stroke width slider
    stroke_width = st.slider('Grosor del lápiz', 1, 30, 15)

    # Stroke color picker
    stroke_color = st.color_picker("Color del lápiz", "#FFFFFF")

    # Background color
    bg_color = st.color_picker("Color de la pizarra", "#000000")

# ------------------------------------------------------------------
# TEMA "APRENDO LOS NÚMEROS" (solo estilos CSS; la lógica y los inputs no cambian)
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Nunito:wght@400;600;700&display=swap');

:root{
  --papel:#fbf7ee;
  --renglon:#e4ecf5;
  --azul:#3b82c4;
  --azul-oscuro:#24598c;
  --amarillo:#ffc93c;
  --coral:#ff6b6b;
  --verde:#4caf7a;
  --morado:#8e6cc9;
  --tinta:#2d3142;
}

/* Fondo: hoja de cuaderno con renglones suaves */
.stApp{
  background:
    repeating-linear-gradient(to bottom, transparent 0 31px, var(--renglon) 31px 32px),
    var(--papel);
  background-attachment: fixed;
}
header[data-testid="stHeader"]{ background: transparent; }

/* Panel central: hoja blanca con borde de colores */
[data-testid="stMainBlockContainer"], .block-container{
  background:
    linear-gradient(90deg, var(--coral) 0 25%, var(--amarillo) 25% 50%, var(--verde) 50% 75%, var(--azul) 75% 100%) top / 100% 10px no-repeat,
    #ffffff;
  border-radius:24px;
  box-shadow:0 18px 40px rgba(45,49,66,.10);
  margin-top:2rem;
  margin-bottom:4rem;
  padding:2rem 2.4rem 2.4rem !important;
  max-width:1100px;
}
@media (max-width:640px){
  [data-testid="stMainBlockContainer"], .block-container{
    padding:1.4rem 1.1rem 1.8rem !important;
  }
}

/* Encabezado */
.ninos-tag{
  display:inline-block;
  font-family:'Nunito', sans-serif;
  font-weight:700; font-size:.8rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--azul-oscuro);
  background:#e3eefa;
  padding:.3rem .8rem; border-radius:999px;
}
.ninos-title{
  font-family:'Baloo 2', sans-serif;
  font-weight:800; font-size:2.8rem; line-height:1.05;
  color:var(--tinta);
  margin:.7rem 0 .5rem;
}
.ninos-title span{ color:var(--coral); }
.ninos-sub{
  font-family:'Nunito', sans-serif;
  font-size:1.1rem; line-height:1.55;
  color:#5c6070;
  max-width:640px;
}
.ninos-numeros{ display:flex; flex-wrap:wrap; gap:.45rem; margin:1.1rem 0 .4rem; }
.ninos-numeros span{
  display:inline-flex; align-items:center; justify-content:center;
  width:2.3rem; height:2.3rem; border-radius:12px;
  font-family:'Baloo 2', sans-serif; font-weight:800; font-size:1.3rem; color:#1a1a1a;
}
.ninos-numeros span:nth-child(5n+1){ background:#ffc2c2; }
.ninos-numeros span:nth-child(5n+2){ background:#ffe08a; }
.ninos-numeros span:nth-child(5n+3){ background:#b5e3c6; }
.ninos-numeros span:nth-child(5n+4){ background:#b9d6f2; }
.ninos-numeros span:nth-child(5n+5){ background:#d8c9f0; }
@media (max-width:640px){
  .ninos-title{ font-size:2.1rem; }
}

/* Títulos y textos del contenido */
h2, h3{
  font-family:'Baloo 2', sans-serif !important;
  font-weight:800 !important;
  color:var(--azul-oscuro) !important;
}
h1 a, h2 a, h3 a{ display:none !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li{
  font-family:'Nunito', sans-serif;
  color:var(--tinta);
}

/* Resultados: números grandes y amigables */
[data-testid="stMetric"]{
  background:var(--papel);
  border-radius:18px;
  padding:.9rem 1rem;
}
[data-testid="stMetricLabel"] p{ font-weight:700; color:#5c6070; }
[data-testid="stMetricValue"]{
  font-family:'Baloo 2', sans-serif;
  font-weight:800;
  color:var(--coral);
}

/* Barra lateral: amarillo suave */
section[data-testid="stSidebar"]{
  background:#fff6dc;
  border-right:4px solid var(--amarillo);
}
section[data-testid="stSidebar"] h3{ font-size:1.15rem !important; }
/* Textos sobre fondos claros: siempre en negro (también si Streamlit usa el tema oscuro) */
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] label,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="caption"],
.stApp [data-testid="stSliderThumbValue"],
.stApp [data-testid="stSliderTickBarMin"],
.stApp [data-testid="stSliderTickBarMax"],
.stApp [data-testid="stFileUploaderFile"] *,
.stApp [data-testid="stAlert"] [data-testid="stMarkdownContainer"] *{
  color:#1a1a1a !important;
}
.stApp .vega-embed text{ fill:#1a1a1a !important; }

/* Botones: conservan los colores originales de Streamlit (contraste) */
.stApp button [data-testid="stMarkdownContainer"],
.stApp button [data-testid="stMarkdownContainer"] *,
.stApp button [data-testid="stMarkdownContainer"] p{
  color:inherit !important;
  font-family:inherit !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<span class="ninos-tag">✏️ Aprendo jugando</span>
<div class="ninos-title">¡Escribe tus <span>números</span>!</div>
<div class="ninos-sub">Escribe un número del 0 al 9 en la pizarra y pulsa <b>Revisar</b>. El profe robot te dirá qué número ve: si es el que querías escribir, ¡lo hiciste muy bien!</div>
<div class="ninos-numeros"><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span></div>
""", unsafe_allow_html=True)

# Cargar modelo
@st.cache_resource
def load_mnist_model():
    """Carga el modelo MNIST desde archivo .keras"""
    
    # Buscar archivo del modelo
    model_files = ['mnist_model.keras', 'mnist_model.h5']
    
    for model_path in model_files:
        if os.path.exists(model_path):
            try:
                st.info(f"📂 Despertando al profe robot ({model_path})...")
                model = keras.models.load_model(model_path)
                st.success("🤖 ¡El profe robot está listo para revisar tus números!")
                return model
            except Exception as e:
                st.error(f"❌ Error al cargar {model_path}: {str(e)}")
                continue
    
    # Si no se encuentra el modelo
    st.error("❌ No se encontró ningún modelo")
    st.info("""
    **Instrucciones:**
    1. Entrena el modelo en Google Colab
    2. Descarga `mnist_model.keras`
    3. Súbelo a la raíz de tu repositorio
    4. Reinicia la aplicación
    """)
    st.stop()

# Cargar modelo
model = load_mnist_model()

def preparar_imagen(image_data, bg_color):
    """Convierte el dibujo al formato MNIST: dígito blanco sobre fondo negro,
    recortado, centrado y escalado a 28x28 sin deformarlo.
    Devuelve None si el tablero está vacío."""
    rgba = image_data.astype("float32")
    fondo = np.array(ImageColor.getrgb(bg_color)[:3], dtype="float32")

    # Qué tanto se diferencia cada píxel del color de fondo (0 = fondo)
    diferencia = np.abs(rgba[:, :, :3] - fondo).max(axis=2)
    trazo = diferencia * (rgba[:, :, 3] / 255.0)  # píxeles transparentes = fondo

    filas, columnas = np.where(trazo > 30)
    if len(filas) == 0:
        return None

    # Recortar el dígito y normalizar el contraste
    recorte = trazo[filas.min():filas.max() + 1, columnas.min():columnas.max() + 1]
    recorte = recorte / recorte.max() * 255

    # Escalar el lado más largo a 20 px (como MNIST), manteniendo la proporción
    alto, ancho = recorte.shape
    escala = 20 / max(alto, ancho)
    nuevo_ancho = max(1, round(ancho * escala))
    nuevo_alto = max(1, round(alto * escala))
    digito = Image.fromarray(recorte.astype("uint8")).resize(
        (nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS
    )

    # Volver a llevar el trazo al máximo brillo (los trazos delgados quedan tenues al reducir)
    arreglo = np.array(digito, dtype="float32")
    arreglo = np.clip(arreglo / arreglo.max() * 255, 0, 255)
    digito = Image.fromarray(arreglo.astype("uint8"))

    # Centrar en un lienzo negro de 28x28
    imagen = Image.new("L", (28, 28), 0)
    imagen.paste(digito, ((28 - nuevo_ancho) // 2, (28 - nuevo_alto) // 2))
    return imagen

# Interfaz
st.write("### ✏️ Escribe un número del 0 al 9")

col1, col2 = st.columns([2, 1])

# Contador para reiniciar el tablero al pulsar "Limpiar"
if "canvas_id" not in st.session_state:
    st.session_state.canvas_id = 0

with col1:
    # Create a canvas component with dynamic key
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=canvas_height,
        width=canvas_width,
        drawing_mode=drawing_mode,
        key=f"canvas_{canvas_width}_{canvas_height}_{st.session_state.canvas_id}",  # Dynamic key based on dimensions
    )

with col2:
    st.write("### 👇 ¿Terminaste?")
    predict_btn = st.button("✅ **¡Revisar mi número!**", type="primary", use_container_width=True)
    clear_btn = st.button("🧽 Borrar y volver a intentar", use_container_width=True)
    
    if clear_btn:
        st.session_state.canvas_id += 1
        st.rerun()

# Predicción
if predict_btn:
    if canvas_result.image_data is not None:
        # Procesar imagen (funciona con cualquier color y tamaño de tablero)
        image_resized = preparar_imagen(canvas_result.image_data, bg_color)
        if image_resized is None:
            st.warning("✏️ ¡Primero escribe un número en la pizarra!")
        else:
            with st.spinner("🤔 El profe robot está mirando tu número..."):
                img_array = np.array(image_resized) / 255.0
                img_array = img_array.reshape(1, 28, 28, 1)
                
                # Predicción
                prediction = model.predict(img_array, verbose=0)
                digit = np.argmax(prediction)
                confidence = np.max(prediction) * 100
            
            # Resultados
            st.success(f"## 🌟 ¡Veo el número **{digit}**!\n\n¿Era el que querías escribir? ¡Muy bien hecho! Si no, bórralo e inténtalo otra vez.")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Escribiste el", digit)
            with col_m2:
                st.metric("Qué tan claro se ve", f"{confidence:.1f}%")
            with col_m3:
                alternative = np.argsort(prediction[0])[-2]
                st.metric("También se parece al", alternative)
            
            # Mostrar imágenes
            st.write("### 🔍 Así lo vio el profe robot")
            col_img1, col_img2 = st.columns(2)
            
            with col_img1:
                st.write("**Tu número:**")
                st.image(canvas_result.image_data, width=200)
            
            with col_img2:
                st.write("**Como lo ve el robot (28x28):**")
                st.image(image_resized, width=200)
            
            # Gráfico de probabilidades
            st.write("### 📊 ¿A qué número se parece más?")
            import pandas as pd
            prob_df = pd.DataFrame({
                'Dígito': [str(i) for i in range(10)],
                'Probabilidad (%)': prediction[0] * 100
            })
            st.bar_chart(prob_df.set_index('Dígito'))
            
            with st.expander("🔍 Ver todos los números"):
                for i, prob in enumerate(prediction[0]):
                    emoji = "🎯" if i == digit else ""
                    st.write(f"{emoji} **Número {i}**: {prob*100:.2f}%")
    else:
        st.warning("✏️ ¡Primero escribe un número en la pizarra!")

