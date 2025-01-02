import os

import streamlit as st
from streamlit_extras.stylable_container import stylable_container

from utils import utils
from static.styles.app_styles import *

def top_navbar():
    st.markdown("""
    <div class="navbar">
    <h2>Workout Monitoring System</h1>
    </div>
    """, unsafe_allow_html=True)
    empty(20)


def title(text):
    st.markdown(f"""
    <div class="title">
    <h3>{text}</h3>
    </div>
    """, unsafe_allow_html=True)
    empty(30)


def subtitle(text):
    st.markdown(f"""
    <div class="subtitle">
    {text}
    </div>
    """, unsafe_allow_html=True)
    empty(20)


def empty(height):
    st.markdown(f"""
    <div style='height:{str(height)}px;'></div>
    """, unsafe_allow_html=True)

def text_container_with_label(placeholder, label, text):
    placeholder.markdown(f"""
    <div class="label">{label}</div>
    <div class="container">{text}</div>
    """, unsafe_allow_html=True)

def feedback_container(placeholder, text):
    placeholder.markdown(f"""
       <div class="feedback_container">{text}</div>
       """, unsafe_allow_html=True)

def summary_item_container(entry):
    _, col1, _ = st.columns([1, 5, 1])
    with col1:
        with stylable_container(key="summary_card_container", css_styles=f"""
            {{background:{secondary_bg_color};
            padding: 20px; 
            border-radius: 5px; 
            border: 1px solid {container_border_color};
            
            }}
        
        """):
            _, col1, col2, _ = st.columns([1, 5, 1, 1], vertical_alignment="center")
            with col1:
                st.markdown(f"""
                <div class="summary_item_container">
                <div class="summary_container_label_row">
                <div class="summary_container_label">Exercise ID</div>
                <div class="summary_container_label">Workout Time</div>
                </div>
                
                <div class="summary_container_text_row">
                <div class="summary_container_text">{entry["Exercise ID"]}</div>
                <div class="summary_container_text">{entry["Workout Time"]}</div>
                    
                </div>
                <div class="summary_container_label_row">
                <div class="summary_container_label">Exercise DateTime</div>
                <div class="summary_container_label">Set</div>
                    
                </div> <div class="summary_container_text_row">
                <div class="summary_container_text">{entry["Exercise DateTime"]}</div>
                <div class="summary_container_text">{entry["Set"]}</div>        
                </div>
                </div>
            
                """, unsafe_allow_html=True)

            with col2:
                if st.button(label="View", key="view_summary_btn_" + entry["Exercise ID"], use_container_width=True):
                    st.session_state.selected_summary = entry["Exercise ID"]
                    st.session_state.selected_summary_exercise = utils.extract_exercise_key(st.session_state.selected_summary)

                    st.switch_page("pages/exercise_summary_details.py")

def summary_details_item_container(entry):
    _, col1, _ = st.columns([1, 5, 1])
    with col1:
        with stylable_container(key="summary_card_container", css_styles=f"""
            {{background:{secondary_bg_color};
            padding: 20px; 
            border-radius: 5px; 
            border: 1px solid {container_border_color};

            }}

        """):
            _, col1, _ = st.columns([1, 5, 1], vertical_alignment="center")
            with col1:
                mistakes_html = ""
                for mistake, mistake_value in entry["Mistake Counts"].items():
                    mistakes_html += f"""
                                    <div class="summary_details_container_row">
                                   <div class="summary_details_container_label">{mistake}</div>
                                   <div class="summary_details_container_text">{mistake_value}</div>
                                   </div>

                                   """
                st.markdown(f"""
                                    <div class="summary_details_item_container">
                                    <div class="summary_details_container_sect1">
                                    <div class="summary_details_container_col">
                                    <div class="summary_details_container_row">
                                    <div class="summary_details_container_label">Set</div>
                                    <div class="summary_details_container_text">{entry["Set Number"]}</div>
                                    </div>
                                    <div class="summary_container_row">
                                    <div class="summary_details_container_label">Workout Time</div>
                                    <div class="summary_details_container_text">{entry["Workout Time"]}</div>
                                    </div>   
                                    </div>
                                    <div class="summary_details_container_col">
                                    <div class="summary_details_container_row">
                                    <div class="summary_details_container_label">Total Reps</div>
                                    <div class="summary_details_container_text">{entry["Total Reps"]}</div>
                                    </div>
                                    <div class="summary_details_container_row">
                                    <div class="summary_details_container_label">Correct Reps</div>
                                    <div class="summary_details_container_text">{entry["Correct Reps"]}</div>
                                    </div>
                                    <div class="summary_details_container_row">
                                    <div class="summary_details_container_label">Total Mistakes</div>
                                    <div class="summary_details_container_text">{entry["Total Mistakes"]}</div>
                                    </div>
                                    </div> 
                                    <div class="summary_details_container_col">
                                    {mistakes_html}
                                    </div>   
                                    </div>                           
                                    </div>

                               """, unsafe_allow_html=True)



            _, col1, col2, _ = st.columns([1, 3, 3, 1], vertical_alignment="center")
            with col1:
                set_id = f'{entry["Exercise ID"]}_set_{entry["Set Number"]}'
                if st.button(label="View Set Video",
                             key=f"view_set_video_btn_{set_id}",
                             use_container_width=True):
                    st.session_state.selected_set = set_id
                    st.session_state.selected_summary_exercise = utils.extract_exercise_key(
                        st.session_state.selected_summary)
                    st.session_state.set_analysis = entry
                    st.switch_page("pages/exercise_set_video_playback.py")
            with col2:
                if st.button(label="View Rep Video",
                             key=f"view_rep_video_btn_{set_id}",
                             use_container_width=True):
                    st.session_state.selected_set = set_id
                    st.session_state.selected_summary_exercise = utils.extract_exercise_key(
                        st.session_state.selected_summary)
                    st.switch_page("pages/exercise_rep_video_list.py")

