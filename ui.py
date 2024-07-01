import streamlit as st
from streamlit_drawable_canvas import st_canvas
from helpers import get_image_description, generate_realistic_image
from PIL import Image



STYLES = [
    "Photorealistic", "Oil painting", "Watercolor", "Digital art",
    "Pencil sketch", "Anime", "Comic book", "Abstract",
    "Impressionist", "Pop art"
]

def skeleton_loader():
    return """
    <div class="skeleton-loader"></div>
    <style>
        .skeleton-loader {
            width: 512px;
            height: 512px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        @keyframes loading {
            0% {
                background-position: 200% 0;
            }
            100% {
                background-position: -200% 0;
            }
        }
    </style>
    """

def bordered_placeholder():
    return """
    <div class="bordered-placeholder"></div>
    <style>
        .bordered-placeholder {
            width: 512px;
            height: 512px;
            border: 2px dashed #cccccc;
        }
    </style>
    """

def main():
    st.set_page_config(layout="wide", page_title="Sketch to Realistic Image Converter")

    st.title("Sketch to Realistic Image Converter")

    if 'canvas_result' not in st.session_state:
        st.session_state.canvas_result = None

    col_input, col_controls, col_output = st.columns([2, 1, 2])

    with col_controls:
        st.subheader("")
        selected_style = st.selectbox("Select output style", STYLES)
        generate_button = st.button("Generate Image", use_container_width=True)
        loading_placeholder = st.empty()

    with col_input:
        st.subheader("Draw your sketch")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=512,
            width=512,
            drawing_mode="freedraw",
            key="canvas",
        )
        
        if canvas_result.image_data is not None:
            st.session_state.canvas_result = canvas_result

    with col_output:
        st.subheader("Generated Realistic Image")
        output_placeholder = st.empty()
        if 'realistic_image' in st.session_state:
            output_placeholder.image(st.session_state.realistic_image, caption="Generated Realistic Image", width=512)
        else:
            output_placeholder.markdown(bordered_placeholder(), unsafe_allow_html=True)

    if generate_button:
        if st.session_state.canvas_result is not None and st.session_state.canvas_result.image_data is not None:
            loading_placeholder.text("Generating...")
            
            # Show the skeleton loader
            output_placeholder.markdown(skeleton_loader(), unsafe_allow_html=True)
            
            img = Image.fromarray(st.session_state.canvas_result.image_data.astype('uint8'), 'RGBA')
            img = img.convert('RGB')
            
            base_description = get_image_description(img)
            st.session_state.description = f"{base_description}, Style: {selected_style}"
            
            try:
                realistic_image = generate_realistic_image(img, st.session_state.description)
                st.session_state.realistic_image = realistic_image
                output_placeholder.image(realistic_image, caption="Generated Realistic Image", width=512)
                loading_placeholder.empty()
                st.success("Image generated successfully!")
            except Exception as e:
                loading_placeholder.empty()
                output_placeholder.markdown(bordered_placeholder(), unsafe_allow_html=True)
                st.error(f"Error generating image: {str(e)}")
        else:
            st.warning("Please draw something on the canvas first!")

    if 'description' in st.session_state:
        with st.expander("Image Description"):
            st.write(st.session_state.description)

if __name__ == "__main__":
    main()