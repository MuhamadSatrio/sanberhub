import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from sanber import app

if __name__ == '__main__':
	app.run(port=20000)

