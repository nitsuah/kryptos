# K4 Theories

## K4 Composite Pipeline: Clock-Indexed Matrix & Geometric Transposition Attack

This document specifies the exact execution architecture, parameterized configuration toggles ("tripwires"), and implementation roadmap for testing the layered physical-artistry hypothesis for Kryptos K4.

Based on local Index of Coincidence (IC) anomalies, the pipeline treats K4 not as a monolithic mathematical puzzle, but as a composite cipher where **Transposition was applied AFTER Substitution** by hand, using the physical states of the Berlin Clock (*Mengenlehreuhr*) and the geographic vectors of Berlin.

Critically, this architecture enforces a **strict linear dependency ("no skipping steps")**. Sanborn designed K4 as a final choke point that requires inputs, variables, and structural constraints directly inherited from the plaintext outcomes of K1, K2, and K3.

---

## I. Core Architecture & Layer Order

The pipeline must execute the inverse operations of Sanborn's suspected hand-encryption sequence. Because local IC segment analysis indicates transposition occurred last, the extraction engine must process the ciphertext in this exact sequence:

```
[ K4 Ciphertext (97 Chars) ]
             │
             ▼
┌──────────────────────────┐
│ 1. Null-Removal Filter   │ ──► Strips padding or "clock shadow" positions
└──────────────────────────┘
             │
             ▼
┌──────────────────────────┐
│ 2. ENE Route Geotrans    │ ──► Reverses diagonal reading path (tan(67.5°))
└──────────────────────────┘
             │
             ▼
┌──────────────────────────┐
│ 3. Hill 2x2 Matrix Loop  │ ──► Evaluates ~120 invertible Berlin Clock states
└──────────────────────────┘
             │
             ▼
┌──────────────────────────┐
│ 4. Vigenère / Crib Scan  │ ──► Validates against NORTHEAST / EAST alignments
└──────────────────────────┘
```

---

## II. The Parameterized Toggle Matrix ("The Tripwires")

To avoid the classical trap of hardcoding a single human interpretation of a visual clue, the front-end script must loop through a combinatorial matrix of parameters. Toggles 5 and 6 directly inject the upstream outputs of K1, K2, and K3 to solve the short-ciphertext entropy problem.

### Toggle 1: Null-Stripping Logic (`null_mode`)
* **`NONE`**: Process all 97 characters intact.
* **`INTERVAL_3`**: Drop every 3rd character systematically (yielding a 65-character residue).
* **`SHADOW_MASK`**: Drop characters dynamically based on the unlit ("shadow") positions of the specific clock state being evaluated.

### Toggle 2: Transposition Grid Dimensions (`grid_geometry`)
Because 97 is a prime number, Sanborn had to pad the grid or leave holes to lay out a transposition block.
* **`10x10`**: Map characters into a 100-slot grid (last 3 positions empty or nulls).
* **`7x14`**: Map characters into a 98-slot grid (last slot empty or null).
* **`8x13`**: Map characters into a 104-slot grid (last 7 slots empty or null).

### Toggle 3: Berlin Clock Matrix Extraction (`matrix_mode`)
For each of the 720 discrete minutes in a 12-hour cycle, map the 4 lamp rows (R1, R2, R3, R4) using two opposing light/dark frameworks:
* **`LIT`**: Counts the number of active, illuminated lamps per row.
* **`UNLIT`**: Counts the absolute structural shadows (Total Lamps in Row - Lit Lamps).
    * *Row 1 (5h): Max 4*
    * *Row 2 (1h): Max 4*
    * *Row 3 (5m): Max 11*
    * *Row 4 (1m): Max 4*

### Toggle 4: Matrix Geometry (`matrix_layout`)
How the 4-digit vector derived from the clock face is populated into a 2x2 matrix K:
* **`ROW_MAJOR`**: Top row [R1, R2], Bottom row [R3, R4]
* **`COL_MAJOR`**: Top row [R1, R3], Bottom row [R2, R4]
* **`SPIRAL`**: Top row [R1, R2], Bottom row [R4, R3]

### Toggle 5: Alphabet Space Mapping (`alphabet_mode`)
* **`LINEAR`**: Standard A=0, B=1, ..., Z=25.
* **`KEYED_KRYPTOS`**: Map integers 0–25 directly to the character indices of the customized KRYPTOS keyed alphabet layout block shared by K1/K2.
* **`KEYED_PALIMPSEST`**: Map integers 0–25 directly to the character indices of the PALIMPSEST specific keyword sequence layout.

### Toggle 6: Upstream Historic Clue Ingestion (`clue_modifier`)
This gate prevents skipping steps, binding K4 directly to the plaintexts extracted from the previous three courtyard panels.
* **`NONE`**: Target clock states across the baseline 720-minute loop.
* **`K2_COORDINATE_ANCHORS`**: Restrict or prioritize the clock states to times matching the literal numeric fragments extracted from the K2 plaintext coordinate string (38, 57, 06, 77, 08) acting as hour/minute selections (e.g., 08:57 or 06:38).
* **`K2_SCALAR_MODIFIER`**: Apply the coordinate digits as modular shifts (+/- mod 26) directly to the cells of the 2x2 Hill matrix to defeat standard textbook brute-forcing.
* **`K3_COMPASS_ALIGNMENT`**: Use the explicit spatial instructions from K2 ("TWO TWO NORTHEAST") and K3 ("PASSAGE ETTE TWO IS THAT POSITION") to modify the index offset or apply a structural step-skipping pattern of 2 rows / 2 columns along the ENE geotransposition pathway.

