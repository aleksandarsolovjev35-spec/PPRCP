#!/usr/bin/env python3
import sys
import os

# Add portal directory to path and execute main
portal_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portal')
sys.path.insert(0, portal_dir)

from server import main

if __name__ == '__main__':
    main()
