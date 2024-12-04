# Rock-Paper-Scissors game! 

import cv2 # type: ignore
import mediapipe  # type: ignore
import random

import time

# A Function that indicates the winning and losing situations in the game

def calculate_game_state(move):
    
    # A list the pc that choses the random move
     
    moves = ['Rock', 'Paper', 'Scissors']
    
    # A dict that has the winning situations
    
    wins = {'Rock': 'Scissors', 'Scissors': 'Paper', 'Paper': 'Rock'}
    
    selected = random.randint(0,2)
    print(f'Computer played : {moves[selected]}')
    
    if move == moves[selected]:
        return 0, moves[selected]
    
    elif wins[move] == moves[selected] :
        return 1, moves[selected]
    
    # in the case of losing
    
    return -1, moves[selected]

##############################################################################################        

# Configuring the fingers status in the X-Y axis to identify the input from the user
# according to the co-ordinates of the tip of the finger relative to its base

def get_finger_status(hands_module, hand_landmarks, finger_name):
    finger_id_map = {'INDEX': 8, 'MIDDLE': 12, 'RING': 16, 'PINKY': 20}

    finger_tip_y = hand_landmarks.landmark[finger_id_map[finger_name]].y
    finger_dip_y = hand_landmarks.landmark[finger_id_map[finger_name] - 1].y
    finger_mcp_y = hand_landmarks.landmark[finger_id_map[finger_name] - 2].y

    return finger_tip_y < finger_mcp_y

# A function for the thumb specifically as its different from other fingers as it can be closed in different ways

def get_thumb_status(hands_module, hand_landmarks):
    thumb_tip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP].x
    thumb_mcp_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 2].x
    thumb_ip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 1].x

    return thumb_tip_x > thumb_ip_x > thumb_mcp_x


#############################################################################################

# Main function section

def start_video():
    capture = cv2.VideoCapture(0)
    
    # Getting from mediapipe the solutions needed for the hand detection
    
    drawingModule = mediapipe.solutions.drawing_utils
    hand_module = mediapipe.solutions.hands
    
    # Variables for the game 
    
    start_time = 0.0
    timer_started = False
    
    time_left_now = 3
    hold_for_play = False
    draw_timer = 0.0
    
    game_over_text = ""
    computer_played = ""
    Player_score = 0
    PC_score = 0
    
    
    
    with hand_module.Hands(static_image_mode = False,
                           min_detection_confidence = 0.7,
                           min_tracking_confidence = 0.4,
                           max_num_hands = 2) as hands:
        while True:
            
            # for a real time game counting from 3 to 0 before you can give ur gesture
            
            if timer_started:
                now_time = time.time()
                time_elapsed = now_time - start_time
                if time_elapsed >= 1:
                    time_left_now -= 1
                    start_time = now_time
                    if time_left_now <= 0:
                        hold_for_play = True
                        timer_started = False
            
            # The capture function returns back 2 values
            # the readed -detected- value, and its corresponding frame as time passes
            
            ret,  frame = capture.read()
            
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            move = 'UNKNOWN'
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if hold_for_play or time.time() - draw_timer <= 2:
                        
                        # Function for the setup of lines and circles on the hand
                        # For visualizing the detected input by the PC
                        
                        drawingModule.draw_landmarks(frame, hand_landmarks, hand_module.HAND_CONNECTIONS)

                    # Now we identify if the finger is open, return back 1
                    # If closed, return back 0
                    # So for Paper all fingers gives 1 --> 11111
                    # For Rock --> 00000
                    # And finally for Scissors --> 01100 (the 1's are for the index and the middle fingers)

                    current_state = ''
                    thumb_status = get_thumb_status(hand_module, hand_landmarks)
                    current_state += '1' if thumb_status else '0'

                    index_status = get_finger_status(hand_module, hand_landmarks, 'INDEX')
                    current_state += '1' if index_status else '0'

                    middle_status = get_finger_status(hand_module, hand_landmarks, 'MIDDLE')
                    current_state += '1' if middle_status else '0'

                    ring_status = get_finger_status(hand_module, hand_landmarks, 'RING')
                    current_state += '1' if ring_status else '0'

                    pinky_status = get_finger_status(hand_module, hand_landmarks, 'PINKY')
                    current_state += '1' if pinky_status else '0'

                    if current_state == '00000':
                        move = 'Rock'
                        
                    elif current_state == '11111':
                        move = 'Paper'
                        
                    elif current_state == '01100':
                        move = 'Scissors'
                        
                    else:
                        move = 'UNKNOWN'
                        
                if hold_for_play and move != 'UNKNOWN':
                    hold_for_play = False
                    draw_timer = time.time()
                    print(f'Player played {move}')
                    
                    # Unpack this function to know whether the player won or not and the PC move
                    
                    won, PC_move = calculate_game_state(move)
                    computer_played = f'Player : {move} | PC : {PC_move}'
                    if won == 1:
                        game_over_text = 'WON!!'
                        Player_score += 1
                    elif won == -1:
                        game_over_text = 'LOST!!'
                        PC_score += 1
                    else:
                        game_over_text = 'DRAW!!'

            # String variables for visualization of the score between the player and the PC
            
            Player_text = f'Player : {Player_score}'
            PC_text = f'PC : {PC_score}'
            
            # Next section is for the text alignment on the screen for more interactive display to the user
            
            font = cv2.FONT_HERSHEY_COMPLEX
            
            if not hold_for_play and not timer_started:
                cv2.putText(frame,
                            game_over_text + " " + computer_played,
                            (10, 450),
                            font,0.75,
                            (255, 255, 255),
                            2,
                            cv2.LINE_4)

            label_text = 'PRESS SPACE TO START!'
            if hold_for_play:
                label_text = 'PLAY NOW!'
            elif timer_started:
                label_text = 'PLAY STARTS IN ' + str(time_left_now)

            cv2.putText(frame,
                        label_text,
                        (150, 50),
                        font, 1,
                        (0, 0, 255),
                        2,
                        cv2.LINE_4)
            
            cv2.putText(frame,
                        Player_text,
                        (50, 90),
                        font, 1,
                        (0, 0, 255),
                        2,
                        cv2.LINE_4)
            
            cv2.putText(frame,
                        PC_text,
                        (50, 125),
                        font, 1,
                        (0, 0, 255),
                        2,
                        cv2.LINE_4)
            
            cv2.imshow('Rock-Paper-Scissors',frame)
            
            if cv2.waitKey(1) == 32:
                print("pressed space")
                start_time = time.time()
                timer_started = True
                time_left_now = 3
                
            if cv2.waitKey(1) == 27:
                break
            
        cv2.destroyAllWindows()
        capture.release()

# For the execution of the whole application

if __name__ == '__main__':
    start_video()