---

## III. Implementation Blueprint (Step-by-Step)

### Step 1: Enumerate and Filter the Clock Space
Create a static lookup array containing all 720 possible structural configurations of a 12-hour clock. For each state:
1. Extract the 4-digit vector based on `matrix_mode`.
2. Format into a 2x2 matrix based on `matrix_layout`.
3. If `clue_modifier` is active, apply any designated scalar or constraint derived from the K2 coordinate numbers.
4. Compute the modular determinant: det(K) = (a*d - b*c) mod 26.
5. **Filter:** Keep only matrices where gcd(det(K), 26) == 1. (This strips the search space down to roughly 100–120 valid invertible decryption keys per clock mode).

### Step 2: Implement the ENE Diagonal Route Transposition
Build a geometric reading function that simulates traversing a grid at an East-Northeast compass heading (67.5°).
1. Populate the selected `grid_geometry` array row-by-row with the text output from the Null Filter.
2. Trace reading paths through the matrix at a fixed slope calculated by tan(67.5°) ≈ 2.414. This means for every 1 row down, the index path steps approximately 2.4 columns to the right.
3. Extract characters sequentially along these parallel diagonal ribbons to yield the detransposed string. If the K2/K3 `clue_modifier` is set to spatial alignment, shift the reading path sequence by the designated offset boundary.

### Step 3: The Hill Decryption Engine
For the remaining ciphertext fragments:
1. Group characters into pairs (digraphs).
2. Compute the modular inverse of the active clock matrix K^-1.
3. Multiply each ciphertext digraph by K^-1 mod 26 using the active `alphabet_mode` mapping to recover the plaintext layer.

### Step 4: Automate Crib Validation (The Constraint Gate)
Because you possess verified anchor points provided directly by Sanborn, you do not need to read thousands of lines of output manually. Run every output string through a programmatic regex validation gate:
* **Gate A:** Does the string contain `NORTHEAST` spanning positions 26–34?
* **Gate B:** Does the string contain `EAST` spanning positions 34–37?
* **Gate C:** Does a localized index check reveal standard English bigram frequencies near those positions?

---

## IV. Execution Logistics & Optimization

* **Total Search Space Size:**
  120 Valid Matrices * 2 (Lit/Unlit) * 3 (Layouts) * 3 (Grids) * 3 (Alphabets) * 4 (Clue Modifiers) * 3 (Null Modes) = 233,280 unique states.

* **Compute Footprint:** Because Hill matrix inversion, array masking, and diagonal indexing are natively vectorizable processes, this entire execution matrix can be fully parallelized. Written in clean Python utilizing NumPy, or native TypeScript, the complete combinatorial sweep will execute and score in under 5 seconds on consumer hardware.

---

## V. Breakthrough Execution & The Eureka Protocol

To guarantee that a positive cryptographic match instantly halts execution and preserves the state machine for immediate inspection, the engine must implement an active interception sequence rather than passive logging.

### 1. Hard Core Intercept (The Eureka Interrupter)
When `Gate A` and `Gate B` match to a value of `TRUE`, the execution loop must instantly execute a hard kill-switch sequence:
* **Terminal Alert:** Flash a high-visibility terminal banner using ANSI styling printing `[!!!] EUREKA: K4 PLAIN TEXT HIT DETECTED`.
* **Audio Anchor:** Trigger a system bell/beeper escape sequence (`\a` or shell alert audio) to create an immediate physical notification during background headless processing.
* **Immediate Exiting:** Terminate all secondary worker threads using an explicit process halt (`process.exit(0)` or `sys.exit(0)`) to lock the application state exactly where the collision occurred.

### 2. Artifact Generation Specifications
Simultaneously with the terminal interruption, the validation framework must dump an immutable, standalone markdown artifact into the root project space named exactly `K4_BREAKTHROUGH_SNAPSHOT.md`. This file must preserve the entire structural environmental state of the run:

```markdown
# 🚨 K4 PLAIN TEXT SOLUTION ARCHIVE

## [ Reconstructed Target Plaintext ]
> INSERT FULL RECONSTRUCTED TEXT STRING HERE

## [ Cipher Parameter Configuration Profile ]
* **Null Mode Configuration:** [null_mode string]
* **Transposition Geometry:** [grid_geometry layout]
* **Berlin Clock Time State:** [Extracted time value, e.g., 08:57 / State #]
* **Clock Vector Mode:** [LIT / UNLIT]
* **Matrix Structure:** [ROW_MAJOR / COL_MAJOR / SPIRAL]
* **Target Hill Matrix K:** [Print 2x2 array values]
* **Target Decryption Matrix K^-1:** [Print inverted modular 2x2 matrix]
* **Active Alphabet Block Map:** [LINEAR / KEYED_KRYPTOS / KEYED_PALIMPSEST]
* **Ingested Clue Intercept Mode:** [clue_modifier configuration flag]

## [ Algorithmic Validation Matrix Metrics ]
* **Positional Index Shift Matches:** Chars 26-34: NORTHEAST | Chars 34-37: EAST
* **Global Text Index of Coincidence (IC):** [Calculated Float Value]
```

### 3. Debug State Variable Lock
The pipeline script should preserve a diagnostic trace environment flag (`save_snapshot_dump()`). When the breakthrough occurs, it must copy the active string variables, numerical configurations, and ciphertext transformations out into a local json trace file (`eureka_debug_dump.json`) so the path can be audited line-by-line in a localized sandbox workspace to verify the exact step-by-step mechanics of how Sanborn enciphered it by hand.