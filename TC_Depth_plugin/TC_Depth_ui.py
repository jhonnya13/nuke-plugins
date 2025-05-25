import nuke
import importlib
import TC_Depth_processing
importlib.reload(TC_Depth_processing)


def create_depth_node():
    # Create a custom node
    node = nuke.createNode("NoOp")
    node.setName("TC_Depth")

    # Set tile color
    node['tile_color'].setValue(0xff0309ff)  # Set tile color (RGBA value) 345f1dff

    # Add a Text_Knob for instructions
    instruction_knob = nuke.Text_Knob('instructions', '', ' - MiDas plugin works with png only\n - You need to connect it to the Read node')
    node.addKnob(instruction_knob)

    divider_knob = nuke.Text_Knob('', '', '')  # Empty name, label, and text
    node.addKnob(divider_knob)


    # Add an enumeration knob (dropdown) for model selection
    model_knob = nuke.Enumeration_Knob('modelSelector', 'Select Model', ['DPT_Hybrid', 'DPT_Large'])
    node.addKnob(model_knob)

    # Set the autolabel to dynamically display the selected model
    autolabel_script = "nuke.thisNode().name() + '\\n' + '(' + nuke.thisNode()['modelSelector'].value() + ')' "
    node['autolabel'].setValue(autolabel_script)

    divider = nuke.Text_Knob('divider', '')  # Empty text creates a simple line
    node.addKnob(divider)
    
    file_path_knob = nuke.File_Knob('outputPath', 'Output Path')
    node.addKnob(file_path_knob)
    file_path_knob.setTooltip("Out/path/to/save/frames.####.png")
    node['outputPath'].setValue('/')
    

    # Add a button to trigger the depth estimation
    button_knob = nuke.PyScript_Knob('getDepth', 'Render Depth')
    button_knob.setFlag(nuke.STARTLINE)  # This will place the button on a new line
    node.addKnob(button_knob)

    # Attach the function to the button knob
    button_knob.setCommand('import TC_Depth_processing; TC_Depth_processing.run_depth_estimation()')
    
    
    # Add a blank text knob for spacing
    spacer = nuke.Text_Knob('spacer', '', '')
    node.addKnob(spacer)
    
    # Add descriptive text knobs for multi-line information
    info_knob_line1 = nuke.Text_Knob('info', '')
    info_knob_line1.setValue('<i>AI tools for VFX<i>')
    node.addKnob(info_knob_line1)

    info_knob_line2 = nuke.Text_Knob('contact', '')
    info_knob_line2.setValue('<i>www.third-creator.com<i>')
    node.addKnob(info_knob_line2)

    # Make them non-editable
    info_knob_line1.setFlag(nuke.READ_ONLY)
    info_knob_line2.setFlag(nuke.READ_ONLY)



