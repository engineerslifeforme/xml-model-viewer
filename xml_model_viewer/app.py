from pathlib import Path

import streamlit as st

from bs4 import BeautifulSoup

XML_FILE = Path('text.xml')

""" # XML Model Viewer"""

if st.button('Refresh'):
    pass

soup = BeautifulSoup(XML_FILE.read_text(), 'html.parser')

attribute_name = st.text_input("Attribute Name", value='xmi:id')
attribute_value = st.text_input("Attribute Value", value='ABCD')

results = soup.find_all(attrs={attribute_name: attribute_value})

st.markdown(f"Found {len(results)} results")

result = results[0]

relationship_types = [
    'type',
    'realizes',
]

def gid(node):
    return node.get('xmi:id')

def get_relationships(node):
    relationships = []
    node_id = gid(node)
    for relate in relationship_types:
        node_relate = node.get(relate)
        if node_relate is not None:
            relationships.extend([
                {
                    'source': node_id,
                    'destination': gid(r),
                    'type': f"{relate}_out",
                    'source_node': node,
                    'destination_node': r,
                } for r in soup.find_all(attrs={"xmi:id": node_relate})
            ])
        relationships.extend([
            {
                'source': gid(r),
                'destination': node_id,
                'type': f"{relate}_in",
                'source_node': r,
                'destination_node': node,
            } for r in soup.find_all(attrs={relate: node_id})
        ])
    return relationships

def iterative_relationships(node):
    relationships = get_relationships(node)
    ignore_list = [gid(node)]
    while True:
        not_processed = [e['source_node'] for e in relationships if e['source'] not in ignore_list] +\
                        [e['destination_node'] for e in relationships if e['destination'] not in ignore_list]
        for unprocessed_node in not_processed:
            relationships.extend(get_relationships(unprocessed_node))
            ignore_list.append(gid(unprocessed_node))
        if len(not_processed) == 0:
            break
    return relationships

st.write(iterative_relationships(result))
