import os
import random
def PicPicker(path, file_used):
	list = os.listdir(path)
	rand_int = random.randint(0,len(list)-1)
	if list[rand_int] == file_used:
		PicPicker(path, file_used)
	else:
		return list[rand_int]
	
if __name__ == '__main__':
    PicPicker(path)