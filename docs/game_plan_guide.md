# This Document Covers the Entire Sunken Cathedral Game. 
7/19/25

Source: https://gemini.google.com/app/f285936dc2866638

### **The Premise**

You are the last Lamplighter, a guardian bound by blood and duty to a chain of phantom lighthouses along a cursed stretch of coast. For generations, your family has tended lights that no ship will ever see, their purpose lost to all but your lineage. Your life is one of solitude, of watching the waves and feeling a strange melancholy you’ve always known—a feeling the old texts call the Temporal Dissonance, an echo of a sorrow not your own.

One night, a storm of impossible fury awakens you. The sea does not rage; it screams. The ocean floor is scoured clean, and in the pre-dawn calm, you see it. Spires of impossible architecture piercing the waves, black against the rising sun. From the highest tower of this submerged structure, a single, ghostly light pulses, a soft, sorrowful blue. It is a beacon that only you can see, a call that resonates with the very ache in your soul.

Compelled by a duty you are only now beginning to understand, you take your ancestral lantern, its flame burning with a sacred, unwavering light. You descend from your lonely cliffside post, into the crushing, silent dark of the sea. You must reach that beacon. You must understand its sorrow. You must give it peace.

### **Game Mechanics: The Lamplighter's Journey**

The game is experienced through a retro interface inspired by classic 1980s text-parser adventures, blending real-time movement with thoughtful, command-based interaction.

**Interface & Graphics**

The entire world is rendered in ASCII characters, with the notable exception of runic script. The screen is divided into a main view and a persistent status panel.

* **Main View:** A top-down perspective of the Cathedral's halls. You are the ☺ symbol.  
* **Status Panel:** A fixed panel on the right side of the screen displaying your current state.

**Example Screen Layout:**

▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  |  The Sunken Cathedral  
▓≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈▓▓≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈▓  |  
▓≈  ☺         L         ≈▓▓≈      S       ≈▓  |  LANTERN OIL: 78%  
▓≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈▓  |  GEODE: \[None\]  
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  |  
                                             |  INVENTORY:  
A sign is carved here: ᛒᛖᚹᚪᚱᛖ ᚦᛖ ᛞᛟᛈ        |  \- Worn Scroll  
\> \_                                          |  \- \[empty\]  
                                             |  \- \[empty\]  
                                             |  \- \[empty\]

* **World Legend:**  
  * ☺ \- You, the Lamplighter  
  * ▓ █ \- Walls, Rubble  
  * ▒ \- Doors, Gates, Psychic Barriers  
  * ≈ \- Deep Water (impassable without light)  
  * L \- Lore Item (Scroll, Tablet)  
  * G \- Prayer Geode  
  * S \- Drowned Sorrow (Spirit)  
  * F \- Consecrated Font (Oil Source)

**Movement & Interaction**

Gameplay is a hybrid of two modes:

1. **Exploration (Real-Time):** Use the **arrow keys** to move your character ☺ through the Cathedral.  
2. **Interaction (Turn-Based):** When you need to perform an action, you type a two-word command (verb \+ noun) into the parser \>. The world pauses while you type.

**Core Gameplay Loop**

Your journey is a constant balance of managing your light, solving environmental puzzles, and interacting with the Cathedral's sorrowful past.

* **The Lantern & Sacred Oil:** Your lantern is your lifeline. Its flame pushes back the crushing deep and illuminates your path.  
  * Your **Sacred Oil** is a constantly depleting resource, shown as a percentage on the status panel.  
  * If your oil runs out, the screen goes dark. You cannot see, and the Drowned Sorrows will quickly overwhelm you, returning you to the last Consecrated Font you visited.  
  * To replenish your supply, you must find a Consecrated Font F and type FILL LANTERN.  
* **Prayer Geodes & Keys:** The Cathedral is sealed by more than just locks.  
  * You will find **Prayer Geodes** G, crystals that can be attuned to your lantern. To attune one, you type USE GEODE. Your status panel will update to show the active geode (e.g., GEODE: Amber).  
  * Different colored psychic barriers ▒ block your path. To pass them, you must have the corresponding geode attuned to your lantern and type SHINE LANTERN.  
  * Some physical doors are locked and require you to find specific keys, for which you would type USE KEY.  
