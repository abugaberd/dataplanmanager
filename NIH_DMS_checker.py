# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tempfile
import streamlit as st
from streamlit.logger import get_logger
import replicate
import os
#from streamlit_app_utils import check_gpt_4, check_key_validity, create_temp_file, create_chat_model, token_limit, token_minimum

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="NIH DMS Plan Checker",
        page_icon="👋",
    )

    st.title("NIH Data Management & Sharing Plan Checker")

    input_method = st.radio("Select input method", ('Upload a document', 'Paste in text'))

    if input_method == 'Upload a document':
        uploaded_file = st.file_uploader("Upload a Data Management & Sharing plan to check", type=['txt', 'pdf', 'doc', 'docx'])

    if input_method == 'Paste in text':
        dms_text = st.text_input("Paste the text of your Data Management & Sharing plan to check")

    st.sidebar.markdown('# Made by: [David Abugaber](https://github.com/dabugaber_deloitte)')
    st.sidebar.markdown('# Git link: [Docsummarizer](https://github.com/abugaberd/dataplanmanager)')
    
    with st.sidebar:
      st.title('🦙💬 Llama 2 Chatbot')
      if 'REPLICATE_API_TOKEN' in st.secrets:
            st.success('API key already provided!', icon='✅')
            replicate_api = st.secrets['REPLICATE_API_TOKEN']
      else:
            replicate_api = st.text_input('Enter Replicate API token:', type='password')
            if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
                st.warning('Please enter your credentials!', icon='⚠️')
            else:
                st.success('Proceed to entering your prompt message!', icon='👉')
      os.environ['REPLICATE_API_TOKEN'] = replicate_api

      st.subheader('Models and parameters')
      selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
      if selected_model == 'Llama2-7B':
          llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
      elif selected_model == 'Llama2-13B':
          llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
      temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
      top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
      max_length = st.sidebar.slider('max_length', min_value=32, max_value=512, value=120, step=8)

    def generate_llama2_response(prompt_input):
      string_dialogue = "Here is a policy from a government agency, paired with a data management plan | GOVERNMENT POLICY: All plans must include: 1) Data Type: Describe the data to be managed, preserved, and shared, including: summary of the types/estimated amount of scientific data. Descriptions may indicate modality (e.g., imaging, genomic, mobile, survey), level of aggregation (e.g., individual, aggregated, summarized), and/or degree of data processing. Describe which scientific data will be preserved and shared. Provide rationale for these decisions based on ethical, legal, and technical factors. Include brief listing of metadata, other relevant data, and associated documentation (e.g., study protocols and data collection instruments) that will be made available. Indicate what specialized tools are needed to access/manipulate data. If applicable, specify whether tools are free, available from the marketplace, or only available from the research team. Indicate whether such tools are likely to remain available for as long as the data are available. 2) Standards: Indicate what standards will apply to data/metadata (i.e., formats, dictionaries, identifiers, definitions, unique identifiers, other documentation). 3) Data Preservation, Access, and Associated Timelines, including: Name of repositories where scientific data/metadata will be archived; How data will be findable/identifiable, i.e., via persistent unique identifiers or standard indexing tools; When data will be available and for how long. Data should be shared ASAP, and no later than time of an associated publication or end of performance period, whichever comes first. Data should be available for as long as would be useful. Identify any differences in timelines for different subsets of data. 4) Access, Distribution, or Reuse Considerations: Researchers should maximize the appropriate sharing of data. Describe applicable factors affecting subsequent access, distribution, or reuse of scientific data related to: Informed consent (e.g., disease-specific limitations, particular communities’ concerns); Privacy/confidentiality protections (i.e., de-identification, Certificates of Confidentiality, other protective measures) consistent with federal, Tribal, state, and local laws, regulations, and policies; Whether access to data derived from humans will be controlled (i.e., made available only after approval); Any restrictions imposed by federal, Tribal, or state laws, regulations, or policies, or existing/anticipated agreements (e.g., with third party funders, partners, HIPAA-covered, through licensing limitations); Any other considerations that limit extent of data sharing. 5) Oversight of Data Management and Sharing: Indicate how compliance with the Plan will be monitored and managed, frequency of oversight, and by whom (e.g., titles, roles). NOTE: Scientific data do not include laboratory notebooks, preliminary analyses, completed case report forms, drafts of scientific papers, plans for future research, peer reviews, communications with colleagues, or physical objects, such as laboratory specimens. | Determine whether the following data management plan adheres to the government policy, and explain why or why not. | DATA MANAGEMENT PLAN: "
      #for dict_message in st.session_state.messages:
      #    if dict_message["role"] == "user":
      #        string_dialogue += "User: " + dict_message["content"] + "\n\n"
      #    else:
      #        string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
      output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                            input={"prompt": f"{string_dialogue} {prompt_input} | Does this Data Management & Sharing plan follow the government policy? Why or why not?: ",
                                    "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
      return output

    if st.button('Check this DMS plan (click once and wait)'):
      if input_method == 'Upload a document':
          response = generate_llama2_response(uploaded_file)
          #st.markdown(summary, unsafe_allow_html=True)
          #os.unlink(temp_file_path)
          #process_summarize_button(uploaded_file, replicate_api)
          #process_summarize_button(uploaded_file, api_key, use_gpt_4, find_clusters)

      else:
          doc = dms_text
          response = generate_llama2_response(doc)

      placeholder = st.empty()
      full_response = ''
      for item in response:
        full_response += item
        placeholder.markdown(full_response)

      st.markdown(full_response[0], unsafe_allow_html=True)
          # process_summarize_button(doc, replicate_api)
          #process_summarize_button(doc, api_key, use_gpt_4, find_clusters, file=False)
    st.markdown('[Author email](mailto:dabugaber@deloitte.com)')

    
if __name__ == "__main__":
    run()
