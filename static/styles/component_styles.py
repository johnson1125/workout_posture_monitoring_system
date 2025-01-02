from static.styles.app_styles import *

# Navbar styles
nav_bar_style = f"""
background-color: {secondary_bg_color};
color: {primary_text_color};
height:70px;
padding: 20px;
border-radius: 15px;
text-align: center; 
box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); 
display:flex;
align-items:center;
justify-content:center;
"""

title_style = f"""
text-align:center;  
color:#EDEDED;
border-bottom:solid 1px {divider_color};
"""

subtitle_style = f"""
text-align:center;
font-size:20px;  
color:#EDEDED;
font-weight:bold;
padding-bottom:5px;
border-bottom:solid 1px {divider_color};
"""

primary_btn_style = f"""
 button{{
    background:{primary_btn_color};
    height:50px;
    }}
    p{{
    color:{primary_btn_text_color};
    font-weight:bold;
    }}
    button:hover{{
    background:{primary_btn_hover_color};
    border-color:{primary_btn_border_color} !important;
    border-width:{primary_btn_hover_border_width};
    }}
    button:not(:active):focus{{
    background:{primary_btn_focus_color} ;
    border-color:{primary_btn_border_color} !important;
    border-width:{primary_btn_focus_border_width};
    }}  
"""

tabs_style = f"""
   .stTabs [role="tablist"] {{
        border-radius: 10px;
        padding: 5px;
        display: flex;
        justify-content: space-around;
    }}

    /* Style individual tabs */
    .stTabs [role="tab"] {{
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s ease, color 0.3s ease;
    }}
     .stTabs [role="tab"] p {{
        font-size: 20px;
        font-weight: bold;
    }}


"""

text_container_with_label_styles = f"""
    .container{{
    text-align: center;
    border: 1px solid {container_border_color};
    background:{secondary_bg_color};
    color:{primary_text_color};
    padding: 10px; 
    border-radius: 5px; 
    }}

"""

feedback_container_styles = f"""
    .feedback_container{{
    text-align: center;
    font-size:20px;
    border: 1px solid {container_border_color};
    background:{secondary_bg_color};
    color:{primary_text_color};
    padding: 10px; 
    border-radius: 5px; 
    }}

"""

summary_item_container_styles = f"""
    .summary_item_container{{
    width:100%;
    display:flex;
    flex-direction:column;
    
    }}
    
    .summary_container_label_row{{
    width:100%;
    display:flex;
    flex-direction:row;
    }}
    
    .summary_container_text_row{{
    width:100%;
    display:flex;
    flex-direction:row;
    margin-bottom:20px;
    }}
    
    .summary_container_label{{
    color:{secondary_text_color};
    flex:1;
    text-align:start;
    font-size:15px;
    }}
    
    .summary_container_text{{
    color:{primary_text_color};
    text-align:start;
    font-size:18px;
    flex:1;
    }}
    
    [class*="st-key-view_summary_btn"]{{
    {primary_btn_style}
    }}
    

"""

summary_details_item_container_styles = f"""
    .summary_details_item_container{{
        width:100%;
        display:flex;
        flex-direction:column;
        
    }}
        
    .summary_details_container_sect1{{
        display:flex;
        flex-direction:row;
        margin-bottom:20px;
        border-bottom:solid 1px {secondary_text_color};
    }}
    
    .summary_details_container_col{{
        flex:1;
    }}
    
    .summary_details_container_row{{
         margin-bottom:20px;
    }}
    
    .summary_details_container_label{{
        color:{secondary_text_color};
        text-align:center;
        font-size:15px;
    }}
    
    .summary_details_container_text{{
        color:{primary_text_color};
        text-align:center;
        font-size:18px;
    
    }}
    
    .summary_details_container_sect2{{
        margin-top:20px;
        margin-bottom:20px;
        border: 1px solid {secondary_text_color};
        border-radius: 5px; 
        padding:20px;
    }}
    
    .summary_details_container_feedback_text{{
        text-align:center;
        color:{primary_text_color};
        
    }}
    
    [class*="st-key-view_rep_video_btn"],[class*="st-key-view_set_video_btn"]{{
    {primary_btn_style}
    }}
"""

set_video_playback_styles= f"""
    .set_video_playback_row{{
         margin-bottom:20px;
    }}
    
    .set_video_playback_label{{
        color:{secondary_text_color};
        text-align:center;
        font-size:15px;
    }}
    
    
    .set_video_playback_text{{
        text-align:center;
        color:{primary_text_color};
        
    }}
    
    .set_video_playback_sect{{
        border: 1px solid {secondary_text_color};
        border-radius: 5px; 
        padding:20px;
    }}
"""

rep_video_list_item_container_styles = f"""
     .rep_video_list_item_container{{
    width:100%;
    display:flex;
    flex-direction:column;
    
    }}
    
    .rep_video_list_item_container_label_row{{
    width:100%;
    display:flex;
    flex-direction:row;
    }}
    
    .rep_video_list_item_container_text_row{{
    width:100%;
    display:flex;
    flex-direction:row;
    margin-bottom:20px;
    }}
    
    .rep_video_list_item_container_label{{
    color:{secondary_text_color};
    flex:1;
    text-align:start;
    font-size:15px;
    }}
    
    .rep_video_list_item_container_text{{
    color:{primary_text_color};
    text-align:start;
    font-size:18px;
    flex:1;
    }}
    
    [class*="st-key-view_rep_video_btn_"]{{
    {primary_btn_style}
    }}
    

"""

rep_video_playback_styles = f"""
    .rep_video_playback_row{{
         margin-bottom:20px;
    }}

    .rep_video_playback_label{{
        color:{secondary_text_color};
        text-align:center;
        font-size:15px;
    }}


    .rep_video_playback_text{{
        text-align:center;
        color:{primary_text_color};

    }}

    .rep_video_playback_sect{{
        border: 1px solid {secondary_text_color};
        border-radius: 5px; 
        padding:20px;
    }}
"""

master_page_styles = f"""
.navbar{{
    {nav_bar_style}
    }}

.title{{
    {title_style}
    }}
"""
