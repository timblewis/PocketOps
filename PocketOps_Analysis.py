epsilon = 0.000001
scores = [0.0]*39366 #2*3^9
board = 9*[1]
board[8]=0
ties_allowed = False
done = False


def board_to_value(board, turn):
    val = 0
    for i in range(0, 9):
        val = 3*val + (board[8-i]*(3*board[8-i] - 1))//2
    return 2*val + turn


def value_to_board(value):
    board = 9*[1]
    turn = value % 2
    value = value >> 1
    for i in range(0,9):
        x = value%3
        board[i] = x*(5-3*x)//2
        value = value // 3
    return (board, turn)


#by decreasing Hamming weight
def increment_board():
    complete = False
    i = 0
    while not complete:
        if board[i]==0:
            i+=1
        elif board[i]==1:
            board[i]=-1
            complete=True
        else:
            complete=True
            board[i]=0
            num_extra_bits = 0
            i+=1
            while i < 9 and board[i]==-1:
                board[i]=0
                num_extra_bits+=1
                i+=1
            if i < 9:
                if board[i]==0:
                    board[i] = 1
                else:
                    board[i] = -1
                    num_extra_bits+=1
            for j in range(num_extra_bits):
                board[j]=1

lines = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
def check_board_state():
    if any(all(board[square]==1 for square in line) for line in lines):
        return 1
    if any(all(board[square]==-1 for square in line) for line in lines):
        return 0
    if sum(int(board[i]==0) for i in range(9)) <= 1:
        if ties_allowed:
            return 0.5
        else:
            return 0
    else:
        return 'i'

def evaluate_board():
    board_value = board_to_value(board, 0)
    open_squares = []
    p1_move_score = []
    p2_move_score = []
    for i in range(9):
        if(board[i]==0):
            open_squares.append(i)
            board[i]=1
            p1_move_score.append([i,scores[board_to_value(board,1)]])
            board[i]=-1
            p2_move_score.append([i,scores[board_to_value(board,0)]])
            board[i]=0
    p1_move_score.sort(key=lambda x: x[1], reverse=True)
    p2_move_score.sort(key=lambda x: x[1], reverse=False)

    p1_score=1
    p2_score=0
    delta_p2_score=1
    while delta_p2_score > epsilon:
        if p1_move_score[0][1] == p2_score:
            p1_score = p2_score
        else:
            den=1/(p1_move_score[0][1] - p2_score)
            num_sum=p1_move_score[0][1]/(p1_move_score[0][1]-p2_score)
            p1_score = (num_sum - 1)/den
            i=1
            while i < len(open_squares) and p1_move_score[i][1] > p1_score:
                den += 1/(p1_move_score[i][1] - p2_score)
                num_sum += p1_move_score[i][1]/(p1_move_score[i][1]-p2_score)
                p1_score = (num_sum - 1)/den
                i+=1

        old_p2_score = p2_score
        if p2_move_score[0][1] == p1_score:
            p2_score = p1_score
        else:
            den=1/(p2_move_score[0][1] - p1_score)
            num_sum=p2_move_score[0][1]/(p2_move_score[0][1]-p1_score)
            p2_score = (num_sum - 1)/den
            i=1
            while i < len(open_squares) and p2_move_score[i][1] < p2_score:
                den += 1/(p2_move_score[i][1] - p1_score)
                num_sum += p2_move_score[i][1]/(p2_move_score[i][1]-p1_score)
                p2_score = (num_sum - 1)/den
                i+=1
        delta_p2_score = abs(p2_score-old_p2_score)

    scores[board_value] = p1_score
    scores[board_value+1] = p2_score


def playing_opt_move_probs(board, turn):
    score_position = scores[board_to_value(board,turn)]
    score_if_blocked = scores[board_to_value(board,(turn+1)%2)]
    possible_move_scores = []
    move_probs = []
    for i in range(9):
        if board[i]==0:
            board[i] = turn*-2 + 1
            possible_move_scores.append([i,scores[board_to_value(board,(turn+1)%2)]])
            board[i] = 0
    possible_move_scores.sort(key=lambda x: x[1], reverse=(turn==0))
    if (turn*-2 + 1)*possible_move_scores[0][1] <= (turn*-2 + 1)*score_if_blocked*(1+10*epsilon):
        for move in possible_move_scores:
            move_probs.append([move[0],1.0/len(possible_move_scores)])
    else:
        support_size = 1
        den = 1/(possible_move_scores[0][1]-score_if_blocked)
        while support_size < len(possible_move_scores)\
            and (turn*-2 + 1)*possible_move_scores[support_size][1] > (turn*-2 + 1)*score_position:
            den += 1/(possible_move_scores[support_size][1]-score_if_blocked)
            support_size+=1
        for i in range(len(possible_move_scores)):
            if i < support_size:
                move_probs.append([possible_move_scores[i][0],1.0/((possible_move_scores[i][1] - score_if_blocked)*den)])
            else:
                move_probs.append([possible_move_scores[i][0],0])
    return move_probs


