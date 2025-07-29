import streamlit as st
from PIL import Image
import cv2 as cv
from PIL import Image
import numpy as np

st.set_page_config(
    layout='wide', 
    page_title='Editor de Imagens',
    page_icon='🖼️',
)

st.title('Editor de Imagens', anchor=False)

with st.container(border = True):
    st.subheader('Carregar Imagem', anchor=False)

    option = st.selectbox(
        label = '',
        label_visibility='collapsed',
        options = ('Via Upload', 'Via Câmera'),
    )

if option == 'Via Upload':
    col1, col2 = st.columns(2)
    
    with col2:
        with st.container(border = True):
            uploaded_image = st.file_uploader('Via upload', type=['jpg', 'jpeg', 'png'], accept_multiple_files=False)
        
    with col1:
        if uploaded_image is not None:
            with st.container(border = True):
                st.session_state.image_original = Image.open(uploaded_image).convert('L')
                st.session_state.image_edited = np.array(Image.open(uploaded_image).convert('L'))

                st.image(st.session_state.image_original, caption='Imagem Original - via upload', use_container_width=True)
elif option == 'Via Câmera':
    col1, col2 = st.columns(2)
    with col2:
        with st.container(border = True):
            camera_image = st.camera_input('', label_visibility='collapsed', disabled=False)
    with col1:
        with st.container(border = True):    
            if camera_image is not None:
                st.session_state.image_original = Image.open(camera_image).convert('L')
                st.session_state.image_edited = np.array(Image.open(camera_image).convert('L'))

                st.image(st.session_state.image_original, caption='Imagem Original - via câmera', use_container_width=True)


col1, col2 = st.columns(2)


def rotation(image_original = st.session_state.get('image_original', None), angle = 0):

    image_np = np.array(image_original)
    image_cv = cv.cvtColor(image_np, cv.COLOR_RGB2BGR)
    
    rows, cols = image_np.shape
        
    center = ((cols-1)/2.0, (rows-1)/2.0)
    scale = 1

    m = cv.getRotationMatrix2D(center, angle, scale)
    res = cv.warpAffine(image_cv, m, (cols, rows))

    return res


def resize(image, sx = 1, sy = 1):
    res = cv.resize(
                image, None, fx=sx, fy=sy, interpolation = cv.INTER_CUBIC
            ) 
    return res

def shear_H(image, c_h = st.session_state.get('shear_horizontal', 0), c_v = st.session_state.get('shear_vertical', 0)):
    
    rows, cols, _ = image.shape

    m = np.float32([[1, c_h, 0], [c_v, 1, 0], [0, 0, 1]])
    res = cv.warpPerspective(image, m, (cols, rows))

    return res

def brightness(image, brilho = 0):
    image = cv.add(image, brilho)
    return image

def contrast(image, contraste = 1):
    image = cv.divide(image, contraste)
    return image

def power_gamma(image, gamma):
    c = 255
    r = image / 255.0
    res = c * np.power(r, gamma)
    res = np.uint8(res)
    return res

def negative_effect(image, apply_effect = False):
    if apply_effect:
        image = cv.bitwise_not(image)
    return image

def transform():
    if 'image_original' in st.session_state:
        st.session_state.image_edited = rotation(angle = st.session_state.get('slider_rotacao', 0))
        st.session_state.image_edited = resize(image = st.session_state.get('image_edited', None), sx = st.session_state.get('resize_horizontal', 1), sy = st.session_state.get('resize_vertical', 1))
        st.session_state.image_edited = shear_H(image = st.session_state.get('image_edited', None), c_h = st.session_state.get('shear_horizontal', 0), c_v = st.session_state.get('shear_vertical', 0))
        st.session_state.image_edited = brightness(image = st.session_state.get('image_edited', None), brilho = st.session_state.get('slider_brilho', 0))
        st.session_state.image_edited = contrast(image = st.session_state.get('image_edited', None), contraste = st.session_state.get('slider_contraste', 1))
        st.session_state.image_edited = power_gamma(image = st.session_state.get('image_edited', None), gamma = st.session_state.get('slider_gama', 1.0))
        st.session_state.image_edited = negative_effect(image = st.session_state.get('image_edited', None), apply_effect = st.session_state.get('toggle_negativo', False))
        with col1:
            with st.container(border = True):      
                col1A, col1B = st.columns(2)
                with col1B:
                    st.image(st.session_state.image_edited, caption='Imagem Editada', use_container_width=True)
                with col1A:
                    st.image(st.session_state.image_original, caption='Imagem Original', use_container_width=True)

def reset_values():
    if 'image_original' in st.session_state:
        st.session_state.update({
            'slider_rotacao': 0,
            'resize_horizontal': 1.0,
            'resize_vertical': 1.0,
            'shear_horizontal': 0.0,
            'shear_vertical': 0.0,
            'slider_brilho': 0,
            'slider_contraste': 1.0,
            'slider_gama': 1.0,
            'toggle_negativo': False
        })
        transform()


with col2:
    with st.container(border = True):
        col2A, col2B = st.columns(2)

        with col2A:
            angulo = st.slider('Rotação (°)', 0, 360, 0, key = 'slider_rotacao', on_change=transform)
            
            col2A1, col2A2 = st.columns(2)

            with col2A1:
                sx = st.slider('Largura (%)', 0.1, 2.0, 1.0, step = 0.01, key = 'resize_horizontal', on_change=transform)
                c_v = st.slider('Cisalhamento Horizontal', -1.0, 1.0, 0.0, step=0.01, key = 'shear_horizontal', on_change=transform)
            with col2A2:
                sy = st.slider('Altura (%)', 0.1, 2.0, 1.0, step = 0.01, key = 'resize_vertical', on_change=transform)
                c_h = st.slider('Cisalhamento Vertical', -1.0, 1.0, 0.0, step=0.01, key = 'shear_vertical', on_change=transform)
            
            if 'image_edited' in st.session_state:
                _, buffer = cv.imencode('.jpg', st.session_state.image_edited)
                st.download_button(
                    label='📥 Baixar imagem',
                    data=buffer.tobytes(),
                    file_name='imagem_editada.jpg',
                    mime='image/jpeg',
                    disabled=False,
                )
            else:
                st.download_button(
                    label='📥 Baixar imagem',
                    data='nothing',
                    file_name='imagem_editada.jpg',
                    mime='image/jpeg',
                    disabled=True,
                )

        with col2B:
            brilho = st.slider('Brilho', -255, 255, 0, step=1, key = 'slider_brilho', on_change=transform)
            constraste = st.slider('Contraste', 0.01, 20.0, 1.0, step=0.01, key = 'slider_contraste', on_change=transform)
            gamma = st.slider('Gama', 0.0, 20.0, 1.0, step=0.01, key = 'slider_gama', on_change=transform)
            negativo = st.toggle('Efeito Negativo', key = 'toggle_negativo', on_change=transform)

            st.button("Reset", type="secondary", on_click=reset_values)
