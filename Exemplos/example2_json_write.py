#!/usr/bin/env python

import json

def main():

    a = {}
    a["parameter1"] = 3.14
    a["parameter2"] = 10

    with open("myfile.json", "w") as fOUT:
        #json.dump(a, fOUT, indent=2)
        json.dump(a,fOUT)

if __name__=="__main__":
    main()
