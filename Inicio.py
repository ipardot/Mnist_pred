import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image, ImageColor
from streamlit_drawable_canvas import st_canvas
import os

st.set_page_config(
    page_title="Detector de Dígitos MNIST",
    page_icon="✍️",
    layout="wide"
)

# Mostrar versión en sidebar
with st.sidebar:
    st.write(f"**TensorFlow:** {tf.__version__}")
    st.write(f"**Keras:** {keras.__version__}")

    st.subheader("Propiedades del Tablero")

    # Canvas dimensions (moved to the top)
    st.subheader("Dimensiones del Tablero")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 500, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    # Drawing mode selector
    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    # Stroke width slider
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 15)

    # Stroke color picker
    stroke_color = st.color_picker("Color de trazo", "#FFFFFF")

    # Background color
    bg_color = st.color_picker("Color de fondo", "#000000")

st.title("✍️ Detección de Dígitos Escritos a Mano")
st.markdown("**Modelo CNN entrenado en Google Colab con MNIST**")

# Cargar modelo
@st.cache_resource
def load_mnist_model():
    """Carga el modelo MNIST desde archivo .keras"""
    
    # Buscar archivo del modelo
    model_files = ['mnist_model.keras', 'mnist_model.h5']
    
    for model_path in model_files:
        if os.path.exists(model_path):
            try:
                st.info(f"📂 Intentando cargar: {model_path}")
                model = keras.models.load_model(model_path)
                st.success(f"✅ Modelo cargado exitosamente desde: `{model_path}`")
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
st.write("### 🎨 Dibuja un dígito del 0 al 9")

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
    st.write("### 🎮 Controles")
    predict_btn = st.button("🔍 **Predecir**", type="primary", use_container_width=True)
    clear_btn = st.button("🗑️ Limpiar", use_container_width=True)
    
    if clear_btn:
        st.session_state.canvas_id += 1
        st.rerun()

# Predicción
if predict_btn:
    if canvas_result.image_data is not None:
        # Procesar imagen (funciona con cualquier color y tamaño de tablero)
        image_resized = preparar_imagen(canvas_result.image_data, bg_color)
        if image_resized is None:
            st.warning("⚠️ Por favor, dibuja un dígito primero")
        else:
            with st.spinner("🤔 Analizando..."):
                img_array = np.array(image_resized) / 255.0
                img_array = img_array.reshape(1, 28, 28, 1)
                
                # Predicción
                prediction = model.predict(img_array, verbose=0)
                digit = np.argmax(prediction)
                confidence = np.max(prediction) * 100
            
            # Resultados
            st.success(f"## 🎯 Dígito detectado: **{digit}**")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Predicción", digit)
            with col_m2:
                st.metric("Confianza", f"{confidence:.1f}%")
            with col_m3:
                alternative = np.argsort(prediction[0])[-2]
                st.metric("2ª opción", alternative)
            
            # Mostrar imágenes
            st.write("### 🖼️ Procesamiento")
            col_img1, col_img2 = st.columns(2)
            
            with col_img1:
                st.write("**Tu dibujo original:**")
                st.image(canvas_result.image_data, width=200)
            
            with col_img2:
                st.write("**Imagen procesada (28x28):**")
                st.image(image_resized, width=200)
            
            # Gráfico de probabilidades
            st.write("### 📊 Probabilidades por dígito")
            import pandas as pd
            prob_df = pd.DataFrame({
                'Dígito': [str(i) for i in range(10)],
                'Probabilidad (%)': prediction[0] * 100
            })
            st.bar_chart(prob_df.set_index('Dígito'))
            
            with st.expander("🔍 Ver detalles"):
                for i, prob in enumerate(prediction[0]):
                    emoji = "🎯" if i == digit else ""
                    st.write(f"{emoji} **Dígito {i}**: {prob*100:.2f}%")
    else:
        st.warning("⚠️ Por favor, dibuja un dígito en el canvas")

