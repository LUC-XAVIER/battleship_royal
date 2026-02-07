# Ship Placement Interface - Implementation Guide

## Overview
The ship placement interface is now fully integrated with the game workflow. After joining/creating a room or selecting P Vs AI, players proceed directly to the placement phase where they can strategically place their ships using a grid-based interface with modal orientation dialogs.

---

## Workflow

### Navigation Flow
```
Welcome Page
    ↓
    ├─→ P Vs AI ──→ Placement Page
    ├─→ P Vs P ──→ Room Options ──→ Create Room ──→ Placement Page
    │                          ├─→ Join Room ──→ Placement Page
    └─→ Battle Royale
```

### Back Button Added
- **Multiplayer Lobby** now has a **Back** button to return to Welcome
- Allows users to change game mode if they selected incorrectly

---

## Placement Interface Design

### Main Components

#### 1. **Placement Grid (10×10)**
- Interactive grid where players click to select ship positions
- Visual feedback:
  - **Blue**: Empty water (available for placement)
  - **Green**: Placed ships
  - **Red/Dark**: Hit/Miss marks (in-game use)

#### 2. **Orientation Modal Dialog**
When a player clicks a grid cell:
1. System checks possible orientations using `TP5.Verif_Placement()`
2. Modal dialog appears showing available options:
   - **⬆ North (Up)** - Ship extends upward
   - **⬇ South (Down)** - Ship extends downward
   - **➡ East (Right)** - Ship extends rightward
   - **⬅ Ouest (Left)** - Ship extends leftward
3. Player selects orientation with radio button
4. Player clicks **"Confirm Placement"** button
5. Modal cannot be closed without confirming

#### 3. **Ship Information**
- Current ship being placed is shown in console output
- Ships must be placed in order:
  1. Porte-Avion (5 cells)
  2. Croiseur (4 cells)
  3. Contre-Torpilleur 1 (3 cells)
  4. Contre-Torpilleur 2 (3 cells)
  5. Sous-Marin (2 cells)

---

## Key Functions Used

### From `TP5.py`
```python
# Verify valid placements for a position and ship size
TP5.Verif_Placement(grille, coords, taille)
→ Returns: String with possible orientations (e.g., "NSEO", "NE", etc.)

# Place a ship on the grid
TP5.Placer_Bateau(grille, ship_index, coords, orientation, taille)
→ Returns: Updated grid with ship placed
```

### From `Partie.py`
```python
# Create empty grid (10×10)
Partie.Generer_Grille(10)
→ Returns: 2D list with all 1s (empty water)

# Generate list of ships with specifications
Partie.Generer_Bateaux()
→ Returns: List of dictionaries with ship info
    {
        'nom': 'porte-avion',
        'taille': 5,
        'touchés': 0
    }
```

### From `corrige.py`
```python
# Convert grid coordinates like "B6" to array indices (1, 5)
corrige.Coords2Nums(position)
→ Used internally by TP5.Placer_Bateau()
```

---

## Placement Algorithm

### Step-by-step Process

1. **Initialize Placement**
   ```
   - Create empty 10×10 grid
   - Load 5 ships list
   - Set current_ship_index = 0
   - Display first ship info
   ```

2. **Wait for Cell Click**
   ```
   - Player clicks a grid cell
   - Convert cell position to coordinates (e.g., row=1, col=5 → "B6")
   ```

3. **Check Valid Orientations**
   ```
   - Call TP5.Verif_Placement(grid, "B6", ship_size)
   - If returns empty string: position invalid, reject
   - If returns "NSE", "NO", etc.: show those options
   ```

4. **Show Modal Dialog**
   ```
   - Display OrientationDialog with radio buttons
   - Only show valid orientations
   - User selects one orientation
   - Modal blocks further interaction until confirmed
   ```

5. **Place Ship**
   ```
   - Call TP5.Placer_Bateau(grid, ship_index, coords, orientation, size)
   - Update UI grid to show ship in green
   - Increment current_ship_index
   ```

6. **Move to Next Ship**
   ```
   - If more ships to place: repeat from Step 2
   - If all ships placed: proceed to game page
   ```

---

## Code Architecture

### New Dialog Class
```python
class OrientationDialog(QDialog):
    """Modal for orientation selection"""
    - init_ui(): Creates radio buttons for each valid orientation
    - get_orientation(): Returns selected orientation character
    - setWindowModality(ApplicationModal): Prevents closing without selection
```

