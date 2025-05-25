import nuke
from TC_Depth_ui import *

nuke.pluginAddPath('./icons')


# Check if the "Third Creator" menu already exists
menu_name = "Third Creator"
nodes_menu = nuke.menu("Nodes")
third_creator_menu = nodes_menu.findItem(menu_name)

if not third_creator_menu:
    # Create the menu if it doesn't exist
    third_creator_menu = nodes_menu.addMenu(menu_name, icon="third_creator_icon.png")

# Add a command to create the TC_Depth node under the "Third Creator" menu
third_creator_menu.addCommand("TC_Depth", "create_depth_node()")




