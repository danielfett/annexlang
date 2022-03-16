import yaml


class StyleCustom(yaml.YAMLObject):
    yaml_tag = "!style-custom"
    style = ''


class StyleDefault(yaml.YAMLObject):
    yaml_tag = "!style-default"
    style = r"""
    % basics
    every node/.style={font=\sffamily\tiny, align=center},
    annex_lifeline/.style={draw=black!30},
    annex_matrix_node/.style={},
    annex_matrix_dummy_height/.style={},
    % default style used below
    line/.style={draw=yellow!50!green},
    seperatorline/.style={draw=blue},
    % groups
    annex_group_box/.style={draw=black!50,dashed,rounded corners=1ex},
    annex_group_title_placeholder/.style={},
    annex_condensed_box/.style={draw=blue,rounded corners=1ex,inner sep=1pt},
    % start/end parties
    annex_start_party_box/.style={fill=white,draw,rounded corners=0.3ex,anchor=center,minimum height=1.7em,inner sep=1.5mm},
    annex_end_party_box/.style={annex_start_party_box,scale=0.7},
    % individual steps
    annex_message/.style={-Latex,line,draw=purple},
    annex_out_of_scope_message/.style={-Latex,line,dashed,draw=purple},
    annex_http_request/.style={-Latex,line,draw=purple},
    annex_http_response/.style={-Latex[open],line,draw=purple},
    annex_xhr_request/.style={-Latex,line,draw=blue},
    annex_xhr_response/.style={-Latex[open],line,draw=blue},
    annex_websocket/.style={-Latex,draw=red},
    annex_postmessage/.style={->,line,dashed,draw=red},
    annex_action/.style={fill=white,inner sep=0ex,minimum height=1.5em},
    annex_open_window/.style={->,line,dashed},
    annex_script_action_box/.style={annex_action,anchor=center},
    annex_script_action_arrow/.style={->,line},
    annex_script_action_arrow_reversed/.style={<-,line},
    annex_open_window_start_party_box/.style={annex_start_party_box},
    annex_open_window_start_party_arrow/.style={->,line,dashed},
    annex_close_window_end_party_box/.style={annex_end_party_box},
    annex_close_window_end_party_arrow/.style={->,line,dashed},
    annex_separator/.style={seperatorline,dashed},
    annex_vertical_space/.style={},
    % text styles
    annex_arrow_text/.style={font=\sffamily\tiny},
    annex_postmessage_text/.style={font=\sffamily\tiny\color{red}},
    annex_comment_text/.style={font=\bfseries},
    annex_multistep_caption_text/.style={font=\sffamily\tiny\color{blue}},
    annex_note/.style={},
    % Debug nodes/captions
    annex_debug/.style={opacity=0},
    """


class StyleDebug(yaml.YAMLObject):
    yaml_tag = "!style-debug"

    style = """
    annex_group_box/.style={fill=cyan!20},
    annex_matrix_node/.style={draw=red},
    annex_matrix_dummy_height/.style={draw=green},
    annex_group_title_placeholder/.style={draw=pink},
    annex_script_action_box/.style={draw=yellow},
    annex_script_action_arrow/.style={->,draw=yellow},
    annex_vertical_space/.style={fill=magenta,opacity=.1},
    annex_debug/.style={draw=none,opacity=.5},
    """