def blocking_opt_move_probs(board, turn):
    score_position = scores[board_to_value(board,turn)]
    score_if_blocked = scores[board_to_value(board,(turn+1)%2)]
    possible_move_scores = []
    move_probs = []
    for i in range(9):
        if board[i]==0:
            board[i] = turn*-2 + 1
            possible_move_scores.append([i,scores[board_to_value(board,(turn+1)%2)]])
            board[i] = 0
    possible_move_scores.sort(key=lambda x: x[1], reverse=(turn==0))
    if (turn*-2 + 1)*possible_move_scores[0][1] <= (turn*-2 + 1)*score_if_blocked*(1+10*epsilon):
        for move in possible_move_scores:
            move_probs.append([move[0],1.0/len(possible_move_scores)])
    else:
        support_size = 1
        den = 1/(possible_move_scores[0][1]-score_if_blocked)
        while support_size < len(possible_move_scores)\
            and (turn*-2 + 1)*possible_move_scores[support_size][1] > (turn*-2 + 1)*score_position:
            den += 1/(possible_move_scores[support_size][1]-score_if_blocked)
            support_size+=1
        for i in range(len(possible_move_scores)):
            if i < support_size:
                move_probs.append([possible_move_scores[i][0],(score_position - possible_move_scores[i][1])/(score_if_blocked - possible_move_scores[i][1])])
            else:
                move_probs.append([possible_move_scores[i][0],0])
    return move_probs


def print_board(board):
    characters = 9*[' ']
    for i in range(9):
        if board[i] == 1:
            characters[i] = 'X'
        elif board[i]==-1:
            characters[i] = 'O'
    print("    |   |   ")
    print("3 " + characters[0] + " | " + characters[1] + " | " + characters[2] + " ")
    print(" ---|---|---")
    print("2 " + characters[3] + " | " + characters[4] + " | " + characters[5] + " ")
    print(" ---|---|---")
    print("1 " + characters[6] + " | " + characters[7] + " | " + characters[8] + " ")
    print("    |   |   ")
    print("  a   b   c ")

def print_board_numbers(numbers):
    print(numbers[0] + "|" + numbers[1] + "|" + numbers[2])
    print("-----|-----|-----")
    print(numbers[3] + "|" + numbers[4] + "|" + numbers[5])
    print("-----|-----|-----")
    print(numbers[6] + "|" + numbers[7] + "|" + numbers[8])


def print_move_scores(board, turn):
    move_scores = 9*[0]
    for i in range(9):
        if board[i] == 1:
            move_scores[i] = "  X  "
        elif board[i] ==-1:
            move_scores[i] = "  O  "
        else:
            board[i] = -2*turn+1
            move_scores[i] = "{0:5.3f}".format(scores[board_to_value(board,1-turn)])
            board[i] = 0
    print_board_numbers(move_scores)


def print_move_percent(board, turn):
    move_percents = 9*[0]
    percent_list = playing_opt_move_probs(board, turn)
    for i in range(9):
        if board[i] == 1:
            move_percents[i] = "  X  "
        elif board[i] ==-1:
            move_percents[i] = "  O  "
    for move_percent in percent_list:
        move_percents[move_percent[0]] = "{0:5.3f}".format(move_percent[1])
    print_board_numbers(move_percents)


def print_block_percent(board, turn):
    block_percents = 9*[0]
    percent_list = blocking_opt_move_probs(board, turn)
    for i in range(9):
        if board[i] == 1:
            block_percents[i] = "  X  "
        elif board[i] ==-1:
            block_percents[i] = "  O  "
    for block_percent in percent_list:
        block_percents[block_percent[0]] = "{0:5.3f}".format(block_percent[1])
    print_board_numbers(block_percents)


def print_data(board, turn):
    print("Optimal probabilities for player " + str(turn+1) + " moves:")
    print_move_percent(board, turn)
    print()
    print("Optimal probabilities for player " + str(2-turn) + " blocks:")
    print_block_percent(board, turn)
    print()
    print("Score if player " + str(turn+1) + " successfully moves:")
    print_move_scores(board, turn)
    print()
    print_board(board)
    print()
    print("score            = " + str(scores[board_to_value(board, turn)]))
    print("score if blocked = " + str(scores[board_to_value(board, 1-turn)]))
    print("player " + str(1+turn) + " to play")


def parse_move(move_str):
    if len(move_str) != 2\
           or (move_str[0] != 'a' and move_str[0] != 'b' and move_str[0] != 'c')\
           or (move_str[1] != '1' and move_str[1] != '2' and move_str[1] != '3'):
        return 'e'
    else:
        row_value = 3*(3-int(move_str[1]))
        if move_str[0] == 'a':
            return row_value
        elif move_str[0] == 'b':
            return row_value + 1
        else:
            return row_value + 2


def move_to_str(move):
    if move % 3 == 0:
        col = "a"
    elif move % 3 == 1:
        col = "b"
    else:
        col = "c"
    return col + str(int(3-move//3))


while not done:
    #print(board)
    board_state = check_board_state()
    if board_state != 'i':
        board_value = board_to_value(board,0)
        scores[board_value] = board_state
        scores[board_value+1] = board_state
    else:
        evaluate_board()

    if(board == 9*[0]):
        done = True
    else:
        increment_board()

command = ""
turn = 0
move_list = []
board_updated = True
print_data(board, turn)
print("Enter \"H\" for help")
while(command!="Q"):
    board_updated = False
    command = input("> ")
    if command == "H":
        print("R: resets the board")
        print("U: undoes the last move")
        print("Xa1: places an X at a1")
        print("Oa1: places an O at a1")
        print("S: switches current player")
    elif command == "R":
        board = 9*[0]
        turn = 0
        move_list = []
        board_updated = True
    elif command == "S":
        turn = 1-turn
        board_updated = True
    elif len(command) == 3 and (command[0] == "X" or command[0] == "O"):
        if command[0] == "X":
            player = 1
        else:
            player = -1
        move = parse_move(command[1:])
        if move != "e":
            move_list.append([move,board[move]])
            board[move] = player
            board_updated = True
        else:
            print("Invalid move")
    elif command == "U" and len(move_list) > 0:
        move = move_list.pop()
        board[move[0]] = move[1]
        board_updated = True
    else:
        print("Invalid command")
    if board_updated:
        print_data(board, turn)