def set_video_playback(video,entry):
    with stylable_container(key="set_video_playback_container", css_styles=f"""
                {{background:{secondary_bg_color};
                width:80%;
                display:flex;
                align-self:center;
                margin-top:20px;
                padding: 40px; 
                border-radius: 5px; 
                border: 1px solid {container_border_color};

                }}

            """):
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown(f"""
                            <div class="set_video_playback_col">
                            <div class="set_video_playback_row">
                            <div class="set_video_playback_label">Set</div>
                            <div class="set_video_playback_text">{entry["Set Number"]}</div>
                            </div>
                            <div class="set_video_playback_row">
                            <div class="set_video_playback_label">Workout Time</div>
                            <div class="set_video_playback_text">{entry["Workout Time"]}</div>
                            </div>
                            <div class="set_video_playback_row">
                            <div class="set_video_playback_label">Total Reps</div>
                            <div class="set_video_playback_text">{entry["Total Reps"]}</div>
                            </div>
                            <div class="set_video_playback_row">
                            <div class="set_video_playback_label">Correct Reps</div>
                            <div class="set_video_playback_text">{entry["Correct Reps"]}</div>
                            </div>
                            <div class="set_video_playback_row">
                            <div class="set_video_playback_label">Total Mistakes</div>
                            <div class="set_video_playback_text">{entry["Total Mistakes"]}</div>
                            </div>   
                            </div>
                                                        
                           """, unsafe_allow_html=True)

        with col2:
            _,col1,_ = st.columns([1,3,1])
            with col1:
                st.video(video)

        with col3:
            mistakes_html = ""
            for mistake, mistake_value in entry["Mistake Counts"].items():
                mistakes_html += f"""
                                <div class="set_video_playback_row">
                                <div class="set_video_playback_label">{mistake}</div>
                                <div class="set_video_playback_text">{mistake_value}</div>
                                </div>
                                
                                """

            st.markdown(f"""
                                <div class="summary_details_container_col">
                                {mistakes_html}
                                </div>   
                        """,unsafe_allow_html=True
            )



        _,col1,_ = st.columns([1,5,1])
        with col1:
            comments_html = ""
            for comment in entry["Comments"]:
                comments_html += f"""<p>{comment}</p>"""
            recommendations_html = ""
            for recommendation in entry["Recommendations"]:
                recommendations_html += f"""<p>{recommendation}</p>"""

            st.markdown(f"""
                                <div class="set_video_playback_sect">
                                <div class="set_video_playback_text">
                                {comments_html}
                                </div>
                                <div class="set_video_playback_text">
                                {recommendations_html}
                                </div>           
                                </div>    
                         """,unsafe_allow_html=True
            )

def rep_video_list_item_container(entry,set_id):
    _, col1, _ = st.columns([1, 5, 1])
    with col1:
        with stylable_container(key="rep_video_list_item_container", css_styles=f"""
               {{background:{secondary_bg_color};
               padding: 20px; 
               border-radius: 5px; 
               border: 1px solid {container_border_color};

               }}

           """):
            _, col1, col2, _ = st.columns([1, 5, 1, 1], vertical_alignment="center")
            with col1:
                st.markdown(f"""
                   <div class="rep_video_list_item_container">
                   <div class="rep_video_list_item_container_label_row">
                   <div class="rep_video_list_item_container_label">Rep</div>
                   <div class="rep_video_list_item_container_label">Result</div>
                   </div>

                   <div class="rep_video_list_item_container_text_row">
                   <div class="rep_video_list_item_container_text">{entry["rep_index"]}</div>
                   <div class="rep_video_list_item_container_text">{utils.remove_underscores_and_capitalize(entry["result"])}</div>
                   </div>
  
                   """, unsafe_allow_html=True)

            with col2:
                rep_id = f'{set_id}_rep_{entry["rep_index"]}'
                if st.button(label="View", key="view_rep_video_btn_" + rep_id, use_container_width=True):
                    st.session_state.selected_rep = rep_id
                    st.session_state.selected_summary_exercise =utils.extract_exercise_key(
                        st.session_state.selected_summary)
                    st.session_state.rep_record = entry
                    st.switch_page("pages/exercise_rep_video_playback.py")

def rep_video_playback(video, entry):
    with stylable_container(key="rep_video_playback_container", css_styles=f"""
                {{background:{secondary_bg_color};
                width:80%;
                display:flex;
                align-self:center;
                margin-top:20px;
                padding: 40px; 
                border-radius: 5px; 
                border: 1px solid {container_border_color};

                }}

            """):
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown(f"""
                            <div class="rep_video_playback_col">
                            <div class="rep_video_playback_row">
                            <div class="rep_video_playback_label">Rep</div>
                            <div class="rep_video_playback_text">{entry["rep_index"]}</div>
                            </div>
                            <div class="rep_video_playback_row">
                            <div class="rep_video_playback_label">Result</div>
                            <div class="rep_video_playback_text">{utils.remove_underscores_and_capitalize(entry["result"])}</div>
                            </div>
                            </div>

                           """, unsafe_allow_html=True)

        with col2:
            _, col1, _ = st.columns([1, 3, 1])
            with col1:
                st.video(video)

        _, col1, _ = st.columns([1, 5, 1])
        with col1:

            st.markdown(f"""
                                <div class="rep_video_playback_sect">
                                <div class="rep_video_playback_text">
                                {entry["feedback"]}
                                </div>        
                                </div>    
                         """, unsafe_allow_html=True
                        )




