
import os


tfile = open("templatelist.txt", "r")

lista = tfile.readlines()

tfile.close()

for line in lista:
    
    line = line.replace("\n","")
    
    filename = line.lower() + ".xml"
    
    outputfile = open(filename, "w")
    
    outputfile.write("<Template>\n")
    outputfile.write("<Name>"+line+"</Name>\n")
    outputfile.write("<UseTheme>"+line+"</UseTheme>\n")
    outputfile.write("<CustomCode></CustomCode>\n")
    outputfile.write("</Template>\n")

    
    outputfile.close()
    