### New Methods in BattleshipGame
```python
init_placement()
    → Initialize grid, ships, reset UI

show_current_ship_info()
    → Display which ship is being placed

on_cell_clicked(cell)
    → Handle grid cell clicks
    → Check valid placements
    → Show orientation dialog

place_ship(coords, orientation, ship_index)
    → Use TP5.Placer_Bateau() to place on model grid
    → Update UI grid cells
    → Move to next ship

finish_placement()
    → Copy placed grid to game page
    → Transition to game

cancel_placement()
    → Return to previous page (room/welcome)
```

---

## Validation & Error Handling

### Valid Placement Checks
1. **Cell occupancy**: Cell must not contain a ship already
2. **Grid boundaries**: Ship cannot extend beyond 10×10 grid
3. **Neighbor collision**: Ships cannot touch (including diagonally)
4. **Direction viability**: Chosen direction must have enough space

### Invalid Placement
- If `Verif_Placement()` returns empty string:
  - No modal shown
  - Cell click ignored
  - Player must choose different cell
  - Example: Cannot place 5-cell ship at J10 (no room going down/right)

---

## Integration with Game State

### Data Structure
Ships are stored in `ships_list` from `Partie.Generer_Bateaux()`:
```python
[
    {'nom': 'porte-avion', 'taille': 5, 'touchés': 0},
    {'nom': 'croiseur', 'taille': 4, 'touchés': 0},
    {'nom': 'contre-torpilleur 1', 'taille': 3, 'touchés': 0},
    {'nom': 'contre-torpilleur 2', 'taille': 3, 'touchés': 0},
    {'nom': 'sous-marin', 'taille': 2, 'touchés': 0}
]
```

### Grid Encoding
- `1`: Empty water
- `2-6`: Ship numbers (2=ship0, 3=ship1, etc.)
- `-1`: Missed shot
- `-2 to -6`: Hit ship cells

---

## User Experience

### Advantages
✓ **Intuitive**: Click cell → choose orientation → place  
✓ **Modal blocking**: Cannot accidentally close or miss selection  
✓ **Validation**: Invalid placements rejected immediately  
✓ **Visual feedback**: Placed ships shown in green  
✓ **Sequential**: Forces proper ship placement order  
✓ **Reversible**: Back button allows returning to room selection  

### Ship Representation
Ships are displayed as:
- **Green cells** on the grid when placed
- **Named in console** when being placed
- Future: Could add ship icons or sprites for visual distinction

---

## Future Enhancements

### Planned Features
1. **Ship Icons**: Replace green cells with actual ship sprites
2. **Multiple Players**: Support `Generer_Joueur(humain)` for each player
3. **Multiplayer Placement**: Sequential placement with network sync
4. **Preview**: Show where ship would be placed before clicking confirm
5. **Rotation Keys**: Allow keyboard shortcuts for orientation selection
6. **Undo**: Let players move already-placed ships

### Code for Future Multiplayer Support
```python
# In Partie.py - Future modification for multiple players:
def Generer_Joueur(humain):
    return {
        "grille": TP5.Placer_Bateaux(grille, bateaux, humain),
        "bateaux": bateaux,
        "tirs": [Generer_Grille(10) for _ in range(num_opponents)],
        "score": 0
    }
```

---

## Testing Checklist

- [x] P Vs AI → Goes to placement page
- [x] P Vs P → Create Room → Goes to placement page
- [x] P Vs P → Join Room → Goes to placement page
- [x] Back button on Multiplayer Lobby works
- [x] Grid displays correctly
- [x] Cell clicks trigger orientation dialog
- [x] Modal dialog shows valid orientations only
- [x] Confirm button places ship and moves to next
- [x] All 5 ships can be placed sequentially
- [x] Game page shows player's placed ships
- [x] Invalid placements are rejected
- [x] Cancel button returns to previous page

---

## Summary

The ship placement interface is now fully functional with:
- ✓ Modal orientation dialogs with radio button selection
- ✓ Integration with TP5.py validation and placement functions
- ✓ Sequential ship placement in proper order
- ✓ Visual grid feedback
- ✓ Back button navigation
- ✓ Non-closeable modal dialogs
- ✓ Proper error handling for invalid placements

Players can now strategically place their fleet before engaging in battle! ⚓

