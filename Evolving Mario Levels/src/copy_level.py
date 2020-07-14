import shutil
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "levels/last.txt"
    if not os.path.exists(path):
        print("The file at " + path + " does not exist.")
        exit(1)
    shutil.copy(path, "Player/Assets/Resources/Levels/Level1.txt")
    print("Finished!")
