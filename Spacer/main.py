# import other files
import player
import player_input as pinput

# import modules


# load stuff
def temp_start():
    name = input("Who are you, Captain? ")
    print(f"Welcome, {name}!")
    return name

# global values


# main loop
def main():
    name = temp_start() # replace later
    me = player.Player(name)
    running = True
    
    while running:
        check = pinput.handle_input(me)
        if check == "negative":
            running = False


# yeah if ykyk
if __name__ == "__main__":
    main()