* **Soothing the Drowned Sorrows:** Combat is an act of empathy.  
  * When you approach a Drowned Sorrow S, it will block your path. The message will read: "A Drowned Sorrow wails, its grief a tangible force."  
  * You cannot harm it physically. You must attune the correct **Prayer Geode** to your lantern—one that resonates with that specific type of sorrow.  
  * With the correct geode active, you type SOOTHE SPIRIT. The spirit will fade peacefully, clearing the way. Using the wrong geode will cause the spirit to lash out, draining a significant amount of your oil.  
* **Inventory & Lore:** Your inventory is limited. You must choose carefully what to carry.  
  * Finding a scroll L and typing READ SCROLL will display the journal entry text on screen, adding it to a permanent log you can access anytime. Once read, the physical scroll is no longer needed.  
  * Dropping items is a key strategy. If you need to carry a new geode but your inventory is full, you might type DROP SCROLL to make room, remembering where you left it for later.  
* **The Tidal Futhark:** The Cathedral's secrets are written in an ancient, runic script.  
  * Early in the game, you will find a **"Child's Learning Tablet"** which serves as your key, providing a partial translation of the Tidal Futhark.  
  * Throughout the Cathedral, you will find signs and warnings carved in these runes. The game will not translate them for you. You must decipher their meaning yourself using the alphabet provided in your log.  
  * These messages provide cryptic clues, foreshadowing, and warnings that are vital to understanding the full story.

### **Act I: The Weeping Halls**

You enter the Sunken Cathedral through a fractured, rose-shaped window. The water here is unnaturally still, and the air, miraculously, is breathable, held in place by a shimmering, invisible barrier. The silence is absolute, broken only by the soft hiss of your lantern and the slow, rhythmic drip of water from vaulted ceilings. Strange, bioluminescent moss casts a faint, blue-green glow on walls carved with reliefs of a forgotten sea god.

The goal of this act is to unseal the grand doors to the main sanctuary. Over the main archway leading deeper into the halls, a hastily carved runic sign is visible:

ᛒᛖᚹᚪᚱᛖ ᚦᛖ ᛞᛟᛈ  
(BEWARE THE DEEP)

**Journals Discovered:**

