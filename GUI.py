import sys
import random
import string
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QSpinBox, QStackedWidget, QListWidget, 
                             QLineEdit, QListWidgetItem, QDialog, QRadioButton, QButtonGroup,
                             QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor

import Partie
import TP5
import corrige


class GridCell(QPushButton):
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.state = 'water'
        self.ship_index = None  # Track which ship occupies this cell
        self.setFixedSize(40, 40)
        self.update_style()
    
    def update_style(self):
        styles = {
            'water': 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0d47a1, stop:1 #1565c0); border: none; color: white;',
            'ship': 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2e7d32, stop:1 #43a047); border: none; color: white; font-weight: bold;',
            'hit': 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #c62828, stop:1 #e53935); border: none; color: white; font-weight: bold;',
            'miss': 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9e9e9e, stop:1 #bdbdbd); border: none; color: white;',
            'sunk': 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #212121); border: none; color: white; font-weight: bold;'
        }
        self.setStyleSheet(styles[self.state])


class Grid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cells = {}
        self.init_grid()
    
    def init_grid(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)  # No spacing between rows
        layout.setContentsMargins(10, 10, 10, 10)
        
        for row in range(10):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(0)  # No spacing between columns
            
            for col in range(10):
                cell = GridCell(row, col)
                self.cells[(row, col)] = cell
                row_layout.addWidget(cell)
            
            layout.addLayout(row_layout)
        
        self.setLayout(layout)
        self.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a237e, stop:1 #283593); border: 2px solid #3949ab; border-radius: 8px;')


