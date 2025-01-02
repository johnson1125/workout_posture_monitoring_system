from static.styles.component_styles import *

css = f"""
<style>
{master_page_styles}

div[data-testid="stElementContainer"]:has(div[data-testid="stMarkdownContainer"] audio.audio_player) {{
    display: none !important;
}}
    
{text_container_with_label_styles}

{feedback_container_styles}
</style>
"""