* **On a Lectern in the Narthex (The High Priest's Formal Record):**7th Day of the Waning Moon. The sea churns with an unholy temper. The god is displeased. The faith of the flock wavers, and whispers of old heresies have returned. I have commissioned the Tide-Binder Kael, a man of secular mind but unparalleled skill, to reinforce the Great Seawalls. Let them stand as a testament to our enduring faith.  
  14th Day. Kael’s work is complete, yet the sea’s anger does not abate. He speaks of pressures and forces beyond his comprehension. I have told him it is a matter of faith, not physics. We shall begin preparations for the Great Hymn of Appeasement. Its holy resonance shall calm the very heart of the ocean.  
* **In a Flooded Side-Chapel, clutched by a skeletal hand (The Tide-Binder's Log):**Log Entry 42\. The High Priest is a fool. A pious, well-meaning fool, but a fool nonetheless. The seawalls are perfect, yet they groan as if the sea itself is trying to pull them apart from within. The pressure readings make no sense. It is a resonant frequency, something deep within the Cathedral's foundation is… singing.  
  Log Entry 45\. I have installed three emergency release valves. If the pressure becomes critical, they can equalize the seawalls. I tried to explain this to Theron, but he waved me away, calling them my "valves of little faith." He insisted on consecrating them himself, as if his prayers could hold back the ocean better than two-hundred tons of reinforced granite.

### **Act II: The Resonant Deeps**

After activating the release valves, the grand doors shudder open, revealing the breathtaking and terrifying main sanctuary. The chamber is vast enough to hold a storm cloud. The ghostly light of the beacon from the tower high above filters down through the deep water, illuminating colossal statues and sending shifting god-rays through the gloom. The air hums with a palpable, ancient grief.

Near the sabotaged sea-gate where the Tide-Binder's body lies, a single, defiant message is scratched into the stone with what looks like a shard of metal:

ᚠᚪᛁᚦ ᛁᛋ ᚦᛖ ᛏᚱᚪᛈ  
(FAITH IS THE TRAP)

**Journals Discovered:**

* **Hidden beneath a collapsed altar (The High Priest's Private Journal):**The god does not answer\! The Hymn must be our salvation. That heretic, Lyra, preaches blasphemy in the shadows, claiming the Heart of the Sea is not a divine gift, but a tool we hoard. She turns the acolytes against me with whispers of a new age. I have excommunicated her, but the poison has spread. They do not understand. The Great Hymn is not for the sea god. It is to awaken the Cathedral's own spirit, to create a sanctuary of power that no god or man can ever assail\!  
* **In the Scriptorium, a sheaf of letters tied with ribbon (Letters from the Acolyte Elara):**My Dearest Finn, You would not believe the sermons of Lyra\! She says the High Priest has lied to us. The Heart of the Sea is not a symbol, but a source of limitless energy\! She says we can use it to warm the very oceans, to grow fields of luminous kelp, to build a paradise beneath the waves\! She plans to disrupt the High Priest’s Hymn and claim the Heart for all of us. I am frightened, Finn, but I am also filled with such hope.  
  (Final, tear-stained letter) Finn, the Hymn has begun. The whole cathedral is shaking. It is not a song, it is a scream\! Lyra has made her move. I see cracks forming in the great windows. The stones… the stones are weeping…  
* **Near a sabotaged sea-gate, beside the crushed skeleton of the Tide-Binder:***(A frantic, final scrawl on a slate tablet)* Sabotage\! The main release valve… it has been deliberately jammed. Someone wants the sea to come in\! The resonance from the Hymn… it’s the exact frequency that will shatter the foundations\! I must warn Theron\! They are turning their song into a weapon\! They have doomed us all\!  
* **In the desecrated crypts, on the body of Lyra, the Heretic:**My confession. I saw a corrupt priesthood, hoarding power while the people on the surface starved. The Heart was our birthright. My calculations were precise. I would disrupt Theron's ritual, sever his control, and channel the Heart’s energy myself. I did not seek destruction. I sought liberation. But his faith… and my science… they met like two warring seas. The energy backlash… it was more than I could have ever imagined. I did not free them. I have only built them a tomb. May the sea have mercy on my soul, for I deserve none.

### **Act III: The Silent Heart**

With the Hymnal Resonators silenced, the psychic storm abates, and the way up the central tower is clear. The ascent is surreal. Gravity seems to warp, and silent, ghostly scenes of the Cathedral's final moments play out on the walls around you.

Just before the final door to the Chancel of the Beacon, a perfectly preserved mosaic on the floor depicts three figures: one fading into nothing, one becoming a star, and one walking into a chaotic storm. Beneath it is a single, clear inscription in the Tidal Futhark:

ᚩᚾᛖ ᚹᛁᛚᛚ ᚱᛖᛗᚪᛁᚾ  
(ONE WILL REMAIN)

You enter the Chancel. The chamber is impossibly, unnaturally dry and silent. In the center, floating in a sphere of calm air, is the Heart of the Sea—a colossal, pearl-like orb, as large as a house. A great, weeping crack runs across its surface, leaking a soft, sorrowful light. This is the source of the beacon.

Floating before it is the translucent spirit of High Priest Theron. Chained to the Heart itself by shackles of pure light is the kneeling, spectral form of Lyra.

Theron turns to you, his voice a dry whisper across a thousand years.

"So, the echo of my grief has finally found its source. You are of my blood. The Dissonance you feel is my own eternal sorrow, calling to you through time."

He explains everything. The cataclysm did not just drown the Cathedral; it trapped them in a bubble of fractured time. He has spent centuries using his fading will to hold the cracked Heart together, preventing a second, more devastating explosion. He has focused all the sorrow, all the pain, into the beacon—a final, desperate prayer for a successor. Lyra, whose ambition triggered the disaster, is bound to the Heart as a living anchor, her life force a seal upon its wound.

He tells you that your arrival gives them a chance for release, and presents you with a choice.

**The Final Choice:**

1. **Extinguish the Light (The Way of Mercy):** You can use your lantern's pure, ancestral flame to overload the Heart. This will shatter it completely, releasing Theron, Lyra, and all the Drowned Sorrows into the final peace of oblivion. The light will go out, the Cathedral will fall truly silent, and the sea will claim it at last. Your Temporal Dissonance will vanish, the ache in your soul finally healed, leaving you fully mortal and truly alone.  
2. **Contain the Light (The Way of Duty):** You can take the High Priest's place. Your bloodline makes you the perfect candidate. You will become the new Warden of the Heart, merging your spirit with the Cathedral to contain its sorrow. It is an eternal sentence, a sacrifice to maintain the balance. You will become a ghost, a phantom of time, and the beacon will continue to shine, a warning and a lament for all ages to come.  
3. **Liberate the Light (The Way of Chaos):** You can fulfill Lyra's original vision. Using your knowledge of the rituals and the Tide-Binder's science, you can shatter Lyra's chains and heal the Heart's wound, but in doing so, unleash its controlled power into the world. The consequences are unknown—a new age of magic, a weapon of terrible power, or a force that could heal the blighted world above. Lyra's spirit would be freed, her ambition vindicated, and you would become the human conduit for this awesome, unpredictable new dawn.

Your choice will determine the final fate of the Sunken Cathedral and will be reflected in the world you return to… if you return at all.

### **Epilogues: The World After**

The final scene of the game depends entirely on the choice you make in the Heart of the Cathedral.

**If you chose The Way of Mercy:**

You watch as your lantern's flame consumes the great pearl. For a moment, there is a light brighter than the sun, followed by an absolute, peaceful silence. The spirits of Theron and Lyra give you a final, grateful nod before dissolving into motes of light. You feel the ache in your soul—the Temporal Dissonance—vanish like a lifted weight. The water rushes in, and you are gently deposited on the shores beside your lighthouse as the sun rises. The Cathedral is gone, truly gone, as if it never existed. The sea is calm. For the first time in your life, you feel ordinary. You are no longer a Lamplighter, for there are no more lights to tend. You are simply a person, free to walk away from the lonely coast, your duty fulfilled, your future your own. The world is as it was, a little less magical, a little more mundane, and you are finally at peace within it.

**If you chose The Way of Duty:**

You step forward and place your hand upon the Heart. A blinding light envelops you as your mortal form dissolves. You have become one with the Cathedral. The spirits of Theron and Lyra, their duty passed on, finally fade into oblivion. You are now the Warden. From your lonely lighthouse on the coast, a new, steady light now shines—your own. Fishermen for generations to come will speak of the Ghost Light of the Cursed Coast, a beacon that seems to watch over them, its sorrowful pulse a constant, comforting presence. You have sacrificed your life to become a legend, a silent guardian bound to the deep, your vigil eternal. The world remains unchanged, its great tragedy contained, its balance maintained by your unending sacrifice.

**If you chose The Way of Chaos:**

You shatter Lyra's chains. As her spirit is freed, she laughs, a sound of pure, triumphant energy. Together, you channel your knowledge into the Heart. The crack on its surface heals, and it begins to glow with a vibrant, world-altering power. The Cathedral rises from the waves, not as a ruin, but as a gleaming, impossible structure of pearl and light. The energy of the Heart washes over the world. The tides shift. Strange, luminous plants begin to grow on the blighted lands. Old magics, long dormant, reawaken. You stand beside Lyra, no longer just a Lamplighter, but the co-architect of a new and unpredictable age. You have brought magic back to a world that has forgotten it, but with it comes chaos, conflict, and wonder in equal measure. Your future, and the world's, is a brilliant, terrifying, and glorious unknown.