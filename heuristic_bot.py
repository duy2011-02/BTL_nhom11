# heuristic_bot.py

BOARD_SIZE = 15  # Kích thước bàn cờ

# Các giá trị thể hiện trạng thái ô trên bàn cờ
EMPTY = ' '
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 4 hướng: ngang, dọc, chéo

# Mẫu (pattern) và điểm số tương ứng
PATTERN_SCORES = {
    #bot tấn công
    "xxxxx": 100000, "0xxxx0": 10000,
    "0xxx0": 1000,   "0xx0": 100,
    "xxxx1": 500,    "1xxxx": 500,
    "0xxx1": 50,     "1xxx0": 50,
    #bot phòng thủ
    "1111x" : 30005, # ƯU TIÊN chặn nếu người chơi sắp thắng
    "x1111" : 30005,
    "0111x" : 2005,
    "x1110" : 2005,
    "x0111" : 1005,
}


class HeuristicBot:
    def __init__(self):
        pass

    def get_move(self, board, player):
        opponent = 'X' if player == 'O' else 'O'
        best_score = 0
        best_move = None

        candidates = self.get_candidate_moves(board, distance=2)

        for x, y in candidates:
            score = self.evaluate_move(board, x, y, player, opponent)
            if score > best_score:
                best_score = score
                best_move = (x, y)

        if best_move is None:
            return BOARD_SIZE // 2, BOARD_SIZE // 2
        return best_move

    def get_candidate_moves(self, board, distance=5):
        candidates = set()
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if board[x][y] != EMPTY:
                    for dx in range(-distance, distance + 1):
                        for dy in range(-distance, distance + 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                                if board[nx][ny] == EMPTY:
                                    candidates.add((nx, ny))
        return list(candidates)

    def evaluate_move(self, board, x, y, player, opponent):
        board[x][y] = player  
        score = 0

        for dx, dy in DIRECTIONS:
            line = self.extract_line(board, x, y, dx, dy, player, opponent)
            score += self.evaluate_patterns(line)
            
        score += self.double_shot_score(board, x, y, player, opponent)
        score += self.block_opponent(board, x, y, player, opponent)
        score += self.threat_blocking(board, x, y, player, opponent)


        board[x][y] = EMPTY  
        return score
    
    def double_shot_score(self, board, x, y, player, opponent):
        count = 0
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, 1),
                    (1, 1), (1, 0), (1, -1), (0, -1)]

        for dx, dy in directions:
            o_count = 0
            blocked = False

            for step in range(1, 5):
                nx, ny = x + step * dx, y + step * dy
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    cell = board[nx][ny]
                    if cell == opponent:
                        blocked = True
                        break
                    elif cell == player:
                        o_count += 1
                else:
                    blocked = True
                    break

            if not blocked and o_count == 3:
                count += 1
                if count >= 2:
                    return 10000
        return 0
    
    def block_opponent(self,board, x, y, player, opponent):
        BOARD_SIZE = len(board)
        DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]
        EMPTY = ' '

        score = 0
        board[x][y] = player
        for dx, dy in DIRECTIONS:
            count_opponent = 1 
            open_ends = 0       

            for dir_mul in [1, -1]:
                step = 1
                while True:
                    nx = x + dir_mul * step * dx
                    ny = y + dir_mul * step * dy
                    if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                        if board[nx][ny] == opponent:
                            count_opponent += 1
                            step += 1
                        elif board[nx][ny] == EMPTY:
                            open_ends += 1
                            break
                        else:
                            break
                    else:
                        break
            if count_opponent == 3 and open_ends > 0:
                score += 5000
             # Nếu chuỗi đối thủ có 4 quân và ít nhất 1 đầu mở → rất nguy hiểm, ưu tiên chặn rất lớn
            if count_opponent == 4 and open_ends > 0:
                score += 10005
                
        board[x][y] = EMPTY
        return score
    
    def threat_blocking(self,board, x, y, player, opponent):
        BOARD_SIZE = len(board)
        DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]
        EMPTY = ' '

        # Giả sử đặt quân mình ở vị trí (x, y)
        board[x][y] = player

        threat_count = 0  # Đếm số threat bị chặn

        # Hàm phụ để đếm chuỗi đối thủ có thể tạo tại vị trí
        def count_potential_threats(nx, ny):
            total_threats = 0
            for dx, dy in DIRECTIONS:
                count_opponent = 0
                open_ends = 0

                # Duyệt theo 2 chiều trong hướng (dx, dy)
                for dir_mul in [1, -1]:
                    step = 1
                    while True:
                        tx = nx + dir_mul * step * dx
                        ty = ny + dir_mul * step * dy
                        if 0 <= tx < BOARD_SIZE and 0 <= ty < BOARD_SIZE:
                            cell = board[tx][ty]
                            if cell == opponent:
                                count_opponent += 1
                                step += 1
                            elif cell == EMPTY:
                                open_ends += 1
                                break
                            else:
                                break
                        else:
                            break

                if (count_opponent == 3 or count_opponent == 4) and open_ends > 0:
                    total_threats += 1
            return total_threats

        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, 1),
                    (1, 1), (1, 0), (1, -1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == EMPTY:
                threats = count_potential_threats(nx, ny)
                if threats >= 2:  # Có ít nhất 2 threat ở vị trí đó => double threat
                    threat_count += 1

        board[x][y] = EMPTY
        if threat_count > 0:
            return 20000 * threat_count

        return 0




    def extract_line(self, board, x, y, dx, dy, player, opponent):
        
        line = ""
        for step in range(-4, 5):
            nx, ny = x + step * dx, y + step * dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                cell = board[nx][ny]
                if cell == player:
                    line += 'x'
                elif cell == EMPTY:
                    line += '0'
                else:
                    line += '1'
            else:
                line += '1'  
        return line

    def evaluate_patterns(self, line):
        score = 0
        for pattern, value in PATTERN_SCORES.items():
            score += line.count(pattern) * value
        return score
