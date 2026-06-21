import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io, os, base64, uuid
from streamlit_drawable_canvas import st_canvas

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def pdf_page_to_image(pdf_bytes, page_num=0, zoom=1.5):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img, doc.page_count

def show_pdf_annotator(user_id):
    st.markdown("<h1>📄 PDF Annotator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888'>Open a PDF, navigate pages, and annotate with drawings, ticks, crosses, and highlights.</p>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if not uploaded:
        st.info("Upload a PDF to start annotating.")
        # show instructions
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, [
            ("✏️","Draw Freely","Use freehand drawing to underline or circle important text"),
            ("✅","Tick & Cross","Mark correct/incorrect answers or important points"),
            ("💾","Save Annotation","Export your annotated page as PNG image"),
        ]):
            with col:
                st.markdown(f"""
                <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:10px;padding:16px;text-align:center'>
                    <div style='font-size:2rem'>{icon}</div>
                    <b style='color:#6C63FF'>{title}</b>
                    <p style='color:#888;font-size:0.85rem;margin-top:8px'>{desc}</p>
                </div>""", unsafe_allow_html=True)
        return

    pdf_bytes = uploaded.read()

    # Store pdf in session
    if 'pdf_bytes' not in st.session_state or st.session_state.get('pdf_name') != uploaded.name:
        st.session_state['pdf_bytes'] = pdf_bytes
        st.session_state['pdf_name'] = uploaded.name
        st.session_state['pdf_page'] = 0

    _, total_pages = pdf_page_to_image(pdf_bytes, 0)

    # Controls
    col1, col2, col3, col4 = st.columns([1,1,2,2])
    with col1:
        if st.button("⬅ Prev") and st.session_state['pdf_page'] > 0:
            st.session_state['pdf_page'] -= 1
            st.rerun()
    with col2:
        if st.button("Next ➡") and st.session_state['pdf_page'] < total_pages - 1:
            st.session_state['pdf_page'] += 1
            st.rerun()
    with col3:
        page_num = st.number_input("Page", min_value=1, max_value=total_pages,
                                    value=st.session_state['pdf_page'] + 1) - 1
        if page_num != st.session_state['pdf_page']:
            st.session_state['pdf_page'] = page_num
            st.rerun()
    with col4:
        st.markdown(f"<p style='color:#888;padding-top:28px'>Page {st.session_state['pdf_page']+1} of {total_pages}</p>", unsafe_allow_html=True)

    current_page = st.session_state['pdf_page']
    img, _ = pdf_page_to_image(pdf_bytes, current_page, zoom=1.5)

    # Annotation toolbar
    st.markdown("#### 🖊️ Annotation Tools")
    tc1, tc2, tc3, tc4, tc5 = st.columns(5)
    with tc1:
        tool = st.selectbox("Tool", ["freedraw", "line", "rect", "circle", "transform"], label_visibility="collapsed")
    with tc2:
        stroke_color = st.color_picker("Color", "#FF0000")
    with tc3:
        stroke_width = st.slider("Width", 1, 20, 3)
    with tc4:
        # Quick stamp buttons
        if st.button("✅ Tick"):
            st.session_state['stamp'] = 'tick'
        if st.button("❌ Cross"):
            st.session_state['stamp'] = 'cross'
    with tc5:
        opacity = st.slider("Opacity", 0.1, 1.0, 0.8)
        fill_color = st.color_picker("Fill", "#FF000000") if tool in ["rect","circle"] else "rgba(0,0,0,0)"

    img_w, img_h = img.size
    canvas_w = min(img_w, 900)
    canvas_h = int(img_h * canvas_w / img_w)

    # Convert PIL to base64 for canvas background
    buf = io.BytesIO()
    img_resized = img.resize((canvas_w, canvas_h))
    img_resized.save(buf, format="PNG")
    bg_img = Image.open(io.BytesIO(buf.getvalue()))

    # Handle stamp tool — overlay tick/cross as initial drawing data
    initial_drawing = st.session_state.get('canvas_drawing', {"version":"4.4.0","objects":[]})

    canvas_result = st_canvas(
        fill_color=fill_color if tool in ["rect","circle"] else "rgba(0,0,0,0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=bg_img,
        update_streamlit=True,
        height=canvas_h,
        width=canvas_w,
        drawing_mode=tool,
        initial_drawing=initial_drawing,
        key=f"canvas_{current_page}_{uploaded.name}",
    )

    if canvas_result.json_data:
        st.session_state['canvas_drawing'] = canvas_result.json_data

    # Quick stamp: add tick or cross text annotation
    stamp = st.session_state.get('stamp')
    if stamp:
        st.info(f"Click on canvas to place {stamp}. (Tip: use freedraw for custom marks)")
        st.session_state.pop('stamp', None)

    # Save annotation
    st.markdown("---")
    sc1, sc2 = st.columns(2)
    with sc1:
        if st.button("💾 Save Annotated Page as PNG", width='stretch'):
            if canvas_result.image_data is not None:
                import numpy as np
                from PIL import Image as PILImage
                img_array = canvas_result.image_data
                ann_img = PILImage.fromarray(img_array.astype('uint8'), 'RGBA')
                # Composite annotation over pdf page
                bg = img_resized.convert("RGBA")
                composite = PILImage.alpha_composite(bg, ann_img)
                save_path = os.path.join(UPLOAD_DIR, f"annotated_{uuid.uuid4()}.png")
                composite.save(save_path)
                # Offer download
                buf2 = io.BytesIO()
                composite.save(buf2, format="PNG")
                st.download_button("⬇️ Download PNG", buf2.getvalue(),
                                   file_name=f"annotated_page_{current_page+1}.png",
                                   mime="image/png", width='stretch')
                st.success(f"Saved!")
            else:
                st.warning("Nothing to save yet. Draw something first!")

    with sc2:
        if st.button("🗑️ Clear Annotations", width='stretch'):
            st.session_state.pop('canvas_drawing', None)
            st.rerun()

    # Add to vocab note
    st.markdown("---")
    st.markdown("#### 📝 Quick Add to Notes")
    note_text = st.text_area("Add a note about this PDF page", placeholder="Write vocabulary or concepts from this page...")
    if st.button("Add to Today's Notes"):
        from utils.note_utils import add_note, get_note_by_date
        from datetime import date
        today = date.today()
        existing = get_note_by_date(user_id, today)
        prev = existing.content if existing else ""
        new_content = prev + f"\n\n📄 PDF: {uploaded.name} (Page {current_page+1}):\n{note_text}"
        add_note(user_id, today,
                 existing.words_learned if existing else 0,
                 existing.time_spent if existing else 0,
                 existing.topic if existing else f"PDF: {uploaded.name}",
                 new_content,
                 existing.mood_rating if existing else 3)
        st.success("Added to today's notes!")
