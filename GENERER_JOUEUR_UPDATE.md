# Updated Ship Placement & Player Generation System

## Key Changes Made

### 1. Modified `Generer_Joueur()` in `Partie.py`

**New Signature:**
```python
def Generer_Joueur(humain, nombre_d_adversaires=1):
```

**Parameters:**
- `humain` (bool): Whether the player is human or AI
- `nombre_d_adversaires` (int): Number of opponents (default=1)

**Returns:**
```python
{
    "grille": [10×10 grid with placed ships],
    "bateaux": [5 ships with specifications],
    "tirs": [list of 10×10 grids, one per opponent],  # ← Now a list!
    "score": 0
}
```

**Before:**
```python
"tirs": Generer_Grille(10)  # Single grid
```

**After:**
```python
"tirs": [Generer_Grille(10) for _ in range(nombre_d_adversaires)]  # List of grids
```

### 2. Updated GUI Ship Placement (`testPyQt.py`)

#### Approach Changed:
- **Before**: Called `Placer_Bateaux()` from TP5.py (console-based input)
- **After**: Handle placement entirely in GUI without calling console functions

#### Why:
`Placer_Bateaux()` uses `GUI.Saisie_Coords()` which calls `input()`. In PyQt, this causes:
```
RuntimeError: can't re-enter readline
```

#### Solution:
Use data structure from `Generer_Joueur()` but do placement in GUI:
```python
self.player_data = {
    "grille": Partie.Generer_Grille(10),      # Empty grid
    "bateaux": Partie.Generer_Bateaux(),      # 5 ships
    "tirs": [Partie.Generer_Grille(10) for _ in range(num_opponents)],
    "score": 0
}
```

### 3. Visual Ship Display

**New UI Elements:**

```
┌─────────────────────────────────────────┐
│ Place Your Ships                        │
├─────────────────────────────────────────┤
│ Current Ship: PORTE-AVION (5 cells)     │
│ Visual: ■ ■ ■ ■ ■                      │
│                                         │
│ Click on a grid cell to select position │
│                                         │
│ [10×10 Grid]                            │
│                                         │
│                                  [Back] │
└─────────────────────────────────────────┘
```

**Implementation:**
```python
self.current_ship_label = QLabel('Current Ship: PORTE-AVION (5 cells)')
self.ship_visual = QLabel('■ ■ ■ ■ ■')  # Updated when ship changes
```

**Update Method:**
```python
def update_ship_display(self):
    if self.current_ship_index < len(self.ships_list):
        ship = self.ships_list[self.current_ship_index]
        ship_visual = ' '.join(['■'] * ship['taille'])
        self.current_ship_label.setText(f'Current Ship: {ship["nom"].upper()} ({ship["taille"]} cells)')
        self.ship_visual.setText(ship_visual)
```

### 4. Radio Button Styling (Orientation Dialog)

**Selected Radio Button (White):**
```css
QRadioButton:checked {
    color: white;
    font-weight: bold;
}
```

**Unselected Radio Button (Dark Gray):**
```css
QRadioButton {
    color: #888888;
    font-size: 14px;
}
```

**Result:**
- Selected: White text with bold font ✓
- Unselected: Gray text (less prominent)
- Better visual distinction between active/inactive choices

### 5. Data Flow in Game

```
Welcome Page
    ↓
[Select Mode: P Vs AI / P Vs P / Battle Royale]
    ↓
Placement Page
    ├─ init_placement()
    │   └─ Creates: {grille, bateaux, tirs, score}
    │       where tirs = [grid1, grid2, grid3, ...]
    ├─ display_current_ship()
    │   └─ Shows ship name + visual (■ ■ ■...)
    ├─ on_cell_clicked()
    │   └─ Get possible orientations via TP5.Verif_Placement()
    ├─ OrientationDialog shows choices
    │   └─ Radio buttons (white when selected)
    ├─ place_ship()
    │   └─ Uses TP5.Placer_Bateau() to place on grid
    │       Moves to next ship
    └─ finish_placement()
        └─ Sends player data to game page
```

### 6. Integration with Existing Code

**Still Used:**
- `Partie.Generer_Grille(10)` - Create empty grids
- `Partie.Generer_Bateaux()` - Get ship specifications
- `TP5.Verif_Placement()` - Validate ship placements
- `TP5.Placer_Bateau()` - Place individual ships on grid
- `corrige.Coords2Nums()` - Convert coordinates

**Not Called in GUI:**
- `TP5.Placer_Bateaux()` - Skipped (console-based)
- `GUI.Saisie_Coords()` - Skipped (console input)
- `GUI.Saisie_Car()` - Skipped (console input)

### 7. Benefits of This Approach

✓ **Clean Separation**: Console logic in TP5/GUI.py, GUI logic in PyQt  
✓ **Flexible**: Can support different numbers of opponents  
✓ **Reusable**: `Generer_Joueur()` works for both console and GUI  
✓ **Extensible**: Easy to add network multiplayer (just sync player_data)  
✓ **Type Safe**: Dictionary structure matches expected format  

### 8. Testing Checklist

- [x] P Vs AI → goes to placement
- [x] P Vs P (Create Room) → goes to placement
- [x] P Vs P (Join Room) → goes to placement
- [x] Current ship displayed with name
- [x] Ship visual shows ■ symbols
- [x] Radio buttons styled (white when selected)
- [x] Orientation dialog appears on cell click
- [x] Can place ships sequentially
- [x] All ships placed → game page
- [x] Back button works
- [x] `tirs` is a list of grids (num_opponents)
- [x] No console input conflicts

### 9. Future Multiplayer Support

To support simultaneous multiplayer placement:

```python
# Server side - generate all players
players = [
    Partie.Generer_Joueur(humain=True, nombre_d_adversaires=2),   # Player 1
    Partie.Generer_Joueur(humain=True, nombre_d_adversaires=2),   # Player 2
]

# Each player gets:
# - grille: their own fleet (hidden from others)
# - tirs: [opponent1_grid, opponent2_grid]

# Network: Send placement confirmations when all players ready
```

---

**Summary:** The system is now fully functional with GUI-based ship placement, proper data structures for multiple opponents, and clean separation from console-based code. 🚢⚓

