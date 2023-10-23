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
    st.sidebar.markdown('# Git link: [Docsummarizer](https://github.com/e-johnstonn/docsummarizer)')
    
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
      string_dialogue = "Here is a government policy regarding Data Management & Sharing plans | NIH recommends addressing all Elements described below: 1. Data Type: Briefly describe the scientific data to be managed, preserved, and shared, including: A general summary of the types and estimated amount of scientific data to be generated and/or used in the research. Describe data in general terms that address the type and amount/size of scientific data expected to be collected and used in the project (e.g., 256-channel EEG data and fMRI images from ~50 research participants). Descriptions may indicate the data modality (e.g., imaging, genomic, mobile, survey), level of aggregation (e.g., individual, aggregated, summarized), and/or the degree of data processing that has occurred (i.e., how raw or processed the data will be). A description of which scientific data from the project will be preserved and shared. NIH does not anticipate that researchers will preserve and share all scientific data generated in a study. Researchers should decide which scientific data to preserve and share based on ethical, legal, and technical factors that may affect the extent to which scientific data are preserved and shared. Provide the rationale for these decisions. A brief listing of the metadata, other relevant data, and any associated documentation (e.g., study protocols and data collection instruments) that will be made accessible to facilitate interpretation of the scientific data. 2. Related Tools, Software and/or Code: An indication of whether specialized tools are needed to access or manipulate shared scientific data to support replication or reuse, and name(s) of the needed tool(s) and software. If applicable, specify how needed tools can be accessed, (e.g., open source and freely available, generally available for a fee in the marketplace, available only from the research team) and, if known, whether such tools are likely to remain available for as long as the scientific data remain available. 3. Standards: An indication of what standards will be applied to the scientific data and associated metadata (i.e., data formats, data dictionaries, data identifiers, definitions, unique identifiers, and other data documentation). While many scientific fields have developed and adopted common data standards, others have not. In such cases, the Plan may indicate that no consensus data standards exist for the scientific data and metadata to be generated, preserved, and shared. 4. Data Preservation, Access, and Associated Timelines: Plans and timelines for data preservation and access, including: The name of the repository(ies) where scientific data and metadata arising from the project will be archived. NIH has provided additional information to assist in selecting suitable repositories for scientific data resulting from funded research (NOT-OD-21-016). How the scientific data will be findable and identifiable, i.e., via a persistent unique identifier or other standard indexing tools. When the scientific data will be made available to other users (i.e., the larger research community, institutions, and/or the broader public) and for how long. NIH encourages scientific data be shared as soon as possible, and no later than time of an associated publication or end of the performance period, whichever comes first. Researchers are encouraged to consider relevant requirements and expectations (e.g., data repository policies, award record retention requirements, journal policies) as guidance for the minimum time frame scientific data should be made available. NIH encourages researchers to make scientific data available for as long as they anticipate it being useful for the larger research community, institutions, and/or the broader public. Identify any differences in timelines for different subsets of scientific data to be shared. 5. Access, Distribution, or Reuse Considerations: NIH expects that in drafting Plans, researchers maximize the appropriate sharing of scientific data generated from NIH-funded or conducted research, consistent with privacy, security, informed consent, and proprietary issues. Describe any applicable factors affecting subsequent access, distribution, or reuse of scientific data related to: Informed consent (e.g., disease-specific limitations, particular communities’ concerns). Privacy and confidentiality protections (i.e., de-identification, Certificates of Confidentiality, and other protective measures) consistent with applicable federal, Tribal, state, and local laws, regulations, and policies. Whether access to scientific data derived from humans will be controlled (i.e., made available by a data repository only after approval). Any restrictions imposed by federal, Tribal, or state laws, regulations, or policies, or existing or anticipated agreements (e.g., with third party funders, with partners, with Health Insurance Portability and Accountability Act (HIPAA) covered entities that provide Protected Health Information under a data use agreement, through licensing limitations attached to materials needed to conduct the research). Any other considerations that may limit the extent of data sharing. 6. Oversight of Data Management and Sharing: Indicate how compliance with the Plan will be monitored and managed, frequency of oversight, and by whom (e.g., titles, roles). NOTE: Scientific data is the recorded factual material commonly accepted in the scientific community as of sufficient quality to validate and replicate research findings, regardless of whether the data are used to support scholarly publications. Scientific data do not include laboratory notebooks, preliminary analyses, completed case report forms, drafts of scientific papers, plans for future research, peer reviews, communications with colleagues, or physical objects, such as laboratory specimens. | Now read the following Data Management & Sharing plan and determine whether it follows the government policy: "
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
