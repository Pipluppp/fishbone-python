import pandas as pd
import sys

class Canvas:
    def __init__(self, rows):
        self.rows = rows
        self.cols = rows * 3
        self.left_padding = self.cols // 2
        self.right_padding = self.cols  // 10
        self.top_bottom_padding = rows // 5
        self.content = [[" "]*(self.left_padding + self.cols + self.right_padding) for _ in range(self.top_bottom_padding + self.rows + self.top_bottom_padding)]

class Fishbone:
    max_height = 0
    max_degree = 0

    def __init__(self, name, level, pos, canvas):
        self.name = name
        self.parent = self
        self.level = level
        self.length = (canvas.cols if level % 2 == 0 else canvas.rows) >> level
        self.pos = pos
        self.row = 0
        self.col = 0
        self.children = []   

    def load_fishbone_structure(self, df, canvas):
        """Load Fishbone canvas into memory, and add attributes of name, parent, level, length, pos"""
        columns = df.columns.to_list()

        # The number of bone levels is just the number of columns from Excel dataframe - 1
        Fishbone.max_height = len(columns) - 1

        for _, row in df.iterrows():
            # Get Fishbone diagram title to root
            if (_ == 0):
                self.name = row[columns[0]]
                continue

            # Find the current node on the Excel row to append (e.g. 1, 2, 3, current_node)
            for idx, c in enumerate(columns):
                current_node = row[c]

                if (str(current_node).isdigit()):
                    continue

                # Traverse through the branches to find specific parent bone to append the node
                parent = root
                level = 1
                for _ in range(1, idx):
                    branches = len(parent.children)
                    if (branches == 0):
                        break
                    parent = parent.children[branches - 1]
                    level += 1
                    
                # Update Fishbone's max number of children
                Fishbone.max_degree = max(Fishbone.max_degree, len(parent.children) + 1)

                child = Fishbone(current_node, level, len(parent.children) + 1, canvas)
                child.parent = parent
                
                parent.children.append(child)
                break

        return self
    
    def rescale_bone_lengths(self):
        """Rescale fishbone length if longer than grandparent's spacing. Also limits going out the canvas"""
        # Overlaps only happen with bone levels 3 onwards
        if (self.level > 2):
            grandparent = self.parent.parent
            grandparent_spacing = grandparent.length // (len(grandparent.children) + 1)

            if (self.length >= grandparent_spacing):
                self.length = (grandparent_spacing // 2) if (self.level % 2 == 0) else grandparent_spacing - 1

        for child in self.children:
            child.rescale_bone_lengths()

    def position_head(self):
        """Position heads of fishbones, relative to number of siblings"""
        siblings = len(self.parent.children)
        spacing = self.pos * self.parent.length // (siblings + 1)

        # Special spacing for Level 1 bones, to make the spacing more wider
        if (self.level == 1):
            spacing = ((self.pos + 1) // 2) * (root.length // 3) - (canvas.cols // 10)

        # Vertical bone
        if (self.level % 2 == 1):
            self.row = self.parent.row
            self.col = self.parent.col - spacing
        # Horizontal bone
        else:
            # Add Level 2 bones alternately on top or bottom depending on parent being at top or bottom
            self.row = self.parent.row + (- spacing if (self.parent.pos % 2 == 0 and self.level == 2) else (spacing))
            self.col = self.parent.col - spacing

        for child in self.children:
            child.position_head()

def draw_heads(root, canvas):
    """Marks the heads of each fishbone"""
    if (root.level != 0):
        canvas.content[root.row][root.col] = "\u25a0"

    if (len(root.children) == 0):
        return
    
    for i in root.children:
        draw_heads(i, canvas)

def draw_main_arrow_head(root, canvas):
    """Mark main fishbone arrow head"""
    length = len(root.name) + 1
    fishbone_arrow_length = canvas.rows  // 10
    
    # Spacing between arrow head and title
    canvas.content[root.row][root.col - length] = " "
    canvas.content[root.row][root.col - length + 1] = " "

    for i in range(1, fishbone_arrow_length):
        for j in range(1, fishbone_arrow_length):
            canvas.content[root.row + i][root.col - length - i - j] = "\u25a0"
            canvas.content[root.row - i][root.col - length - i - j] = "\u25a0"
        
def draw_bone_horizontal(fishbone, canvas):
    """Draw horizontal fishbones"""
    char = "-" if fishbone.level else "\u25a0"

    for i in range(1, fishbone.length):
        canvas.content[fishbone.row][fishbone.col - i] = char

    draw_bone_name(fishbone, canvas)

def draw_bone_NW(fishbone, canvas):
    """Draw diagonal bones towards North West"""
    for i in range(1, fishbone.length):
        canvas.content[fishbone.row + i][fishbone.col - i] = "\\"

    draw_bone_name(fishbone, canvas)

def draw_bone_SW(fishbone, canvas):
    """Draw diagonal bones towards South West"""
    for i in range(1, fishbone.length):
        canvas.content[fishbone.row - i][fishbone.col - i] = "/"

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
        name_position_col = fishbone.col - fishbone.length
    elif (fishbone.pos % 2 == 0 and fishbone.level == 1):
        # South-west diagonal bones
        name_position_row = fishbone.row - fishbone.length + 1
        name_position_col = fishbone.col - fishbone.length
    else:
        # North-west diagonal bones
        name_position_row = fishbone.row + fishbone.length - 1
        name_position_col = fishbone.col - fishbone.length

    for i, char in enumerate(reversed(fishbone.name), 1):
        canvas.content[name_position_row][name_position_col - i] = char

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
df = pd.read_excel(file)

canvas = Canvas(50)
root = Fishbone("Root", 0, 0, canvas)
root.load_fishbone_structure(df, canvas)

# Increase canvas size if loaded fishbone too complex (lots of levels, lots of content). Reload the contents
if (Fishbone.max_height > 3 or Fishbone.max_degree > 7):
    canvas = Canvas(125)
    root = Fishbone("Root", 0, 0, canvas)
    root.load_fishbone_structure(df, canvas)

# Position the fishbone heads, rescale bone lengths that overlap
root.row = canvas.top_bottom_padding + canvas.rows // 2 - 1 
root.col = canvas.left_padding + canvas.cols - 1
root.rescale_bone_lengths()
root.position_head()

# Draws the fishbone diagram
draw_fishbone(root, canvas)
draw_heads(root, canvas)
draw_main_arrow_head(root, canvas)

# Print canvas
canvasLine = "content"
for i, row in enumerate(reversed(canvas.content), 1):
    values = "".join(f"{element:{1}s}" for element in row)
    line   = canvasLine.replace("content", values)
    print(line)