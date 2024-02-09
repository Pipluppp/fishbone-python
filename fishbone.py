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

    def draw_fishbone(self, fishbone):
        """Draw fishbones recursively"""
        if (fishbone.level % 2 == 0):
            self.draw_bone_horizontal(fishbone)
        elif (fishbone.level == 1 and fishbone.pos % 2 == 0):
            self.draw_bone_SW(fishbone)
        else:
            self.draw_bone_NW(fishbone)
        
        for child in fishbone.children:
            self.draw_fishbone(child)

    def draw_heads(self, fishbone):
        """Marks the heads of each fishbone"""
        if (fishbone.level != 0):
            self.content[fishbone.row][fishbone.col] = "\u25a0"

        if (len(fishbone.children) == 0):
            return
        
        for child in fishbone.children:
            self.draw_heads(child)

    def draw_main_arrow_head(self, fishbone):
        """Mark main fishbone arrow head"""
        length = len(fishbone.name) + 1
        fishbone_arrow_length = self.rows  // 10
        
        # Spacing between arrow head and title
        self.content[fishbone.row][fishbone.col - length] = " "
        self.content[fishbone.row][fishbone.col - length + 1] = " "

        for i in range(1, fishbone_arrow_length):
            for j in range(1, fishbone_arrow_length):
                self.content[fishbone.row + i][fishbone.col - length - i - j] = "\u25a0"
                self.content[fishbone.row - i][fishbone.col - length - i - j] = "\u25a0"
            
    def draw_bone_horizontal(self, fishbone):
        """Draw horizontal fishbones"""
        char = "-" if fishbone.level else "\u25a0"

        for i in range(1, fishbone.length):
            self.content[fishbone.row][fishbone.col - i] = char

        self.draw_bone_name(fishbone)

    def draw_bone_NW(self, fishbone):
        """Draw diagonal bones towards North West"""
        for i in range(1, fishbone.length):
            self.content[fishbone.row + i][fishbone.col - i] = "\\"

        self.draw_bone_name(fishbone)

    def draw_bone_SW(self, fishbone):
        """Draw diagonal bones towards South West"""
        for i in range(1, fishbone.length):
            self.content[fishbone.row - i][fishbone.col - i] = "/"

        self.draw_bone_name(fishbone)

    def draw_bone_name(self, fishbone):
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
            self.content[name_position_row][name_position_col - i] = char

class Fishbone:
    max_height = 0
    max_degree = 0

    def __init__(self, name, level, pos):
        self.name = name
        self.parent = self
        self.level = level
        self.pos = pos
        self.length = 0
        self.row = 0
        self.col = 0
        self.children = []   

    def load_fishbone_structure(self, df):
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
                    
                # Create the Fishbone node, connect to parent, and append to the Fishbone structure
                child = Fishbone(current_node, level, len(parent.children) + 1)
                child.parent = parent
                parent.children.append(child)

                # Update Fishbone's max number of children
                Fishbone.max_degree = max(Fishbone.max_degree, len(parent.children) + 1)
                break
        return self
    
    def set_fishbone_lengths(self, canvas):
        """Set the fishbone lengths of the Fishbone structure"""
        # Horizontal/Vertical bones get column/rows size, scaled by the bone's level
        if (self.level % 2 == 0):
            self.length = canvas.cols >> self.level
        else:
            self.length = canvas.rows >> self.level

        # Rescale lengths overlapping fishbones around it
        self.rescale_bone_length()

        for child in self.children:
            child.set_fishbone_lengths(canvas)
    
    def rescale_bone_length(self):
        """Rescale fishbone length if longer than grandparent's spacing. Also limits going out the canvas"""
        # Overlaps only happen with bone levels 3 onwards
        grandparent = self.parent.parent
        grandparent_spacing = grandparent.length // (len(grandparent.children) + 1)

        if (self.level <= 2):
            return
    
        if (self.length < grandparent_spacing):
            return
        
        self.length = (grandparent_spacing // 2) if (self.level % 2 == 0) else grandparent_spacing - 1

    def position_heads(self, canvas):
        """Position heads of fishbones, relative to number of siblings"""
        siblings = len(self.parent.children)
        spacing = self.pos * self.parent.length // (siblings + 1)

        # Special placement for Root bone
        root.row = canvas.top_bottom_padding + canvas.rows // 2 - 1 
        root.col = canvas.left_padding + canvas.cols - 1

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
            child.position_heads(canvas)

file = sys.argv[1]
df = pd.read_excel(file)

root = Fishbone("Root", 0, 0)
root.load_fishbone_structure(df)

# Set canvas size dependent on fishbone complexity: Multiple evels, Packed with content
if (Fishbone.max_height > 3 or Fishbone.max_degree > 7):
    canvas = Canvas(125)
else:
    canvas = Canvas(50)

# Set the fishbone lengths, position the fishbone heads
root.set_fishbone_lengths(canvas)
root.position_heads(canvas)

# Draws the fishbone diagram
canvas.draw_fishbone(root)
canvas.draw_heads(root)
canvas.draw_main_arrow_head(root)

# Print canvas
canvasLine = "content"
for i, row in enumerate(reversed(canvas.content), 1):
    values = "".join(f"{element:{1}s}" for element in row)
    line   = canvasLine.replace("content", values)
    print(line)