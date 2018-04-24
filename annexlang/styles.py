import yaml

class StyleCustom(yaml.YAMLObject):
    yaml_tag = "!style-custom"
    style = ''
        
class StyleDefault(yaml.YAMLObject):
    yaml_tag = "!style-default"
    style = r"""
    % basics
    every node/.style={font=\sffamily\tiny},
    annex_lifeline/.style={draw=black!30},
    annex_matrix_node/.style={},
    annex_matrix_dummy_height/.style={},
    % default style used below
    line/.style={draw=yellow!50!green},
    % groups
    annex_group_box/.style={draw=black!50,dashed,rounded corners=1ex},
    annex_group_title_placeholder/.style={},
    annex_condensed_box/.style={draw=blue,rounded corners=1ex,inner sep=0},
    % start/end parties
    annex_start_party_box/.style={fill=white,draw,rounded corners=0.3ex,anchor=center,inner sep=0.5ex,minimum height=1.7em,inner sep=1.5mm},
    annex_end_party_box/.style={annex_start_party_box,scale=0.7},
    % individual steps
    annex_arrow_text/.style={font=\sffamily\tiny},
    annex_http_request/.style={-Latex,line,draw=purple},
    annex_http_response/.style={-Latex[open],line,draw=purple},
    annex_action/.style={fill=white,inner sep=0ex,minimum height=1.5em},
    annex_open_window/.style={->,line,dashed},
    annex_script_action_box/.style={annex_action,anchor=center},
    annex_script_action_arrow/.style={->,line},
    annex_script_action_arrow_reversed/.style={<-,line},
    annex_open_window_start_party_box/.style={annex_start_party_box},
    annex_open_window_start_party_arrow/.style={->,line,dashed},
    """

class StyleDebug(yaml.YAMLObject):
    yaml_tag = "!style-debug"

    style = """
    annex_group_box/.style={fill=cyan!20},
    annex_matrix_node/.style={draw=red},
    annex_matrix_dummy_height/.style={draw=green},
    annex_group_title_placeholder/.style={draw=pink}
    annex_script_action_box/.style={draw=yellow},
    annex_script_action_arrow/.style={->,draw=yellow},

    """
