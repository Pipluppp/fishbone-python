import pandas as pd

ROWS = 50
COLS = 200
LEFT_PADDING = 75

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

def print_fishbone(root):
    """For testing: Recursively print Fishbones"""
    for i in range(root.level):
        print("-", end = "")

    print(f"{root.name} (parent is {root.parent.name}, has coordinates ({root.row}, {root.col}) and length {root.length})")

    branches = len(root.children)
    if (branches == 0):
        return
    for i in root.children:
        print_fishbone(i)

def load_fishbone(df, name):
    """Load Fishbone canvass into memory, and add attributes of name, parent, level, length, pos, row and col"""
    columns = df.columns.to_list()
    root = Fishbone(name, 0, 0)
    root.row = ROWS // 2 - 1
    root.col = COLS + LEFT_PADDING - 1

    # For each row of the table
    for _, i in df.iterrows():
        # Skip the first line which is just the useless column names
        if (_ == 0):
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

            # Add point head of fishbone
            spacing = child.pos * temp.length // 6
            if (child.level % 2):
                child.row = temp.row
                child.col = temp.col - spacing
            else:
                # Add diagonal alternately
                child.row = temp.row + (spacing if child.parent.pos % 2 else (- spacing))
                child.col = temp.col - spacing
            
            temp.children.append(child)
            break

    return root

def plot_heads(root, canvas):
    """Marks the heads of each fishbone"""
    # Plot special arrow head for main bone
    if (root.level == 0):
        length = len(root.name) + 1
        for i in range(6):
            for j in range(6):
                canvas[root.row + i][root.col - length - i - j] = "\u25a0"
                canvas[root.row - i][root.col - length - i - j] = "\u25a0"

    if (root.level != 0):
        canvas[root.row][root.col] = "\u25a0"

    if (len(root.children) == 0):
        return
    
    for i in root.children:
        plot_heads(i, canvas)

def draw_bone_horizontal(fishbone, canvas):
    """Draw horizontal fishbones"""
    char = "-" if fishbone.level else "\u25a0"

    for i in range(1, fishbone.length):
        canvas[fishbone.row][fishbone.col - i] = char

    # If main bone, name at front
    if (fishbone.level == 0):
        name_starting_column = fishbone.col - 1
        # Add space between front bone name and arrow
        canvas[fishbone.row][fishbone.col - len(fishbone.name) - 1] = " "
    else:
        name_starting_column = fishbone.col - fishbone.length - 1
    
    # Add fishbone name
    for i, char in enumerate(reversed(fishbone.name)):
        canvas[fishbone.row][name_starting_column - i] = char

def draw_bone_NW(fishbone, canvas):
    """Draw diagonal bones towards North West"""
    for i in range(1, fishbone.length):
        canvas[fishbone.row + i][fishbone.col - i] = "\\"

    for i, char in enumerate(reversed(fishbone.name)):
        canvas[fishbone.row + fishbone.length - 1][fishbone.col - fishbone.length - i] = char

def draw_bone_SW(fishbone, canvas):
    """Draw diagonal bones towards South West"""
    for i in range(1, fishbone.length):
        canvas[fishbone.row - i][fishbone.col - i] = "/"

    # Add fishbone name
    name_length = len(fishbone.name)
    for i, char in enumerate(reversed(fishbone.name)):
        canvas[fishbone.row - fishbone.length + 1][fishbone.col - fishbone.length - i] = char

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

canvas = [[" "]*(COLS + LEFT_PADDING) for _ in range(ROWS)]
df = pd.read_excel('test-nested-2.xlsx')
root = load_fishbone(df, "Late to Work")
plot_heads(root, canvas)
draw_fishbone(root, canvas)

# Guide frames
for i in range(1, COLS - 1):
    canvas[0][LEFT_PADDING + i] = "X"
    canvas[ROWS - 1][LEFT_PADDING + i] = "-"

for i in range(1, ROWS - 1):
    canvas[i][LEFT_PADDING] = "|"
    canvas[i][LEFT_PADDING + COLS - 1] = "|"  

# Print canvas
canvasLine = "content"
for i, row in enumerate(reversed(canvas), 1):
    values = "".join(f"{element:{1}s}" for element in row)
    line   = canvasLine.replace("content", values)
    print(line)
