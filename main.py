import tkinter as tk
from tkinter import messagebox
from heuristic_bot import HeuristicBot
from minimax_bot import MinimaxBot


class CaroGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Cờ Caro")
        self.geometry("600x680")
        self.resizable(False, False)
        self.bot = None   # KHỞI TẠO ở đây tránh lỗi
        self.mode = None
        self.create_mode_selection()

    def create_mode_selection(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Chọn chế độ chơi", font=("Arial", 20))
        label.pack(pady=20)

        btn_pvp = tk.Button(self, text="Player v Player", font=("Arial", 16), width=20,
                            command=lambda: self.start_game("PvP"))
        btn_pvp.pack(pady=10)

        btn_pvh = tk.Button(self, text="Player vs HeuristicBot", font=("Arial", 16), width=20,
                            command=lambda: self.start_game("PvH"))
        btn_pvh.pack(pady=10)
        btn_pvmini = tk.Button(self, text="Player vs Minimax", font=("Arial", 16), width=20,
                       command=lambda: self.start_game("PvMinimax"))
        btn_pvmini.pack(pady=10)
        btn_bot_vs_bot = tk.Button(self, text="Heuristic vs Minimax", font=("Arial", 16), width=20,
                           command=lambda: self.start_game("HvM"))
        btn_bot_vs_bot.pack(pady=10)


        
    def start_game(self, mode):
        self.mode = mode
        self.bot = None  # Reset bot khi bắt đầu
        for widget in self.winfo_children():
            widget.destroy()
        self.create_game_board()

        if mode == "PvH":
            self.bot = HeuristicBot() 
        elif mode == "PvMinimax":
            self.bot = MinimaxBot()
        elif mode == "HvM":
            self.bot_X = HeuristicBot()
            self.bot_O = MinimaxBot()
            self.after(500, self.bot_vs_bot_turn)
    

    def create_game_board(self):
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x")

        self.label_mode = tk.Label(header_frame, text=f"Chế độ: {self.mode}", font=("Arial", 14))
        self.label_mode.pack(side="left", padx=10, pady=5)

        self.label_time = tk.Label(header_frame, text="Thời gian: 0s", font=("Arial", 14))
        self.label_time.pack(side="right", padx=10, pady=5)

        board_frame = tk.Frame(self, bg="black")
        board_frame.pack(padx=10, pady=10)

        self.buttons = []
        self.board = [[' ' for _ in range(15)] for _ in range(15)]
        self.current_player = "X"
        self.game_over = False

        for row in range(15):
            row_buttons = []
            for col in range(15):
                btn = tk.Button(board_frame, width=2, height=1,
                                bg="#00cc44",
                                relief="solid", bd=1,
                                font=("Arial", 12, "bold"),
                                command=lambda r=row, c=col: self.cell_clicked(r, c))
                btn.grid(row=row, column=col, padx=1, pady=1)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.seconds = 0
        self.update_timer()

    def cell_clicked(self, row, col):
        if self.game_over:
            return

        if self.mode == "PvH" and self.current_player == "O":
            return

        if self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            self.buttons[row][col].config(text=self.current_player, fg="white")

            if self.check_winner(row, col):
                self.game_over = True
                messagebox.showinfo("Kết quả", f"Người chơi {self.current_player} thắng!")
                self.create_mode_selection()
                return

            if self.check_draw():
                self.game_over = True
                messagebox.showinfo("Kết quả", "Hòa!")
                self.create_mode_selection()
                return

            # Đổi lượt
            self.current_player = "O" if self.current_player == "X" else "X"

            # Nếu chế độ có bot và đến lượt máy, gọi bot đánh
            if self.mode in ['PvH','PvMinimax'] and self.current_player == 'O':
                self.after(100, self.bot_turn)

    def bot_turn(self):
            if self.game_over or self.bot is None:
                return
        
        
            move = self.bot.get_move(self.board, self.current_player)
        
            if move is None:
                self.game_over = True
                messagebox.showinfo("Kết quả", "Hòa!")
                self.create_mode_selection()
                return

            row, col = move
            self.board[row][col] = self.current_player
            self.buttons[row][col].config(text=self.current_player, fg="red")

            if self.check_winner(row, col):
                self.game_over = True
                messagebox.showinfo("Kết quả", "Máy thắng!")
                self.create_mode_selection()
                return

            if self.check_draw():
                self.game_over = True
                messagebox.showinfo("Kết quả", "Hòa!")
                self.create_mode_selection()
                return

            self.current_player = "X"
    
    def bot_vs_bot_turn(self):
        if self.game_over:
            return

        if self.current_player == "X":
            move = self.bot_X.get_move(self.board, "X")
        else:
            move = self.bot_O.get_move(self.board, "O")

        if move is None:
            self.game_over = True
            messagebox.showinfo("Kết quả", "Hòa!")
            self.create_mode_selection()
            return

        row, col = move
        self.board[row][col] = self.current_player
        self.buttons[row][col].config(text=self.current_player, fg="blue" if self.current_player == "X" else "red")

        if self.check_winner(row, col):
            self.game_over = True
            messagebox.showinfo("Kết quả", f"{self.current_player} thắng!")
            self.create_mode_selection()
            return

        if self.check_draw():
            self.game_over = True
            messagebox.showinfo("Kết quả", "Hòa!")
            self.create_mode_selection()
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self.after(200, self.bot_vs_bot_turn)  # delay nhỏ để xem quá trình

            
    def check_winner(self, row, col):
        def count_dir(r_step, c_step):
            count = 1
            r, c = row + r_step, col + c_step
            while 0 <= r < 20 and 0 <= c < 20 and self.board[r][c] == self.current_player:
                count += 1
                r += r_step
                c += c_step
            r, c = row - r_step, col - c_step
            while 0 <= r < 20 and 0 <= c < 20 and self.board[r][c] == self.current_player:
                count += 1
                r -= r_step
                c -= c_step
            return count

        if count_dir(0, 1) >= 5:
            return True
        if count_dir(1, 0) >= 5:
            return True
        if count_dir(1, 1) >= 5:
            return True
        if count_dir(1, -1) >= 5:
            return True
        return False
    
    def check_draw(self):
        for row in self.board:
            if ' ' in row:
                return False
        return True

    def update_timer(self):
        self.seconds += 1
        if hasattr(self, 'label_time') and self.label_time.winfo_exists():
            self.label_time.config(text=f"Thời gian: {self.seconds}s")
            self.after(1000, self.update_timer)


if __name__ == "__main__":
    app = CaroGame()
    app.mainloop()


