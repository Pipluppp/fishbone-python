import pandas as pd
import sys

ROWS = 125
COLS = ROWS * 3
LEFT_PADDING = COLS // 3
RIGHT_PADDING = COLS // 10
TOP_BOTTOM_PADDING = ROWS // 5

class Fishbone:
    def __init__(self, name, level, pos):
        self.name = name
        self.parent = self
        self.level = level
        self.length = (COLS if level % 2 == 0 else ROWS) >> level
        self.pos = pos
        self.row = 0
        self.col = 0
        self.children = []   

    def print_fishbone_content(self):
        """For testing: Recursively print Fishbones"""
        for i in range(self.level):
            print("-", end = "")

        print(f"{self.name} (parent is {self.parent.name}, has coordinates ({self.row}, {self.col}) and length {self.length})")

        branches = len(self.children)
        if (branches == 0):
            return
        for child in self.children:
            child.print_fishbone_content()

def load_fishbone(df):
    """Load Fishbone canvas into memory, and add attributes of name, parent, level, length, pos, row and col"""
    columns = df.columns.to_list()
    root = Fishbone("Root", 0, 0)
    root.row = TOP_BOTTOM_PADDING + ROWS // 2 - 1
    root.col = LEFT_PADDING + COLS - 1

    # For each row of the table
    for _, i in df.iterrows():
        # Get Fishbone diagram title to root
        if (_ == 0):
            root.name = i[columns[0]]
            continue

        # Find the canvas/node to append
        for idx, c in enumerate(columns):
            # Series of digits determins the level, skip them until we find the canvas
            if (str(i[c]).isdigit()):
                continue

            temp = root
            level = 1

            # Traverse through the branches to find specific parent bone to append the node
            for j in range(1, idx):
                branch = len(temp.children)
                if (branch == 0):
                    break
                temp = temp.children[branch - 1]
                level += 1
                
            child = Fishbone(i[c], level, len(temp.children) + 1)
            child.parent = temp
            
            temp.children.append(child)
            break

    return root

def position_head(bone):
    """Position heads of fishbones, relative to number of siblings"""
    siblings = len(bone.parent.children)
    spacing = bone.pos * bone.parent.length // (siblings + 1)

    # Special spacing for Level 1 bones, to make the spacing more wider
    if (bone.level == 1):
        spacing = ((bone.pos + 1) // 2) * (root.length // 3) - (COLS // 10)

    # Vertical bone
    if (bone.level % 2 == 1):
        bone.row = bone.parent.row
        bone.col = bone.parent.col - spacing
    # Horizontal bone
    else:
        # Add Level 2 bones alternately on top or bottom depending on parent being at top or bottom
        bone.row = bone.parent.row + (- spacing if (bone.parent.pos % 2 == 0 and bone.level == 2) else (spacing))
        bone.col = bone.parent.col - spacing

    for i in bone.children:
        position_head(i)

def rescale(bone):
    """Rescale fishbone length if longer than grandparent's spacing. Also limits going out the canvas"""
    # Overlaps only happen with bone levels 3 onwards
    if (bone.level > 2):
        grandparent = bone.parent.parent
        grandparent_spacing = grandparent.length // (len(grandparent.children) + 1)

        if (bone.length >= grandparent_spacing):
            bone.length = (grandparent_spacing // 2) if (bone.level % 2 == 0) else grandparent_spacing - 1

    for i in bone.children:
        rescale(i)

def draw_heads(root, canvas):
    """Marks the heads of each fishbone"""
    if (root.level != 0):
        canvas[root.row][root.col] = "\u25a0"

    if (len(root.children) == 0):
        return
    
    for i in root.children:
        draw_heads(i, canvas)

def draw_main_arrow_head(root, canvas):
    """Mark main fishbone arrow head"""
    length = len(root.name) + 1
    fishbone_arrow_length = 10
    
    # Spacing between arrow head and title
    canvas[root.row][root.col - length] = " "
    canvas[root.row][root.col - length + 1] = " "

    for i in range(1, fishbone_arrow_length):
        for j in range(1, fishbone_arrow_length):
            canvas[root.row + i][root.col - length - i - j] = "\u25a0"
            canvas[root.row - i][root.col - length - i - j] = "\u25a0"
        
def draw_bone_horizontal(fishbone, canvas):
    """Draw horizontal fishbones"""
    char = "-" if fishbone.level else "\u25a0"

    for i in range(1, fishbone.length):
        canvas[fishbone.row][fishbone.col - i] = char

    draw_bone_name(fishbone, canvas)

def draw_bone_NW(fishbone, canvas):
    """Draw diagonal bones towards North West"""
    for i in range(1, fishbone.length):
        canvas[fishbone.row + i][fishbone.col - i] = "\\"

    draw_bone_name(fishbone, canvas)

def draw_bone_SW(fishbone, canvas):
    """Draw diagonal bones towards South West"""
    for i in range(1, fishbone.length):
        canvas[fishbone.row - i][fishbone.col - i] = "/"

    draw_bone_name(fishbone, canvas)

def draw_bone_name(fishbone, canvas):
    """Draw name of fishbone"""
    name_position_row = 0
    name_position_col = 0

    # Name position varies on type of bone
    if (fishbone == root):
        # Root
        name_position_row = fishbone.row
        name_position_col = fishbone.col + 1
    elif (fishbone.level % 2 == 0):
        # Horizontal bones non-root
        name_position_row = fishbone.row
        name_position_col = fishbone.col - fishbone.length - 1
    elif (fishbone.pos % 2 == 0 and fishbone.level == 1):
        # South-west diagonal bones
        name_position_row = fishbone.row - fishbone.length + 1
        name_position_col = fishbone.col - fishbone.length
    else:
        # North-west diagonal bones
        name_position_row = fishbone.row + fishbone.length - 1
        name_position_col = fishbone.col - fishbone.length

    for i, char in enumerate(reversed(fishbone.name), 1):
        canvas[name_position_row][name_position_col - i] = char

def draw_fishbone(root, canvas):
    """Draw fishbones recursively"""
    if (root.level % 2 == 0):
        draw_bone_horizontal(root, canvas)
    elif (root.level == 1 and root.pos % 2 == 0):
        draw_bone_SW(root, canvas)
    else:
        draw_bone_NW(root, canvas)
    
    for i in root.children:
        draw_fishbone(i, canvas)

file = sys.argv[1]
canvas = [[""]*(LEFT_PADDING + COLS + RIGHT_PADDING) for _ in range(TOP_BOTTOM_PADDING + ROWS + TOP_BOTTOM_PADDING)]
df = pd.read_excel(file)
root = load_fishbone(df)

rescale(root)
position_head(root)

draw_fishbone(root, canvas)
draw_heads(root, canvas)
draw_main_arrow_head(root, canvas)

# Print canvas
canvasLine = "content"
for i, row in enumerate(reversed(canvas), 1):
    values = "".join(f"{element:{1}s}" for element in row)
    line   = canvasLine.replace("content", values)
    print(line)