from time import sleep

import streamlit as st
from streamlit.components.v1 import html
from streamlit_js_eval import streamlit_js_eval

if "svg_height" not in st.session_state:
    st.session_state["svg_height"] = 200

if "previous_mermaid" not in st.session_state:
    st.session_state["previous_mermaid"] = ""


def mermaid(code: str) -> None:
    html(
        f"""
        <pre class="mermaid">
            {code}
        </pre>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height=st.session_state["svg_height"] + 50,
    )


selection = st.selectbox("Choose example", ["Simple", "Class Diagram", "Flowchart"])

if selection == "Simple":
    code = """
    graph LR
        A --> B --> C
    """
elif selection == "Class Diagram":
    code = """
    classDiagram
        Animal <|-- Duck
        Animal <|-- Fish
        Animal <|-- Zebra
        Animal : +int age

        class Duck{
            +String beakColor
            +swim()
            +quack()
        }

        class Fish{
            -int sizeInFeet
            -canEat()
        }

        class Zebra{
            +bool is_wild
            +run()
        }
    """
else:
    code = """
    graph TD
        A[Christmas] -->|Get money| B(Go shopping)
        B --> C{Let me think}
        C -->|One| D[Laptop]
        C -->|Two| E[iPhone]
        C -->|Three| F[fa:fa-car Car]
    """

mermaid(code)

if code != st.session_state["previous_mermaid"]:
    st.session_state["previous_mermaid"] = code
    sleep(1)
    streamlit_js_eval(
        js_expressions='parent.document.getElementsByTagName("iframe")[0].contentDocument.getElementsByClassName("mermaid")[0].getElementsByTagName("svg")[0].getBBox().height',
        key="svg_height",
    )