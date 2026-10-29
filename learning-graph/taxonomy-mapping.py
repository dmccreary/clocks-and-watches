"""Add taxonomy IDs to the learning graph CSV."""
import csv

# Define taxonomy assignments for each concept ID
taxonomy = {
    # FOUND - Foundation Concepts (1-5, 48)
    1: "FOUND", 2: "FOUND", 3: "FOUND", 4: "FOUND", 5: "FOUND", 48: "FOUND",

    # PYTH - Python Programming (6-31, 246-263)
    6: "PYTH", 7: "PYTH", 8: "PYTH", 9: "PYTH", 10: "PYTH", 11: "PYTH",
    12: "PYTH", 13: "PYTH", 14: "PYTH", 15: "PYTH", 16: "PYTH", 17: "PYTH",
    18: "PYTH", 19: "PYTH", 20: "PYTH", 21: "PYTH", 22: "PYTH", 23: "PYTH",
    24: "PYTH", 25: "PYTH", 26: "PYTH", 27: "PYTH", 28: "PYTH", 29: "PYTH",
    30: "PYTH", 31: "PYTH",
    246: "PYTH", 247: "PYTH", 248: "PYTH", 249: "PYTH", 250: "PYTH",
    251: "PYTH", 252: "PYTH", 253: "PYTH", 254: "PYTH", 255: "PYTH",
    256: "PYTH", 257: "PYTH", 258: "PYTH", 259: "PYTH", 260: "PYTH",
    261: "PYTH", 262: "PYTH", 263: "PYTH",

    # HARD - Hardware and Electronics (39-40, 52-55, 264-278, 209)
    39: "HARD", 40: "HARD", 52: "HARD", 53: "HARD", 54: "HARD", 55: "HARD",
    264: "HARD", 265: "HARD", 266: "HARD", 267: "HARD", 268: "HARD",
    269: "HARD", 270: "HARD", 271: "HARD", 272: "HARD", 273: "HARD",
    274: "HARD", 275: "HARD", 276: "HARD", 277: "HARD", 278: "HARD",
    209: "HARD",

    # MCTR - Microcontroller (32-38, 41-47, 49-51, 111, 229, 291)
    32: "MCTR", 33: "MCTR", 34: "MCTR", 35: "MCTR", 36: "MCTR",
    37: "MCTR", 38: "MCTR", 41: "MCTR", 42: "MCTR", 43: "MCTR",
    44: "MCTR", 45: "MCTR", 46: "MCTR", 47: "MCTR", 49: "MCTR",
    50: "MCTR", 51: "MCTR", 111: "MCTR", 229: "MCTR", 291: "MCTR",

    # COMM - Communication Buses (56-71, 325-330)
    56: "COMM", 57: "COMM", 58: "COMM", 59: "COMM", 60: "COMM",
    61: "COMM", 62: "COMM", 63: "COMM", 64: "COMM", 65: "COMM",
    66: "COMM", 67: "COMM", 68: "COMM", 69: "COMM", 70: "COMM",
    71: "COMM", 325: "COMM", 326: "COMM", 327: "COMM", 328: "COMM",
    329: "COMM", 330: "COMM",

    # TIME - Timekeeping (85-122, 292-300)
    85: "TIME", 86: "TIME", 87: "TIME", 88: "TIME", 89: "TIME",
    90: "TIME", 91: "TIME", 92: "TIME", 93: "TIME", 94: "TIME",
    95: "TIME", 96: "TIME", 97: "TIME", 98: "TIME", 99: "TIME",
    100: "TIME", 101: "TIME", 102: "TIME", 103: "TIME", 104: "TIME",
    105: "TIME", 106: "TIME", 107: "TIME", 108: "TIME", 109: "TIME",
    110: "TIME", 112: "TIME", 113: "TIME", 114: "TIME",
    115: "TIME", 116: "TIME", 117: "TIME", 118: "TIME", 119: "TIME",
    120: "TIME", 121: "TIME", 122: "TIME",
    292: "TIME", 293: "TIME", 294: "TIME", 295: "TIME", 296: "TIME",
    297: "TIME", 298: "TIME", 299: "TIME", 300: "TIME",

    # DISP - Displays and Drawing (123-169, 279-290, 205-207, 230, 348-350)
    123: "DISP", 124: "DISP", 125: "DISP", 126: "DISP", 127: "DISP",
    128: "DISP", 129: "DISP", 130: "DISP", 131: "DISP", 132: "DISP",
    133: "DISP", 134: "DISP", 135: "DISP", 136: "DISP", 137: "DISP",
    138: "DISP", 139: "DISP", 140: "DISP", 141: "DISP", 142: "DISP",
    143: "DISP", 144: "DISP", 145: "DISP", 146: "DISP", 147: "DISP",
    148: "DISP", 149: "DISP", 150: "DISP", 151: "DISP", 152: "DISP",
    153: "DISP", 154: "DISP", 155: "DISP", 156: "DISP", 157: "DISP",
    158: "DISP", 159: "DISP", 160: "DISP", 161: "DISP", 162: "DISP",
    163: "DISP", 164: "DISP", 165: "DISP", 166: "DISP", 167: "DISP",
    168: "DISP", 169: "DISP",
    279: "DISP", 280: "DISP", 281: "DISP", 282: "DISP", 283: "DISP",
    284: "DISP", 285: "DISP", 286: "DISP", 287: "DISP", 288: "DISP",
    289: "DISP", 290: "DISP",
    205: "DISP", 206: "DISP", 207: "DISP", 230: "DISP",
    348: "DISP", 349: "DISP", 350: "DISP",

    # MATH - Math and Geometry (81, 231-245)
    81: "MATH", 231: "MATH", 232: "MATH", 233: "MATH", 234: "MATH",
    235: "MATH", 236: "MATH", 237: "MATH", 238: "MATH", 239: "MATH",
    240: "MATH", 241: "MATH", 242: "MATH", 243: "MATH", 244: "MATH",
    245: "MATH",

    # INPT - Input and Sensors (72-84, 195-199, 343-346)
    72: "INPT", 73: "INPT", 74: "INPT", 75: "INPT", 76: "INPT",
    77: "INPT", 78: "INPT", 79: "INPT", 80: "INPT", 82: "INPT",
    83: "INPT", 84: "INPT",
    195: "INPT", 196: "INPT", 197: "INPT", 198: "INPT", 199: "INPT",
    343: "INPT", 344: "INPT", 345: "INPT", 346: "INPT",

    # SNPW - Sound and Power (101, 183-189, 200-204, 208, 336-340)
    101: "SNPW", 183: "SNPW", 184: "SNPW", 185: "SNPW", 186: "SNPW",
    187: "SNPW", 188: "SNPW", 189: "SNPW",
    200: "SNPW", 201: "SNPW", 202: "SNPW", 203: "SNPW", 204: "SNPW",
    208: "SNPW", 336: "SNPW", 337: "SNPW", 338: "SNPW", 339: "SNPW",
    340: "SNPW",

    # PROJ - Projects and Kits (170-182, 190-194, 301-306, 314-318, 341-342, 347, 175-177)
    170: "PROJ", 171: "PROJ", 172: "PROJ", 173: "PROJ", 174: "PROJ",
    175: "PROJ", 176: "PROJ", 177: "PROJ",
    178: "PROJ", 179: "PROJ", 180: "PROJ", 181: "PROJ", 182: "PROJ",
    190: "PROJ", 191: "PROJ", 192: "PROJ", 193: "PROJ", 194: "PROJ",
    301: "PROJ", 302: "PROJ", 303: "PROJ", 304: "PROJ", 305: "PROJ",
    306: "PROJ", 311: "PROJ", 312: "PROJ", 313: "PROJ",
    314: "PROJ", 315: "PROJ", 316: "PROJ", 317: "PROJ", 318: "PROJ",
    341: "PROJ", 342: "PROJ", 347: "PROJ",

    # DSGN - Design and Development (210-228, 308-310, 319-324, 331-335)
    210: "DSGN", 211: "DSGN", 212: "DSGN", 213: "DSGN", 214: "DSGN",
    215: "DSGN", 216: "DSGN", 217: "DSGN", 218: "DSGN", 219: "DSGN",
    220: "DSGN", 221: "DSGN", 222: "DSGN", 223: "DSGN", 224: "DSGN",
    225: "DSGN", 226: "DSGN", 227: "DSGN", 228: "DSGN",
    308: "DSGN", 309: "DSGN", 310: "DSGN",
    319: "DSGN", 320: "DSGN", 321: "DSGN", 322: "DSGN", 323: "DSGN",
    324: "DSGN", 331: "DSGN", 332: "DSGN", 333: "DSGN", 334: "DSGN",
    335: "DSGN",
}

# Read CSV and add taxonomy
rows = []
with open('learning-graph.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cid = int(row['ConceptID'])
        tax = taxonomy.get(cid, "MISC")
        row['TaxonomyID'] = tax
        rows.append(row)

# Write updated CSV
with open('learning-graph.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['ConceptID', 'ConceptLabel', 'Dependencies', 'TaxonomyID'])
    writer.writeheader()
    writer.writerows(rows)

# Report
from collections import Counter
counts = Counter(r['TaxonomyID'] for r in rows)
print("Taxonomy distribution:")
for tax, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {tax}: {count} ({count/len(rows)*100:.1f}%)")

misc = [r for r in rows if r['TaxonomyID'] == 'MISC']
if misc:
    print(f"\nMISC concepts ({len(misc)}):")
    for r in misc:
        print(f"  {r['ConceptID']}. {r['ConceptLabel']}")
