# The World Clock (Weltzeituhr) in Kryptos K4

Breadcrumb: Home > Docs > Sources > Clock


In the context of Jim Sanborn's Kryptos K4 puzzle, the World Clock (Weltzeituhr) is not used as a complex math engine, but rather as a highly tactile, physical, and historical key. When Sanborn formally clarified that the "BERLINCLOCK" clue explicitly pointed to the World Clock, codebreakers and journalists—including those who recently reviewed his original Smithsonian coding scraps—identified how its specific attributes translate cryptographically:

1. Geographic Alignment & Vector Keys

    - The World Clock serves as a spatial reference point when paired with other clues. The "East-Northeast" Vector: Sanborn previously released the plaintext clue "EASTNORTHEAST" (often abbreviated or misspelled in his notes as "NORTHEST").
    - The Physical Link: In the actual city layout of Berlin, if you draw a straight line from the Berlin Clock (Mengenlehreuhr) heading exactly East-Northeast, it leads directly to Alexanderplatz, where the World Clock sits.
    - Cryptographic Use: In classical ciphers, geographic angles (like \(67.5^{\circ }\) for East-Northeast) or physical distances between the coordinates of these two clocks can be converted into numbers. These numbers frequently act as a numerical key or a shift index to slide letters along a Vigenère cipher tableau.

2. Historical & Narrative Data Substitution

    - Sanborn explicitly noted that the fall of the Berlin Wall heavily influenced his plaintext design. The World Clock was the central public gathering landmark for the crowds during the 1989 protests.
    - Data Fields as Plaintext: In Kryptos, historical details often mask the final riddle. Names, exact dates (e.g., November 9, 1989), or the specific 148 cities engraved on the World Clock's rotunda can serve as a custom alphabet or a substitution key.

3. "Go Between the Lines" & The Shadow Rule

    - Sanborn’s underlying puzzle design relies heavily on physical observation, shadows, and perspective.
    - The "Secret is the Shadow" Clue: Decoded materials heavily associate the clocks with instructions like "go between the lines" and "the secret is the shadow of the word".
    - Cryptographic Use: The World Clock features a massive, rotating kinetic sculpture of the solar system on top. The physical alignment of its moving metal rods and the specific shadows they cast at certain times of day replicate a mechanical cipher.
    - This acts similarly to a transposition cipher Matrix, where the changing alignment of physical parts determines how scrambled letters should be re-ordered to read smoothly.
    - Ultimately, Sanborn has joked to investigators, "Who says it is even a math solution?" indicating that the World Clock is a visual cipher—using geography, time zones, and its unique structure to decode the 97 elusive characters of K4.
    -  We may need to explore the Vigenère tableau and methods Sanborn used in k1,k2,k3 or look closer at the historical timeline of the Berlin Wall's fall or other events to uncover the exact mechanism by which the World Clock's or other clocks attributes are used in the K4 solution.