import streamlit as st
from PIL import Image
import io
import numpy as np

st.set_page_config(page_title="DTF Alpha Cleaner Pro", layout="wide")

# CSS compatible con todas las versiones
st.markdown("""
<style>
.black-box {
    background-color: #000000;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #444;
    text-align: center;
    margin-bottom: 10px;
}
.black-box img {
    background-color: #000000 !important;
    display: block;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

if 'key' not in st.session_state:
    st.session_state.key = 0

def restart():
    st.session_state.key += 1
    # ✅ CORRECCIÓN CLAVE: Streamlit 1.57.0 usa st.rerun() (NO experimental_rerun)
    st.rerun()  # ¡Este es el cambio que resuelve tu error!

st.title("DTF Alpha Cleaner Pro")
st.write("Limpia bordes suaves de IA para una impresión DTF perfecta.")

uploaded_file = st.file_uploader(
    "Sube tu diseño (PNG con transparencia)", 
    type=["png"], 
    key=f"uploader_{st.session_state.key}"
)

if uploaded_file is not None:
    with st.sidebar:
        st.header("Ajustes")
        threshold = st.slider(
            "Umbral de limpieza", 
            0, 
            255, 
            128,
            help="Valores por debajo de este umbral se eliminarán"
        )
        
        st.info("Rojo = Areas a eliminar | Negro = Transparente | Colores = Conservados")
        
        if st.button("Cargar otra imagen"):
            restart()

    # ✅ CORRECCIÓN CLAVE: Evita getdata() obsoleto usando numpy
    img = Image.open(uploaded_file).convert("RGBA")
    img_array = np.array(img)
    
    # Procesamiento con numpy (más rápido y compatible)
    r, g, b, a = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2], img_array[:, :, 3]
    
    # Crear máscara para píxeles semitransparentes
    mask = (a > 0) & (a < threshold)
    
    # Preparar imágenes de vista previa y limpia
    preview_array = img_array.copy()
    clean_array = img_array.copy()
    
    # Marcar en rojo en la vista previa
    preview_array[mask, 0] = 255  # Rojo
    preview_array[mask, 1] = 0
    preview_array[mask, 2] = 0
    preview_array[mask, 3] = 255  # Opacidad total para ver el rojo
    
    # Eliminar en la versión limpia
    clean_array[mask, 3] = 0  # Transparente
    
    # Conservar opacidad total en áreas sólidas
    clean_array[a >= threshold, 3] = 255
    
    img_preview = Image.fromarray(preview_array)
    img_clean = Image.fromarray(clean_array)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. ORIGINAL")
        st.image(img, width=300)

    with col2:
        st.subheader("2. RESULTADO (FONDO NEGRO)")
        st.markdown('<div class="black-box">', unsafe_allow_html=True)
        st.image(img_preview, width=300)
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("ROJO = Areas eliminadas")

    st.markdown("---")
    
    buf = io.BytesIO()
    img_clean.save(buf, format="PNG")
    
    st.download_button(
        label="DESCARGAR PNG LIMPIO",
        data=buf.getvalue(),
        file_name="dtf_limpio.png",
        mime="image/png"
    )
    
    st.success("Imagen lista para impresión DTF")

else:
    st.info("""
    **Instrucciones:**
    1. Sube un PNG con transparencia
    2. Ajusta el umbral según tus necesidades
    3. Descarga el resultado
    
    *Umbral recomendado:*
    - Sombras suaves: 50-80
    - Bordes definidos: 150+
    """)
