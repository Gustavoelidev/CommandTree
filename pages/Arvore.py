import os
import streamlit as st
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.save_tree_feature import check_ip, get_lists_of_commands, to_compare, models


st.set_page_config(
    page_title="[TEST] Arvore de comandos",
)