class OrientationDialog(QDialog):
    """Modal dialog for selecting ship orientation"""
    def __init__(self, ship_name, possible_orientations, parent=None):
        super().__init__(parent)
        self.selected_orientation = None
        self.orientation_names = {
            'N': '⬆ North (Up)',
            'S': '⬇ South (Down)',
            'E': '➡ East (Right)',
            'O': '⬅ Ouest (Left)'
        }
        self.init_ui(ship_name, possible_orientations)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
    def init_ui(self, ship_name, possible_orientations):
        self.setWindowTitle('Choose Orientation')
        self.setStyleSheet('background: #1e1e2e; color: white; border: 2px solid #3949ab;')
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title = QLabel(f'Select orientation for {ship_name}')
        title.setStyleSheet('color: white; font-size: 16px; font-weight: 600;')
        layout.addWidget(title)
        
        # Radio buttons for orientations
        button_group = QButtonGroup(self)
        for i, orient in enumerate(possible_orientations):
            radio = QRadioButton(self.orientation_names.get(orient, orient))
            # Style radio button with white text when selected
            radio.setStyleSheet("""
                QRadioButton {
                    color: #888888;
                    font-size: 14px;
                    padding: 6px;
                }
                QRadioButton:checked {
                    color: white;
                    font-weight: bold;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }
                QRadioButton::indicator:checked {
                    background: #4caf50;
                }
            """)
            radio.toggled.connect(lambda checked, o=orient: self.on_orientation_selected(o, checked))
            button_group.addButton(radio, i)
            layout.addWidget(radio)
            if i == 0:
                radio.setChecked(True)
        
        # Confirm button
        confirm_btn = QPushButton('Confirm Placement')
        confirm_btn.setFixedHeight(44)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4caf50, stop:1 #66bb6a);
                border: 1px solid #66bb6a;
                border-radius: 12px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #66bb6a, stop:1 #81c784);
            }
        """)
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
        
        self.setLayout(layout)
        self.setFixedWidth(300)
        
    def on_orientation_selected(self, orientation, checked):
        if checked:
            self.selected_orientation = orientation
    
    def get_orientation(self):
        return self.selected_orientation


class BattleshipGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_mode = None  # Track current game mode: 'ai', 'lan', 'battle_royale'
        self.ai_data = None  # Store AI player data for P vs AI mode
        self.player_turn = True  # Track whose turn it is
        self.init_ui()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            # ESC key to exit fullscreen/close game
            self.close()
        else:
            super().keyPressEvent(event)
    
    def init_ui(self):
        self.setWindowTitle('Battleship')
        
        # Keep window maximized throughout
        self.showMaximized()
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 20, 30))
        self.setPalette(palette)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_page = self.build_welcome_page()
        self.room_options_page = self.build_room_options_page()
        self.create_room_page = self.build_create_room_page()
        self.join_room_page = self.build_join_room_page()
        self.placement_page = self.build_placement_page()
        self.game_page = self.build_game_page()

        self.stack.addWidget(self.welcome_page)
        self.stack.addWidget(self.room_options_page)
        self.stack.addWidget(self.create_room_page)
        self.stack.addWidget(self.join_room_page)
        self.stack.addWidget(self.placement_page)
        self.stack.addWidget(self.game_page)

        self.stack.setCurrentWidget(self.welcome_page)
        
    def create_button(self, text, handler=None):
        btn = QPushButton(text)
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2196f3, stop:1 #42a5f5);
                border: 1px solid #64b5f6;
                border-radius: 12px;
                color: white;
                font-size: 15px;
                padding: 8px 18px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #42a5f5, stop:1 #64b5f6);
            }
            QPushButton:pressed {
                background: #1e88e5;
            }
        """)
        if handler:
            btn.clicked.connect(handler)
        return btn

    def build_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        title = QLabel('Welcome to Battleship')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('color: white; font-size: 28px; font-weight: 700; letter-spacing: 1px;')
        subtitle = QLabel('Pick your battle mode to begin')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet('color: #b0bec5; font-size: 16px;')

        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(14)
        btn_ai = self.create_button('P Vs AI', self.start_ai)
        btn_pvp = self.create_button('P Vs P', lambda: self.go_room_options('pvp'))
        btn_br = self.create_button('Battle Royale', lambda: self.go_room_options('br'))
        buttons_layout.addWidget(btn_ai)
        buttons_layout.addWidget(btn_pvp)
        buttons_layout.addWidget(btn_br)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(buttons_layout)
        page.setLayout(layout)
        return page

    def build_room_options_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)
        label = QLabel('Multiplayer Lobby')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet('color: white; font-size: 24px; font-weight: 600; letter-spacing: 0.6px;')
        btn_join = self.create_button('Join Room', self.open_join_room)
        btn_create = self.create_button('Create Room', self.open_create_room)
        btn_back = self.create_button('Back', lambda: self.stack.setCurrentWidget(self.welcome_page))
        layout.addWidget(label)
        layout.addWidget(btn_join)
        layout.addWidget(btn_create)
        layout.addWidget(btn_back)
        page.setLayout(layout)
        return page

    def build_create_room_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)

        label = QLabel('Host Room')
        label.setStyleSheet('color: white; font-size: 22px; font-weight: 600;')

        self.room_code_label = QLabel()
        self.room_code_label.setStyleSheet('color: #90caf9; font-size: 20px; font-weight: 700;')

        self.host_player_list = QListWidget()
        self.host_player_list.setStyleSheet('background: #0e1623; color: white; border: 1px solid #1e2a3a; border-radius: 8px; padding: 6px;')
        self.host_player_list.setFixedHeight(180)

        self.host_count_label = QLabel('Players joined: 0')
        self.host_count_label.setStyleSheet('color: #cfd8dc; font-size: 14px;')

        begin_btn = self.create_button('Begin', self.start_game_from_host)
        back_btn = self.create_button('Back', lambda: self.stack.setCurrentWidget(self.room_options_page))

        layout.addWidget(label)
        layout.addWidget(self.room_code_label)
        layout.addWidget(self.host_count_label)
        layout.addWidget(self.host_player_list)
        layout.addWidget(begin_btn)
        layout.addWidget(back_btn)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def build_join_room_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)

        label = QLabel('Join a Room')
        label.setStyleSheet('color: white; font-size: 22px; font-weight: 600;')

        self.available_rooms = QListWidget()
        self.available_rooms.setStyleSheet('background: #0e1623; color: white; border: 1px solid #1e2a3a; border-radius: 8px; padding: 6px;')
        self.available_rooms.setFixedHeight(180)

        manual_label = QLabel('Enter code or IP:')
        manual_label.setStyleSheet('color: #cfd8dc; font-size: 14px;')
        self.manual_code = QLineEdit()
        self.manual_code.setPlaceholderText('Enter code or IP provided by host')
        self.manual_code.setStyleSheet('background: #0e1623; color: white; border: 1px solid #1e2a3a; border-radius: 8px; padding: 10px;')

        join_btn = self.create_button('Join', self.join_selected_room)
        back_btn = self.create_button('Back', lambda: self.stack.setCurrentWidget(self.room_options_page))

        layout.addWidget(label)
        layout.addWidget(self.available_rooms)
        layout.addWidget(manual_label)
        layout.addWidget(self.manual_code)
        layout.addWidget(join_btn)
        layout.addWidget(back_btn)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def build_game_page(self):
        page = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Turn indicator
        self.turn_label = QLabel('Your Turn')
        self.turn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_label.setStyleSheet('color: #4caf50; font-size: 20px; font-weight: bold; padding: 15px;')
        main_layout.addWidget(self.turn_label)

        # Opponent grids area with proper spacing
        opponents_container = QWidget()
        self.opponents_layout = QVBoxLayout()
        self.opponents_layout.setSpacing(10)
        self.opponents_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        opponents_container.setLayout(self.opponents_layout)
        
        self.opponent_grids = []

        # Player grid with proper spacing
        self.player_grid = Grid()
        
        player_container = QWidget()
        player_layout = QVBoxLayout()
        player_layout.setSpacing(10)
        player_title = QLabel('Your Fleet')
        player_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_title.setStyleSheet('color: #90caf9; font-size: 16px; font-weight: bold; padding: 10px;')
        player_layout.addWidget(player_title)
        player_layout.addWidget(self.player_grid, alignment=Qt.AlignmentFlag.AlignCenter)
        player_container.setLayout(player_layout)

        # Add with stretch to distribute space evenly
        main_layout.addWidget(opponents_container, stretch=1)
        main_layout.addStretch(1)
        main_layout.addWidget(player_container, stretch=1)

        page.setLayout(main_layout)
        return page

    def build_placement_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('Place Your Ships')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('color: white; font-size: 24px; font-weight: 700;')
        
        # Current ship info section
        ship_info_layout = QHBoxLayout()
        ship_info_layout.setSpacing(20)
        
        # Ship name and details
        self.current_ship_label = QLabel('Current Ship: [None]')
        self.current_ship_label.setStyleSheet('color: #90caf9; font-size: 16px; font-weight: 600;')
        
        # Ship visual representation
        self.ship_visual = QLabel()
        self.ship_visual.setStyleSheet('background: transparent; color: #4caf50; font-size: 24px; font-family: monospace;')
        self.ship_visual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ship_visual.setMinimumWidth(200)
        
        ship_info_layout.addWidget(self.current_ship_label)
        ship_info_layout.addWidget(self.ship_visual)
        ship_info_layout.addStretch()
        
        # Instructions
        instructions = QLabel('Click on a grid cell to select position, then choose orientation')
        instructions.setStyleSheet('color: #cfd8dc; font-size: 13px;')
        
        # Grid
        self.placement_grid = Grid()
        
        # Buttons
        btn_layout = QHBoxLayout()
        back_btn = self.create_button('Back', self.cancel_placement)
        btn_layout.addStretch()
        btn_layout.addWidget(back_btn)
        
        layout.addWidget(title)
        layout.addLayout(ship_info_layout)
        layout.addWidget(instructions)
        layout.addWidget(self.placement_grid, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(btn_layout)
        
        page.setLayout(layout)
        
        # State for placement
        self.placement_model_grid = None
        self.ships_list = None
        self.current_ship_index = 0
        self.player_data = None
        
        return page

    def start_ai(self):
        self.game_mode = 'ai'  # Set game mode to AI
        # Create AI opponent data
        self.ai_data = Partie.Generer_Joueur(False, nombre_d_adversaires=1)
        self.init_placement()
        self.previous_page = self.welcome_page
        self.stack.setCurrentWidget(self.placement_page)

    def go_room_options(self, mode):
        self.current_mode = mode
        self.stack.setCurrentWidget(self.room_options_page)

    def open_create_room(self):
        self.room_code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))
        self.room_code_label.setText(f'Room code: {self.room_code}')
        self.host_player_list.clear()
        for name in ['Host']:  
            self.host_player_list.addItem(QListWidgetItem(name))
        self.host_count_label.setText(f'Players joined: {self.host_player_list.count()}')
        self.stack.setCurrentWidget(self.create_room_page)

    def open_join_room(self):
        self.available_rooms.clear()
        sample_rooms = ['AX93QZ', 'BR5562', 'NAVY12', 'SEA7IP']
        for code in sample_rooms:
            self.available_rooms.addItem(QListWidgetItem(f'Room {code}'))
        self.stack.setCurrentWidget(self.join_room_page)

    def start_game_from_host(self):
        self.init_placement()
        self.previous_page = self.create_room_page
        self.stack.setCurrentWidget(self.placement_page)

    def join_selected_room(self):
        selected = self.available_rooms.currentItem()
        code = self.manual_code.text().strip()
        if selected and not code:
            code = selected.text().split()[-1]
        if not code:
            if self.available_rooms.count() > 0:
                code = self.available_rooms.item(0).text().split()[-1]
        self.joined_room_code = code
        self.init_placement()
        self.previous_page = self.join_room_page
        self.stack.setCurrentWidget(self.placement_page)

    # OLD METHODS - Not used in AI mode, kept for future multiplayer modes
    # def rebuild_opponent_grids(self, count):
    #     for grid in self.opponent_grids:
    #         self.opponents_layout.removeWidget(grid)
    #         grid.setParent(None)
    #     self.opponent_grids = []
    #     for _ in range(count):
    #         grid = Grid()
    #         self.opponent_grids.append(grid)
    #         self.opponents_layout.addWidget(grid)

    # def shoot_all_grids(self):
    #     pass

    # ---- Ship Placement Methods ----
    def init_placement(self):
        """Initialize placement using data from Generer_Joueur()"""
        # Determine number of opponents based on game mode
        num_opponents = 1  # Default for AI
        if hasattr(self, 'opponent_count'):
            num_opponents = self.opponent_count.value()
        
        # Create empty grids - we'll use GUI-based placement instead of Placer_Bateaux
        # which expects console input
        empty_grid = Partie.Generer_Grille(10)
        ships_list = Partie.Generer_Bateaux()
        grilles_tirs = [Partie.Generer_Grille(10) for _ in range(num_opponents)]
        
        # Store player data structure
        self.player_data = {
            "grille": empty_grid,  # Will be filled by GUI placement
            "bateaux": ships_list,
            "tirs": grilles_tirs,
            "score": 0
        }
        
        self.placement_model_grid = self.player_data["grille"]
        self.ships_list = self.player_data["bateaux"]
        self.current_ship_index = 0
        self.placed_ships = []
        
        # Reset grid UI
        for cell in self.placement_grid.cells.values():
            cell.state = 'water'
            cell.ship_index = None
            cell.update_style()
            # Clear previous connections
            try:
                cell.clicked.disconnect()
            except TypeError:
                pass
        
        # Connect cell clicks
        for cell in self.placement_grid.cells.values():
            cell.clicked.connect(lambda checked=False, c=cell: self.on_cell_clicked(c))
        
        # Show first ship info
        self.update_ship_display()

    def update_ship_display(self):
        """Update the display of the current ship being placed"""
        if self.current_ship_index < len(self.ships_list):
            ship = self.ships_list[self.current_ship_index]
            ship_name = ship['nom']
            ship_size = ship['taille']
            
            # Update ship name label
            self.current_ship_label.setText(f'Current Ship: {ship_name.upper()} ({ship_size} cells)')
            
            # Create visual representation of ship
            ship_visual = ' '.join(['■'] * ship_size)
            self.ship_visual.setText(ship_visual)
        else:
            # All ships placed
            self.current_ship_label.setText('All Ships Placed!')
            self.ship_visual.setText('✓')

    def on_cell_clicked(self, cell):
        """Handle cell click during ship placement"""
        if self.current_ship_index >= len(self.ships_list):
            # All ships placed, go to game
            self.finish_placement()
            return
        
        ship = self.ships_list[self.current_ship_index]
        row, col = cell.row, cell.col
        
        # Convert row/col to coordinates like "B6"
        coords = chr(row + 65) + str(col + 1)
        
        # Check possible orientations for this position using TP5.Verif_Placement
        possible_orientations = TP5.Verif_Placement(
            self.placement_model_grid,
            coords, 
            ship['taille']
        )
        
        if not possible_orientations:
            # No valid placement here
            print(f"Cannot place {ship['nom']} at {coords}")
            return
        
        # Show orientation selection dialog
        dialog = OrientationDialog(ship['nom'], possible_orientations, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            orientation = dialog.get_orientation()
            if orientation:
                self.place_ship(coords, orientation, self.current_ship_index)

    def place_ship(self, coords, orientation, ship_index):
        """Place ship on grid and update state"""
        ship = self.ships_list[ship_index]
        
        # Place on model grid
        self.placement_model_grid = TP5.Placer_Bateau(
            self.placement_model_grid,
            ship_index,
            coords,
            orientation,
            ship['taille']
        )
        
        # Update UI grid to show ship
        for r in range(10):
            for c in range(10):
                if self.placement_model_grid[r][c] == ship_index + 2:
                    self.placement_grid.cells[(r, c)].state = 'ship'
                    self.placement_grid.cells[(r, c)].ship_index = ship_index
                    self.placement_grid.cells[(r, c)].update_style()
        
        self.placed_ships.append({
            'index': ship_index,
            'name': ship['nom'],
            'coords': coords,
            'orientation': orientation
        })
        
        # Move to next ship
        self.current_ship_index += 1
        self.update_ship_display()
        
        # Check if all ships placed
        if self.current_ship_index >= len(self.ships_list):
            self.finish_placement()

    def finish_placement(self):
        """All ships placed, proceed to game"""
        # Update player data with placed grid
        self.player_data["grille"] = self.placement_model_grid
        
        # Setup game based on mode
        if self.game_mode == 'ai':
            # Setup for P vs AI mode
            self.setup_ai_game()
        else:
            # Setup for multiplayer modes (to be implemented later)
            pass
        
        self.stack.setCurrentWidget(self.game_page)
    
    def setup_ai_game(self):
        """Setup the game page for P vs AI mode"""
        # Clear existing opponent grids
        for grid in self.opponent_grids:
            self.opponents_layout.removeWidget(grid)
            grid.setParent(None)
        self.opponent_grids = []
        
        # Add opponent title
        opponent_title = QLabel('Computer Fleet')
        opponent_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        opponent_title.setStyleSheet('color: #ef5350; font-size: 14px; font-weight: bold;')
        
        # Create single opponent grid for AI
        ai_grid = Grid()
        self.opponent_grids.append(ai_grid)
        
        # Add grid label container
        opponent_container = QWidget()
        opponent_layout = QVBoxLayout()
        opponent_layout.addWidget(opponent_title)
        opponent_layout.addWidget(ai_grid)
        opponent_container.setLayout(opponent_layout)
        
        self.opponents_layout.addWidget(opponent_container)
        
        # Connect cell clicks for shooting
        for (row, col), cell in ai_grid.cells.items():
            cell.clicked.connect(lambda checked=False, r=row, c=col: self.player_shoot(r, c))
        
        # Update player grid to show ships
        for r in range(10):
            for c in range(10):
                v = self.placement_model_grid[r][c]
                if v >= 2:
                    self.player_grid.cells[(r, c)].state = 'ship'
                    self.player_grid.cells[(r, c)].ship_index = v - 2
                    self.player_grid.cells[(r, c)].update_style()
        
        # Initialize turn
        self.player_turn = True
        self.turn_label.setText('Your Turn - Click on enemy grid to fire!')
        self.turn_label.setStyleSheet('color: #4caf50; font-size: 18px; font-weight: bold; padding: 10px;')

    
    def player_shoot(self, row, col):
        """Handle player shooting at AI grid"""
        if not self.player_turn:
            return
        
        ai_grid = self.opponent_grids[0]
        cell = ai_grid.cells[(row, col)]
        
        # Check if already shot here
        if cell.state in ['hit', 'miss', 'sunk']:
            return
        
        # Convert to coords format
        coords = chr(row + 65) + str(col + 1)
        
        # Execute shot using corrige.Tir
        result = corrige.Tir(
            self.ai_data["grille"],
            self.player_data["tirs"][0],
            coords,
            self.ai_data["bateaux"]
        )
        
        # Update cell based on result
        if result == -1:  # Already shot (shouldn't happen with our check above)
            return
        elif result == 0:  # Miss
            cell.state = 'miss'
            cell.setText('○')
            cell.update_style()
            # Switch to AI turn
            self.player_turn = False
            self.turn_label.setText('Computer is thinking...')
            self.turn_label.setStyleSheet('color: #ff9800; font-size: 18px; font-weight: bold; padding: 10px;')
            QTimer.singleShot(1000, self.computer_turn)
        elif result == 1:  # Hit
            cell.state = 'hit'
            cell.setText('✖')
            cell.update_style()
            # Player continues (hits again)
            self.turn_label.setText('HIT! Your turn again - Click to fire!')
        elif result == 2:  # Sunk
            cell.state = 'hit'
            cell.setText('✖')
            cell.update_style()
            # Mark entire ship as sunk
            self.mark_sunk_ship(ai_grid, self.ai_data["grille"])
            # Check if player won
            if corrige.Gagne(self.ai_data["bateaux"]):
                self.show_win_message("Congratulations! You Win!")
            else:
                self.turn_label.setText('SHIP SUNK! Your turn again - Click to fire!')
    
    def computer_turn(self):
        """AI takes a shot"""
        if self.player_turn:
            return
        
        # Get AI shot coordinates
        coords = TP5.Ordi_Coords(self.ai_data["tirs"][0], self.player_data["bateaux"])
        row, col = corrige.Coords2Nums(coords)
        
        # Execute shot
        result = corrige.Tir(
            self.player_data["grille"],
            self.ai_data["tirs"][0],
            coords,
            self.player_data["bateaux"]
        )
        
        # Update player's grid
        player_cell = self.player_grid.cells[(row, col)]
        
        if result == 0:  # Miss
            player_cell.state = 'miss'
            player_cell.setText('○')
            player_cell.update_style()
            # Switch back to player turn
            self.player_turn = True
            self.turn_label.setText('Computer MISSED! Your turn - Click to fire!')
            self.turn_label.setStyleSheet('color: #4caf50; font-size: 18px; font-weight: bold; padding: 10px;')
        elif result == 1:  # Hit
            player_cell.state = 'hit'
            player_cell.setText('✖')
            player_cell.update_style()
            # AI continues
            self.turn_label.setText('Computer HIT! Computer shoots again...')
            QTimer.singleShot(1000, self.computer_turn)
        elif result == 2:  # Sunk
            player_cell.state = 'hit'
            player_cell.setText('✖')
            player_cell.update_style()
            # Mark ship as sunk
            self.mark_sunk_ship(self.player_grid, self.player_data["grille"])
            # Check if computer won
            if corrige.Gagne(self.player_data["bateaux"]):
                self.show_win_message("Computer Wins! Better luck next time.")
            else:
                self.turn_label.setText('Computer SUNK YOUR SHIP! Computer shoots again...')
                QTimer.singleShot(1000, self.computer_turn)
    
    def mark_sunk_ship(self, grid, model_grid):
        """Mark all cells of a sunk ship as black"""
        # Get the correct bateaux list
        if grid == self.opponent_grids[0]:
            bateaux = self.ai_data["bateaux"]
        else:
            bateaux = self.player_data["bateaux"]
        
        # Check all ships and mark sunk ones
        for ship_index in range(len(bateaux)):
            ship = bateaux[ship_index]
            # If this ship is fully sunk
            if ship["touchés"] == ship["taille"]:
                # Mark all cells of this ship as sunk (black)
                ship_value = ship_index + 2  # Ships are indexed 2-6 in the grid
                for r in range(10):
                    for c in range(10):
                        # Check if this cell contains this ship (positive or negative)
                        cell_value = model_grid[r][c]
                        if abs(cell_value) == ship_value:
                            cell = grid.cells[(r, c)]
                            cell.state = 'sunk'
                            cell.setText('■')
                            cell.update_style()
                            cell.repaint()  # Force immediate visual update
    
    def show_win_message(self, message):
        """Show win/lose message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Game Over")
        msg_box.setText(message)
        msg_box.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: #1e1e2e;
                color: white;
                min-width: 400px;
                min-height: 200px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 18px;
                padding: 20px;
            }
            QPushButton {
                background: #2196f3;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 100px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #42a5f5;
            }
        """)
        msg_box.exec()
        # Return to welcome page while maintaining maximized state
        self.stack.setCurrentWidget(self.welcome_page)
        self.showMaximized()
    
    def cancel_placement(self):
        """Cancel placement and return to previous page"""
        prev = getattr(self, 'previous_page', self.welcome_page)
        self.stack.setCurrentWidget(prev)


def main():
    app = QApplication(sys.argv)
    window = BattleshipGame()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()