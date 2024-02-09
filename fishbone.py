import pandas as pd
import sys

class Canvas:
    def __init__(self, rows):
        self.rows = rows
        self.cols = rows * 3
        self.left_padding = self.cols // 3
        self.right_padding = self.cols  // 10
        self.top_bottom_padding = rows // 5
        self.content = [[" "]*(self.left_padding + self.cols + self.right_padding) for _ in range(self.top_bottom_padding + self.rows + self.top_bottom_padding)]

class Fishbone:
    def __init__(self, name, level, pos, canvas):
        self.name = name
        self.parent = self
        self.level = level
        self.length = (canvas.cols if level % 2 == 0 else canvas.rows) >> level
        self.pos = pos
        self.row = 0
        self.col = 0
        self.children = []   

    def load_fishbone(self, df, canvas):
        """Load Fishbone canvas into memory, and add attributes of name, parent, level, length, pos, row and col"""
        columns = df.columns.to_list()

        # For each row of the table
        for _, i in df.iterrows():
            # Get Fishbone diagram title to root
            if (_ == 0):
                self.name = i[columns[0]]
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
                    
                child = Fishbone(i[c], level, len(temp.children) + 1, canvas)
                child.parent = temp
                
                temp.children.append(child)
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
root.row = canvas.top_bottom_padding + canvas.rows // 2 - 1
root.col = canvas.left_padding + canvas.cols - 1

# Loads fishbone content into root, fix bone lengths overlaps, and position head of the fishbones
root.load_fishbone(df, canvas)
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